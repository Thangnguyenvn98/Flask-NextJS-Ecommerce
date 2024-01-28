from database import db
from sqlalchemy import ForeignKey,Integer,Column, String,DateTime,func
from sqlalchemy import String
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid



class Store(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.current_timestamp())
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return f"<Store {self.id} >"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self,name):
        self.name = name
        db.session.commit()



class User(db.Model):
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    picture = db.Column(db.String(500))
    stores = db.relationship('Store', backref='user', lazy=True)


    def __repr__(self):
        return f"< {self.name} >"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
