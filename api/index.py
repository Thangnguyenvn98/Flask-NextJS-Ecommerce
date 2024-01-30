from importlib.metadata import version
from flask import Flask,jsonify,request,Response
from flask_restx import Api,Resource
from config import DevConfig
from flask_cors import CORS,cross_origin
from model import Store, User, Billboard, Category, Size
from database import db
from flask_migrate import Migrate
from functools import wraps
from six.moves.urllib.request import urlopen
from jose import jwt
from serialize import configure_serializers
from sqlalchemy.orm import joinedload


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
store_model, user_model, billboard_model,category_model,size_model = configure_serializers(api)


# /server.py
# --------------------------- STORE API SPECIFIC-------------------------------------
@api.route('/api/store')
class StoresResource(Resource):
    @api.marshal_list_with(store_model)
    def get(self):
        stores = Store.query.all()
        return stores
    
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
    
   
@api.route('/api/store/<string:store_id>')
class SpecificStoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,store_id):
        store = Store.query.filter_by(id = store_id).first_or_404() 
        return store
#-------------------------------User and Store API-----------------------------------

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


@api.route('/api/store/<string:store_id>/<string:user_id>')
class UserSpecificStoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,store_id,user_id):
        store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
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
    
@api.route('/api/user/<string:user_id>/stores')
class UserAllStoresResource(Resource):

    @api.marshal_list_with(store_model)
    def get(self,user_id):
        stores = Store.query.filter_by(user_id=user_id).all()
        if stores:
            return stores
        else:
            return {'message': 'No stores found for this user'}, 204
        

@api.route('/api/user/<string:user_id>/store')
class UserAnyFirstStoreResource(Resource):

    @api.marshal_with(store_model)
    def get(self,user_id):
        store = Store.query.filter_by(user_id=user_id).first()
        if store is not None:
            return store
        else:
            return {'error': 'Store not found for user {}'.format(user_id)}, 404
        
#----------------------------STORE AND BILLBOARD API ROUTES-------------------------------------


#GETTING A SINGLE BILLBOARD FROM BILLBOARD ID   
@api.route('/api/billboard/<string:billboard_id>')
class SingleBillboardResource(Resource):

    @api.marshal_with(billboard_model)
    def get(self,billboard_id):
        billboard = Billboard.query.filter_by(id = billboard_id).first_or_404() 
        return billboard


