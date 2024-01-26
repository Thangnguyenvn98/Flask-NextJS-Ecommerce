from importlib.metadata import version
from flask import Flask,jsonify,request
from flask_restx import Api,Resource,fields
from config import DevConfig
from flask_cors import CORS,cross_origin
from model import Store, User
from database import db
from flask_migrate import Migrate
from functools import wraps
from six.moves.urllib.request import urlopen
from jose import jwt
import json

import sys

flask_major_version = int(version("flask")[0])
if flask_major_version >= 2:
    from flask import g

    ctx = g
else:
    from flask import _app_ctx_stack

    ctx = _app_ctx_stack.top

ALGORITHMS = ["RS256"]

app=Flask(__name__)
app.config.from_object(DevConfig)
CORS(app)

db.init_app(app)
migrate=Migrate(app,db)
api=Api(app,doc='/api/docs')

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

# /server.py

# Format error response and append status code
def get_token_auth_header():
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def requires_auth(f):
    """Determines if the Access Token is valid
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_auth_header()
        jsonurl = urlopen(f"https://{app.config['AUTH0_DOMAIN']}/.well-known/jwks.json")
        jwks = json.loads(jsonurl.read())
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=ALGORITHMS,
                    audience=app.config['AUTH0_AUDIENCE'],
                    issuer=f"https://{app.config['AUTH0_DOMAIN']}/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError({"code": "token_expired",
                                "description": "token is expired"}, 401)
            except jwt.JWTClaimsError:
                raise AuthError({"code": "invalid_claims",
                                "description":
                                    "incorrect claims,"
                                    "please check the audience and issuer"}, 401)
            except Exception:
                raise AuthError({"code": "invalid_header",
                                "description":
                                    "Unable to parse authentication"
                                    " token."}, 401)

            ctx.current_user = payload
            return f(*args, **kwargs)
        raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
    return decorated

# /server.py

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False


store_model = api.model(
    "Store",
    {
        "id": fields.Integer(),
        "name": fields.String(),
        "user_id": fields.String(),
        "created_at": fields.DateTime(),
        "updated_at": fields.DateTime(),
    }
)

user_model = api.model(
    "User",
    {
        "id":fields.String(),
        "name":fields.String(),
        "picture": fields.String(),
    }
)

@api.route('/api/stores')
class StoresResource(Resource):
    
    @api.marshal_with(store_model)
    def post(self):
        try:
            data = request.get_json()
            if 'name' not in data:
                return {'error': 'Missing required field "name"'}, 400

            # Create a new user and store
            print(data,file=sys.stderr)
            new_store = Store(name=data.get('name'),user_id=data.get('userId'))
            db.session.add(new_store)
            new_store.save()

            # Commit the changes to the database
            print(new_store,file=sys.stderr)
            return new_store, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error in post method: {str(e)}")  # Print the error for debugging
            return {'error': 'Internal server error'}, 500
    
    @cross_origin(headers=["Content-Type", "Authorization"])
    @requires_auth
    @api.marshal_list_with(store_model)
    def get(self):
        stores = Store.query.all()
        return stores
    
@api.route('/api/store/<string:user_id>')
class StoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,user_id):
        store = Store.query.filter_by(user_id=user_id).first()
        return store


@api.route('/api/user')
class UserResource(Resource):
    def get(self):
        return jsonify(msg="Testing")


    def post(self):
        user = request.get_json()
        user_id = user.get('sid')
        user_name = user.get('name')
        user_picture = user.get('picture')

        # Check if user already exists
        existing_user = User.query.get(user_id)
        if existing_user is None:
            # User does not exist, so create a new one
            new_user = User(id=user_id, name=user_name, picture=user_picture)
            new_user.save()
            return {'message': 'User added'}, 200
        else:
            # User already exists, so do nothing
            return {'message': 'User already exists'}, 200
    
@api.route('/api/admin')
class AdminResource(Resource):
    def get(self):
        return jsonify(msg="Hello admin!")

if __name__ == '__main__':
    app.run(debug=True,port=8080)