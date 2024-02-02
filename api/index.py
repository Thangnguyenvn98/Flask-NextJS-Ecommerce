from importlib.metadata import version
from flask import Flask,jsonify,request
from flask_restx import Api,Resource
from config import DevConfig
from flask_cors import CORS,cross_origin
from model import Store, User, Billboard, Category, Size, Color, Product, Image, Order,OrderItem
from database import db
from flask_migrate import Migrate
from functools import wraps
from jose import jwt
from serialize import configure_serializers
from sqlalchemy import or_
from sqlalchemy.orm import joinedload, subqueryload
from decouple import config
import stripe


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

stripe_keys = {
        "secret_key": config("STRIPE_SECRET_KEY"),
        "publishable_key": config("STRIPE_PUBLISHABLE_KEY"),
    }

stripe.api_key = stripe_keys['secret_key']
endpoint_secret = 'whsec_9827f858a1435d6aec418e0ef84bd91d32639f3ed4cfd5209eecec527febd9d7'


db.init_app(app)
migrate=Migrate(app,db)
api=Api(app,doc='/api/docs')
store_model, user_model, billboard_model,category_model,size_model,color_model,product_model,full_product_model,order_model = configure_serializers(api)


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

#----------------------------------------------------------------
@api.route('/api/<string:user_id>/<string:store_id>/store')
class UserStoreDeleteResource(Resource):
    @api.marshal_with(store_model)
    def delete (self,user_id,store_id):
        if not user_id:
            return {'message': 'User unauthenticated'}, 401
        if not store_id:
            return {'message': 'Store ID is required'}, 400
       
        store_to_delete = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        store_delete_copy = store_to_delete.__dict__.copy()
        store_to_delete.delete()
        return store_delete_copy
    
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
        category = Category.query.options(joinedload(Category.billboard)).filter_by(id=category_id,store_id=store_id).first_or_404()
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

#-----------------------------STORE AND SIZE API----------------------------------- 
#GETTING SPECIFIC COLOR FROM COLOR ID
@api.route('/api/size/<string:size_id>')
class SingleSizeResource(Resource):

    @api.marshal_with(size_model)
    def get(self,size_id):
        size = Size.query.filter_by(id = size_id).first_or_404() 
        return size


