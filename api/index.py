from flask import Flask,jsonify,request, redirect, session
from flask_restx import Api,Resource,fields
from config import DevConfig
from flask_cors import CORS
from model import Store, User
from database import db
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from auth0.authentication import GetToken
from auth0.management import Auth0
from functools import wraps
import sys



app=Flask(__name__)
app.config.from_object(DevConfig)
CORS(app)

db.init_app(app)
migrate=Migrate(app,db)
api=Api(app,doc='/api/docs')
# oauth=OAuth(app)

# auth0 = oauth.register(
#        'auth0',
#        client_id=app.config['AUTH0_CLIENT_ID'],
#        client_secret=app.config['AUTH0_CLIENT_SECRET'],
#        client_kwargs= {
#            'scope': 'openid profile email'
#        },
#        server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'

#    )

# class AuthError(Exception):
#     def __init__(self, error, status_code):
#         self.error = error
#         self.status_code = status_code

# def get_token_auth_header():
#        auth_header = request.headers.get('Authorization', None)
#        if not auth_header:
#            raise AuthError({
#                'code': 'authorization_header_missing',
#                'description': 'Authorization header is expected.'
#            }, 401)
#        parts = auth_header.split()
#        if parts[0].lower() != 'bearer':
#            raise AuthError({
#                'code': 'invalid_header',
#                'description': 'Authorization header must start with "Bearer".'
#            }, 401)
#        elif len(parts) == 1:
#            raise AuthError({
#                'code': 'invalid_header',
#                'description': 'Token not found.'
#            }, 401)
#        elif len(parts) > 2:
#            raise AuthError({
#                'code': 'invalid_header',
#                'description': 'Authorization header must be bearer token.'
#            }, 401)
#        return parts[1]

# def require_scope(scope):
#        def decorator(f):
#            @wraps(f)
#            def decorated(*args, **kwargs):
#                token = get_token_auth_header()
#                try:
#                    payload = auth0.parse_id_token(token)
#                    if scope in payload.get('scope', '').split():
#                        return f(*args, **kwargs)
#                    else:
#                        raise AuthError({
#                            'code': 'insufficient_scope',
#                            'description': 'Permission denied.'
#                        }, 403)
#                except Exception as e:
#                    raise AuthError({
#                        'code': 'invalid_token',
#                        'description': 'Token is invalid.'
#                    }, 401)
#            return decorated
#        return decorator




store_model = api.model(
    "Store",
    {
        "id": fields.Integer(),
        "name": fields.String(),
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

            new_store = Store(name=data.get('name'))
            db.session.add(new_store)
            new_store.save()

            # Commit the changes to the database
            print(new_store,file=sys.stderr)
            return new_store, 201
        except Exception as e:
            db.session.rollback()
            print(f"Error in post method: {str(e)}")  # Print the error for debugging
            return {'error': 'Internal server error'}, 500
        
    @api.marshal_list_with(store_model)
    def get(self):
        stores = Store.query.all()
        return stores
        


# @api.route('/api/user')
# class UserResource(Resource):
#     @require_scope('openid')
#     def get(self):
#         token = auth0.authorize_access_token()
#         payload = auth0.parse_id_token(token)
#         user_id = payload['sub']
#         index = user_id.find("|")
#         if index:
#             user_id = user_id[index+1:]
#         user = User.query.get(user_id)
#         if user:
#             return jsonify(user_id=user.id), 200
#         else:
#             return {'error':'User not found'}, 404
    
@api.route('/api/admin')
class AdminResource(Resource):
    def get(self):
        return jsonify(msg="Hello admin!")

if __name__ == '__main__':
    app.run(debug=True,port=8080)