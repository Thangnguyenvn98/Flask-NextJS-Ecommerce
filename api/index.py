from flask import Flask,jsonify,request
from flask_restx import Api,Resource,fields
from config import DevConfig
from flask_cors import CORS
from model import Items
from database import db
from flask_migrate import Migrate



app=Flask(__name__)
app.config.from_object(DevConfig)
CORS(app)

db.init_app(app)
migrate=Migrate(app,db)
api=Api(app,doc='/api/docs')

items_model=api.model(
    "Items",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "price":fields.Float()
    }
)

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



if __name__ == '__main__':
    app.run(debug=True,port=8080)