from flask_restx import fields

def configure_serializers(api):
    store_model = api.model(
        "Store",
        {
            "id": fields.String(),
            "name": fields.String(),
            "user_id": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )

    user_model = api.model(
        "User",
        {
            "id": fields.String(),
            "name": fields.String(),
            "picture": fields.String(),
        }
    )

    billboard_model = api.model(
        "Billboard",
        {
            "id": fields.String(),
            "label": fields.String(),
            "store_id":fields.String(),
            "imageUrl": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )


    category_model = api.model(
        "Category",
        {
            "id": fields.String(),
            "name": fields.String(),
            "store_id":fields.String(),
            "billboard_id": fields.String(),
            "billboard": fields.Nested(billboard_model),  # nested field for billboard
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )

    size_model = api.model(
        "Size",
        {
            "id": fields.String(),
            "name": fields.String(),
            "value":fields.String(),
            "store_id": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )

    color_model = api.model(
        "Color",
        {
            "id": fields.String(),
            "name": fields.String(),
            "value":fields.String(),
            "store_id": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )
    category_name_model = api.model("Category", {
    'name': fields.String()
    })

    size_name_model = api.model("Size", {
    'name': fields.String()
    })

    color_value_model = api.model("Color", {
    'value': fields.String()
    })

    image_url_model = api.model("Image", {
        'url': fields.String()
    })

    product_model = api.model(
        "Product",
        {
            "id": fields.String(),
            "name": fields.String(),
            "price": fields.Float(),
            "store_id":fields.String(),
            "store_id": fields.String(),
            "category": fields.Nested(category_name_model),
            "size": fields.Nested(size_name_model),
            "color": fields.Nested(color_value_model),
            "images": fields.Nested(image_url_model),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
            "is_featured": fields.Boolean(),
            "is_archived": fields.Boolean()
        }
    )

    image_model = api.model(
        "Image", {
            "id": fields.String(),
            "url":fields.String(),
            "product_id": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime()
        }
    )

    full_product_model = api.model (
         "Product",
         {
         "id": fields.String(),
            "name": fields.String(),
            "price": fields.Float(),
            "store_id":fields.String(),
            "category_id": fields.String(),
            "color_id": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
            "is_featured": fields.Boolean(),
            "is_archived": fields.Boolean(),
            "images": fields.Nested(image_model),
            "category": fields.Nested(category_model),
            "color": fields.Nested(color_model),
            "size": fields.Nested(size_model),
           
     })
    orderitem_model = api.model (
        "OrderItem",
        {
            "id":fields.String(),
            "products":fields.Nested(product_model),

        })
    
    order_model = api.model(
        "Order",
        {
            "id": fields.String(),
            "phone":fields.String(),
            "address":fields.String(),
            "is_paid":fields.Boolean(),
            "orderitems":fields.Nested(orderitem_model),
            "created_at":fields.DateTime()
             
        }
    )
        
    

    # Optionally return the models if needed in other parts of the application
    return store_model, user_model, billboard_model,category_model,size_model,color_model,product_model,full_product_model,order_model
