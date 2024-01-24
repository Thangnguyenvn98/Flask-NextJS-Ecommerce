from flask import Flask,jsonify,request, redirect, session
from flask_restx import Api,Resource,fields
from config import DevConfig
from flask_cors import CORS
from model import Items
from database import db
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from functools import wraps



app=Flask(__name__)
app.config.from_object(DevConfig)
CORS(app)

db.init_app(app)
migrate=Migrate(app,db)
api=Api(app,doc='/api/docs')
oauth=OAuth(app)

auth0 = oauth.register(
       'auth0',
       client_id=app.config['AUTH0_CLIENT_ID'],
       client_secret=app.config['AUTH0_CLIENT_SECRET'],
       client_kwargs= {
           'scope': 'openid profile email'
       },
       server_metadata_url=f'https://{app.config["AUTH0_DOMAIN"]}/.well-known/openid-configuration'

   )

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def get_token_auth_header():
       auth_header = request.headers.get('Authorization', None)
       if not auth_header:
           raise AuthError({
               'code': 'authorization_header_missing',
               'description': 'Authorization header is expected.'
           }, 401)
       parts = auth_header.split()
       if parts[0].lower() != 'bearer':
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Authorization header must start with "Bearer".'
           }, 401)
       elif len(parts) == 1:
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Token not found.'
           }, 401)
       elif len(parts) > 2:
           raise AuthError({
               'code': 'invalid_header',
               'description': 'Authorization header must be bearer token.'
           }, 401)
       return parts[1]

def require_scope(scope):
       def decorator(f):
           @wraps(f)
           def decorated(*args, **kwargs):
               token = get_token_auth_header()
               try:
                   payload = auth0.parse_id_token(token)
                   if scope in payload.get('scope', '').split():
                       return f(*args, **kwargs)
                   else:
                       raise AuthError({
                           'code': 'insufficient_scope',
                           'description': 'Permission denied.'
                       }, 403)
               except Exception as e:
                   raise AuthError({
                       'code': 'invalid_token',
                       'description': 'Token is invalid.'
                   }, 401)
           return decorated
       return decorator



items_model=api.model(
    "Items",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "price":fields.Float()
    }
)
@api.route('/api/login')
class AuthLogin(Resource):
    def get(self):
        return auth0.authorize_redirect(redirect_uri='http://localhost:8080/api/callback')

@api.route('/api/callback')
class AuthCallback(Resource):
    def get(self):
        token =auth0.authorize_access_token()
        session["user"] = token
           # Perform any additional user validation or database operations here
        return redirect('http://localhost:3000')

@api.route('/api/items')
class ItemsResource(Resource):

    @api.marshal_list_with(items_model)
    def get(self):
        items=Items.query.all()
        return items
    
    @api.marshal_with(items_model)
    def post(self):
        data=request.get_json()
        new_items=Items(
            title=data.get('title'),
            price=data.get('price')
        )
        new_items.save()
        return new_items,201

@api.route('/api/admin')
class AdminResource(Resource):
    def get(self):
        return jsonify(msg="Hello admin!")

if __name__ == '__main__':
    app.run(debug=True,port=8080)