#GETTING ALL SIZES WITH STORE ID 
@api.route('/api/<string:store_id>/sizes')
class UserStoreSizesResource(Resource):
    @api.marshal_list_with(size_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        sizes = Size.query.filter_by(store_id=store_id).order_by(Size.created_at.desc()).all()
        if sizes:
            return sizes
        else:
            return [],200
        
#CREATE A SIZES WITH STORE ID 
            
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
    
    
#GETTING size BASED ON TH STORE ID AND COLOR ID
@api.route('/api/<string:store_id>/sizes/<string:size_id>')
class StoreSpecificSizeUpdateResource(Resource):

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
class UserSpecificSizeResource(Resource):
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



#-----------------------------STORE AND COLOR API----------------------------------- 
#GETTING SPECIFIC COLOR FROM COLOR ID
@api.route('/api/color/<string:color_id>')
class SingleColorResource(Resource):

    @api.marshal_with(color_model)
    def get(self,color_id):
        color = Color.query.filter_by(id = color_id).first_or_404() 
        return color


#GETTING ALL ColorS WITH STORE ID 
@api.route('/api/<string:store_id>/colors')
class UserStoreColorsResource(Resource):
    @api.marshal_list_with(color_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        colors = Color.query.filter_by(store_id=store_id).order_by(Color.created_at.desc()).all()
        if colors:
            return colors
        else:
            return [],200
        
#CREATE A colorS WITH STORE ID 
            
    @api.marshal_with(color_model)
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
        new_color = Color(name=data.get('name'),store_id=store_id,value=data.get('value'))
        new_color.save()
        return new_color, 201
    
    
#GETTING color BASED ON TH STORE ID AND COLOR ID
@api.route('/api/<string:store_id>/colors/<string:color_id>')
class StoreSpecificcolorUpdateResource(Resource):

    @api.marshal_with(color_model)
    def get(self,store_id,color_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        color = Color.query.filter_by(id=color_id,store_id=store_id).first_or_404()
        return color 
      
    @api.marshal_with(color_model)
    def patch(self,store_id,color_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not color_id:
            return {'message': 'Color ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'User unauthenticated'}, 401
        if 'name' not in data:
            return {'message': 'Name is required'}, 400
        if 'value' not in data:
            return {'message': 'Value is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        color_to_update = Color.query.filter_by(id=color_id,store_id=store_id).first_or_404()
        color_to_update.update(data.get('name'),data.get('value'))
        return color_to_update
    
# DELETE A color BASED ON MATCHING USER ID AND STORE ID AND color ID
@api.route('/api/<string:user_id>/<string:store_id>/color/<string:color_id>')
class UserSpecificColorResource(Resource):
    @api.marshal_with(color_model)
    def delete (self,user_id,store_id,color_id):
        if not user_id:
            return {'message': 'Unauthenticated'}, 400
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not color_id:
            return {'message': 'color ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        color_to_delete = Color.query.filter_by(id=color_id,store_id=store_id).first_or_404()
        color_copy = color_to_delete.__dict__.copy()
        color_to_delete.delete()
        return color_copy 

#----------------------------------STORE AND PRODUCT--------------------------------------    

#GETTING A SINGLE PRODUCT FROM PRODUCT ID   
@api.route('/api/product/<string:product_id>')
class SingleProductResource(Resource):

    @api.marshal_with(product_model)
    def get(self,product_id):
        product = Product.query.options(joinedload(Product.images)).filter_by(id=product_id).first_or_404()
        return product


@api.route('/api/store/<string:store_id>/products')
class UserStoreProductsResource(Resource):
    @api.marshal_list_with(product_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400

        # Create a query
        query = Product.query.options(
            joinedload(Product.category),
            joinedload(Product.size),
            joinedload(Product.color),
            subqueryload(Product.images)  # Include images
        ).filter_by(store_id=store_id)
   
        # Order by creation date and execute the query
        products = query.order_by(Product.created_at.desc()).all()

        if products:
            return products
        else:
            return [],200



#GETTING ALL products WITH STORE ID 
@api.route('/api/<string:store_id>/products')
class UserStoreProductsResource(Resource):
    @api.marshal_list_with(full_product_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400

        # Get URL parameters
        categoryId = request.args.get('categoryId')
        colorId = request.args.get('colorId')
        sizeId = request.args.get('sizeId')
        isFeatured = request.args.get('isFeatured')

        # Create a query
        query = Product.query.options(
            joinedload(Product.category),
            joinedload(Product.size),
            joinedload(Product.color),
            subqueryload(Product.images)  # Include images
        ).filter_by(store_id=store_id,is_archived=False)

        # Add filters based on URL parameters
        if categoryId:
            query = query.filter_by(category_id=categoryId)
        if colorId:
            query = query.filter_by(color_id=colorId)
        if sizeId:
            query = query.filter_by(size_id=sizeId)
        if isFeatured:
            if isFeatured == "true":
                query = query.filter_by(is_featured=True)
        # Order by creation date and execute the query
        products = query.order_by(Product.created_at.desc()).all()

        if products:
            return products
        else:
            return [],200
        
#CREATE A productS WITH STORE ID 
            
    @api.marshal_with(product_model)
    def post(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'Unauthenticated'},400
        if 'name' not in data:
            return {'error': 'Missing required field "label"'}, 400
        if 'price' not in data:
            return {'error': 'Missing required field "label"'}, 400
        if 'images' not in data or not data.get('images'):
            return {'error': 'Image URL is required'}, 400
        if 'isArchived' not in data:
            return {'error': 'Archived is required'},400
        if 'isFeatured' not in data:
            return {'error': 'Featured is required'},400
        if 'sizeId' not in data:
            return {'error': 'Size ID is required'}, 400
        if 'categoryId' not in data:
            return {'error': 'Category ID is required'}, 400
        if 'colorId' not in data:
            return {'error': 'Color ID is required'}, 400
        existing_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        new_product = Product(name=data.get('name'),store_id=store_id,
                              price=data.get('price'),category_id=data.get('categoryId'),is_featured=data.get('isFeatured'),is_archived=data.get('isArchived'),
                              size_id=data.get('sizeId'),color_id=data.get('colorId'))
        new_product.save()
        images = data.get('images')
        for image_url in images:
            new_image = Image(url=image_url['url'],product_id=new_product.id)
            new_image.save()
        
        return new_product, 201
    
    
#GETTING PRODUCTS BASED ON TH STORE ID AND PRODUCTS ID
@api.route('/api/<string:store_id>/products/<string:product_id>')
class StoreSpecificProductUpdateResource(Resource):

    @api.marshal_with(full_product_model)
    def get(self,store_id,product_id):
        if not product_id:
            return {'message': 'Product ID is required'}, 400
        product = Product.query.filter_by(id=product_id,store_id=store_id).first_or_404()
        return product
      
    @api.marshal_with(product_model)
    def patch(self,store_id,product_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not product_id:
            return {'message': 'Product ID is required'}, 400
        data = request.get_json()
        if 'user_id' not in data:
            return {'message': 'Unauthenticated'},400
        if 'name' not in data:
            return {'error': 'Missing required field "label"'}, 400
        if 'price' not in data:
            return {'error': 'Missing required field "label"'}, 400
        if 'images' not in data or not data.get('images'):
            return {'error': 'Image URL is required'}, 400
        if 'sizeId' not in data:
            return {'error': 'Size ID is required'}, 400
        if 'categoryId' not in data:
            return {'error': 'Category ID is required'}, 400
        if 'colorId' not in data:
            return {'error': 'Color ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=data.get('user_id')).first_or_404()
        product_to_update = Product.query.filter_by(id=product_id,store_id=store_id).first_or_404()
        product_to_update.update(data.get('name'),data.get('price'),data.get('categoryId'),data.get('colorId'),data.get('sizeId'),data.get('isFeatured'),data.get('isArchived'))
        images_to_created = data.get('images')
    
        Image.query.filter_by(product_id=product_id).delete()
        db.session.commit()
        for image_url in images_to_created:
            new_image = Image(url=image_url['url'],product_id=product_id)
            new_image.save()
        return product_to_update
    
# DELETE A product BASED ON MATCHING USER ID AND STORE ID AND product ID
@api.route('/api/<string:user_id>/<string:store_id>/product/<string:product_id>')
class UserSpecificProductResource(Resource):
    @api.marshal_with(product_model)
    def delete (self,user_id,store_id,product_id):
        if not user_id:
            return {'message': 'Unauthenticated'}, 400
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        if not product_id:
            return {'message': 'product ID is required'}, 400
        user_store = Store.query.filter_by(id=store_id,user_id=user_id).first_or_404()
        product_to_delete = Product.query.filter_by(id=product_id,store_id=store_id).first_or_404()
        product_copy = product_to_delete.__dict__.copy()
        product_to_delete.delete()
        return product_copy 


@api.route('/api/<string:store_id>/checkout')
class UserCheckOutResource(Resource):
    
    def post(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        data = request.get_json()
        if 'productIds' not in data:
            return {'message': 'Product ids are required'}, 400
        print(data.get('productIds'),file=sys.stderr)
        # products = Product.query.filter_by(id=data.get('productIds'))
        productIds = data.get('productIds')
        products = Product.query.filter(Product.id.in_(productIds)).all()
        print(products,file=sys.stderr)
        line_items = []
        for product in products:
            line_items.append({
                'quantity':1,
                'price_data':{
                    'currency':'USD',
                    'product_data':{
                        'name': product.name
                    },
                    'unit_amount':int(product.price*100)
                }
            })
        new_order = Order(store_id=store_id,is_paid=False)
        new_order.save()
        for product in products:
            orderitem = OrderItem(product_id=product.id,order=new_order)
            orderitem.save()
        
        session = stripe.checkout.Session.create(
        line_items=line_items,
        billing_address_collection='required',
        phone_number_collection={"enabled": True},
        mode='payment',
        success_url='http://localhost:3001/cart?success=1',
        cancel_url='http://localhost:3001/cart?cancelled=1',
        metadata={
        'orderId': new_order.id
        },
        )
        return jsonify({'url' : session.url})
#----------------------------------------------------------------
    
@api.route('/api/<string:store_id>/orders')
class StoreOrderResource(Resource):
    
    @api.marshal_list_with(order_model)
    def get(self,store_id):
        if not store_id:
           return {'message': 'Store ID is required'}, 400
        orders = Order.query.filter_by(store_id=store_id).order_by(Order.created_at.desc()).all()
        if orders:
            return orders
        return [],200

@api.route('/api/webhook')
class StoreOrderWebhook(Resource):

    def post(self):
        event=None
       
        payload = request.get_data(as_text=True)

        sig_header = request.headers['STRIPE_SIGNATURE']

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
        )
        except ValueError as e:
        # Invalid payload
            raise e
        except stripe.error.SignatureVerificationError as e:
        # Invalid signature
            raise e

    # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print(session,file=sys.stderr)
            phone = session['customer_details']['phone']
            address = session['customer_details']['address']
            address_components = [
                address['line1'],
                address['line2'],
                address['city'],
                address['state'],
                address['postal_code'],
                address['country']
            ]
            address_string = ', '.join(filter(None, address_components))
            order_id = session['metadata']['orderId']
            order=Order.query.get(order_id)
            if order:
                order.update(True,address_string,phone)
            for order_item in order.orderitems:
                product=Product.query.get(order_item.product_id)
                if product:
                    product.update_is_archived()
    
        return None,200

#-------------Retrieve paid orders-----------------------
@api.route('/api/<string:store_id>/orders/paid')
class OrdersPaidResource(Resource):
    @api.marshal_list_with(order_model)
    def get(self,store_id):
        if not store_id:
            return {'message': 'Store ID is required'}, 400
        print(store_id,file=sys.stderr)
        orders = Order.query.filter_by(is_paid=True,store_id=store_id).all()
        if orders:
            return orders
        return [],200
         

if __name__ == '__main__':
    app.run(debug=True,port=8080)