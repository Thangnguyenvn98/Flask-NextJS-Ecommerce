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
            "imageUrl:": fields.String(),
            "created_at": fields.DateTime(),
            "updated_at": fields.DateTime(),
        }
    )

    # Optionally return the models if needed in other parts of the application
    return store_model, user_model, billboard_model