#GETTING ALL BILLBOARDS WITH STORE ID 
@api.route('/api/<string:store_id>/billboards')
class UserStoreBillboardsResource(Resource):
    @api.marshal_list_with(billboard_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        billboards = Billboard.query.filter_by(store_id=store_id).order_by(Billboard.created_at.desc()).all()
        if billboards:
            return billboards
        else:
            return [],200
        
#CREATE A BILLBOARDS WITH STORE ID 
            
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
    
    
#GETTING BILLBOARD BASED ON TH STORE ID AND BILLBOARD ID
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
    
# DELETE A BILLBOARD BASED ON MATCHING USER ID AND STORE ID AND BILLBOARD ID
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
        billboard_copy = billboard_to_delete.__dict__.copy()
        billboard_to_delete.delete()
        return billboard_copy    
        
#---------------------------------BILLBOARD AND CATEGORIES--------------------------------------------- 



#GETTING SPECIFIC CATEGORY FROM CATEGORY ID
@api.route('/api/category/<string:category_id>')
class CategoryResource(Resource):

    @api.marshal_with(category_model)
    def get(self,category_id):
        category = Category.query.filter_by(id = category_id).first_or_404() 
        return category 


#GETTING ALL THE CATEGORIES GIVEN THE STORE ID
@api.route('/api/<string:store_id>/categories')
class UserStoreBillboardsCategoryResource(Resource):
    @api.marshal_list_with(category_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        categories = Category.query.options(joinedload(Category.billboard)).filter_by(store_id=store_id).order_by(Category.created_at.desc()).all()
        if categories:
            return categories
        else:
            return [],200

#CREATE NEW CATEGORIES WITH THE GIVEN STORE ID IN PARAMS, BILLBOARD ID IN REQUEST    
    @api.marshal_with(category_model)
    def post(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'Unauthenticated'},400
        if 'name' not in data:
            return {'error': 'Missing required field "name"'}, 400
        if 'billboardId' not in data:
            return {'error': 'Billboard ID is required'}, 400
        existing_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        new_category = Category(name=data.get('name'),store_id=store_id,billboard_id=data.get('billboardId'))
        new_category.save()
        return new_category, 201

@api.route('/api/<string:store_id>/categories/<string:category_id>')
class StoreSpecificCategoryUpdateResource(Resource):

    @api.marshal_with(category_model)
    def get(self,store_id,category_id):
        if not category_id:
            return {'message': 'category ID is required'}, 400
        category = Category.query.filter_by(id=category_id,store_id=store_id).first_or_404()
        return category 
      
    @api.marshal_with(category_model)
    def patch(self,store_id,category_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not category_id:
            return {'message': 'category ID is required'}, 400
        data = request.get_json()
        print(data,file=sys.stderr)
        if 'user_id' not in data:
            return {'message': 'User unauthenticated'}, 401
        if 'name' not in data:
            return {'message': 'Name is required'}, 400
        if 'billboardId' not in data:
            return {'message': 'Billboard ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        category_to_update = Category.query.filter_by(id=category_id,store_id=store_id).first_or_404()
        category_to_update.update(data.get('name'),data.get('billboardId'))
        return category_to_update
    
# DELETE A category BASED ON MATCHING USER ID AND STORE ID AND category ID
@api.route('/api/<string:user_id>/<string:store_id>/category/<string:category_id>')
class UserSpecificCategoryResource(Resource):
    @api.marshal_with(category_model)
    def delete (self,user_id,store_id,category_id):
        if not user_id:
            return {'message': 'Unauthenticated'}, 400
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not category_id:
            return {'message': 'category ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        category_to_delete = Category.query.filter_by(id=category_id,store_id=store_id).first_or_404()
        category_to_copy = category_to_delete.__dict__.copy()
        category_to_delete.delete()
        return category_to_copy   

#-----------------------------CATEGORY AND SIZE API----------------------------------- 
#GETTING SPECIFIC CATEGORY FROM CATEGORY ID
@api.route('/api/size/<string:size_id>')
class SinglesizeResource(Resource):

    @api.marshal_with(size_model)
    def get(self,size_id):
        size = Size.query.filter_by(id = size_id).first_or_404() 
        return size


#GETTING ALL sizeS WITH STORE ID 
@api.route('/api/<string:store_id>/sizes')
class UserStoresizesResource(Resource):
    @api.marshal_list_with(size_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        sizes = Size.query.filter_by(store_id=store_id).order_by(Size.created_at.desc()).all()
        if sizes:
            return sizes
        else:
            return [],200
        
#CREATE A sizeS WITH STORE ID 
            
    @api.marshal_with(size_model)
    def post(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'Unauthenticated'},400
        if 'name' not in data:
            return {'error': 'Missing required field "Name"'}, 400
        if 'value' not in data:
            return {'error': 'Value is required'}, 400
        existing_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        new_size = Size(name=data.get('name'),store_id=store_id,value=data.get('value'))
        new_size.save()
        return new_size, 201
    
    
#GETTING size BASED ON TH STORE ID AND size ID
@api.route('/api/<string:store_id>/sizes/<string:size_id>')
class StoreSpecificsizeUpdateResource(Resource):

    @api.marshal_with(size_model)
    def get(self,store_id,size_id):
        if not size_id:
            return {'message': 'size ID is required'}, 400
        size = Size.query.filter_by(id=size_id,store_id=store_id).first_or_404()
        return size 
      
    @api.marshal_with(size_model)
    def patch(self,store_id,size_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not size_id:
            return {'message': 'size ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'User unauthenticated'}, 401
        if 'name' not in data:
            return {'message': 'Name is required'}, 400
        if 'value' not in data:
            return {'message': 'Value is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        size_to_update = Size.query.filter_by(id=size_id,store_id=store_id).first_or_404()
        size_to_update.update(data.get('name'),data.get('value'))
        return size_to_update
    
# DELETE A size BASED ON MATCHING USER ID AND STORE ID AND size ID
@api.route('/api/<string:user_id>/<string:store_id>/size/<string:size_id>')
class UserSpecificsizeResource(Resource):
    @api.marshal_with(size_model)
    def delete (self,user_id,store_id,size_id):
        if not user_id:
            return {'message': 'Unauthenticated'}, 400
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not size_id:
            return {'message': 'size ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        size_to_delete = Size.query.filter_by(id=size_id,store_id=store_id).first_or_404()
        size_copy = size_to_delete.__dict__.copy()
        size_to_delete.delete()
        return size_copy    

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=8080)