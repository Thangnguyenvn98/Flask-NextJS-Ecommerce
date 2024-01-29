from importlib.metadata import version
from flask import Flask,jsonify,request,Response
from flask_restx import Api,Resource
from config import DevConfig
from flask_cors import CORS,cross_origin
from model import Store, User, Billboard
from database import db
from flask_migrate import Migrate
from functools import wraps
from six.moves.urllib.request import urlopen
from jose import jwt
from serialize import configure_serializers

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
store_model, user_model, billboard_model = configure_serializers(api)


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




@api.route('/api/store')
class StoresResource(Resource):
    
    @api.marshal_with(store_model)
    def post(self):
        try:
            data = request.get_json()
            if 'name' not in data:
                return {'error': 'Missing required field "name"'}, 400
           
            # Create a new user and store
            new_store = Store(name=data.get('name'),user_id=data.get('userId'))
            new_store.save()

            # Commit the changes to the database
            return new_store, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error in post method: {str(e)}")  # Print the error for debugging
            return {'error': 'Internal server error'}, 500
    
    # @cross_origin(headers=["Content-Type", "Authorization"])
    # @requires_auth
    @api.marshal_list_with(store_model)
    def get(self):
        stores = Store.query.all()
        return stores
    
@api.route('/api/store/<string:store_id>')
class StoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,store_id):
        store = Store.query.filter_by(id = store_id).first_or_404() 
        return store
    
@api.route('/api/billboard/<string:billboard_id>')
class BillboardResource(Resource):

    @api.marshal_with(billboard_model)
    def get(self,billboard_id):
        billboard = Billboard.query.filter_by(id = billboard_id).first_or_404() 
        return billboard
    
@api.route('/api/<string:store_id>/billboards')
class UserStoreBillboardsResource(Resource):
    @api.marshal_with(billboard_model)
    def post(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'Unauthenticated'},400
        if 'label' not in data:
            return {'error': 'Missing required field "label"'}, 400
        if 'imageUrl' not in data:
            return {'error': 'Image URL is required'}, 400
        existing_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        new_billboard = Billboard(label=data.get('label'),store_id=store_id,imageUrl=data.get('imageUrl'))
        new_billboard.save()
        return new_billboard, 201
    
    @api.marshal_list_with(billboard_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        billboards = Billboard.query.filter_by(store_id=store_id).order_by(Billboard.created_at.desc()).all()
        if billboards:
            return billboards
        else:
            return [],200



@api.route('/api/<string:store_id>/billboards/<string:billboard_id>')
class StoreSpecificBillboardUpdateResource(Resource):

    @api.marshal_with(billboard_model)
    def get(self,store_id,billboard_id):
        if not billboard_id:
            return {'message': 'Billboard ID is required'}, 400
        billboard = Billboard.query.filter_by(id=billboard_id,store_id=store_id).first_or_404()
        return billboard 
      
    @api.marshal_with(billboard_model)
    def patch(self,store_id,billboard_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not billboard_id:
            return {'message': 'Billboard ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'User unauthenticated'}, 401
        if 'label' not in data:
            return {'message': 'Label is required'}, 400
        if 'imageUrl' not in data:
            return {'message': 'ImageURL is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        billboard_to_update = Billboard.query.filter_by(id=billboard_id,store_id=store_id).first_or_404()
        billboard_to_update.update(data.get('label'),data.get('imageUrl'))
        return billboard_to_update
    
   
    
@api.route('/api/<string:user_id>/<string:store_id>/billboard/<string:billboard_id>')
class UserSpecificBillboardResource(Resource):
    @api.marshal_with(billboard_model)
    def delete (self,user_id,store_id,billboard_id):
        if not user_id:
            return {'message': 'Unauthenticated'}, 400
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not billboard_id:
            return {'message': 'Billboard ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        billboard_to_delete = Billboard.query.filter_by(id=billboard_id,store_id=store_id).first_or_404()
        billboard_to_delete.delete()
        return billboard_to_delete    
        
    
@api.route('/api/store/<string:store_id>/<string:user_id>')
class UserSpecificStoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,store_id,user_id):
        store = Store.query.filter_by(id=store_id).first_or_404()
        print(store_id,file=sys.stderr)
        print(user_id,file=sys.stderr)
        return store
    
    @api.marshal_with(store_model)
    def patch(self,store_id,user_id):
        if not user_id:
            return {'message': 'User unauthenticated'}, 401
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'name' not in data:
            return {'message': 'Name is required'}, 400
        store_to_update = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        store_to_update.update(data.get('name'))
        return store_to_update
    
    @api.marshal_with(store_model)
    def delete (self,store_id,user_id):
        if not user_id:
            return {'message': 'User unauthenticated'}, 401
        if not store_id:
            return {'message': 'Store ID is required'}, 400
       
        store_to_delete = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        store_to_delete.delete()
        return store_to_delete



@api.route('/api/user')
class UserResource(Resource):
    @api.marshal_with(user_model)
    def post(self):
        user = request.get_json()
        user_id = user.get('sub')
        # Check if user already exists
        existing_user = User.query.get(user_id)
        if existing_user is None:
            user_name = user.get('name')
            user_picture = user.get('picture')
            # User does not exist, so create a new one
            new_user = User(id=user_id, name=user_name, picture=user_picture)
            new_user.save()
            return {'message': 'User added'}, 200
        else:
            # User already exists, so do nothing
            return {'message': 'User already exists'}, 200
    
@api.route('/api/user/<string:user_id>/stores')
class UserStoresResource(Resource):

    @api.marshal_list_with(store_model)
    def get(self,user_id):
        stores = Store.query.filter_by(user_id=user_id).all()
        if stores:
            return stores
        else:
            return {'message': 'No stores found for this user'}, 204
        
@api.route('/api/user/<string:user_id>/store')
class UserStoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,user_id):
        store = Store.query.filter_by(user_id=user_id).first()
        if store is not None:
            print(store,file=sys.stderr)
            print("Testing 2",file=sys.stderr)
            return store
        else:
            return {'error': 'Store not found for user {}'.format(user_id)}, 404


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8080)