from database import db
from sqlalchemy import ForeignKey,Integer,Column, String,DateTime,func
from sqlalchemy import String
from sqlalchemy.orm import relationship
import datetime
import uuid



class Store(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=datetime.datetime.now)
    user_id = db.Column(db.String(50), db.ForeignKey('user.id'), nullable=False)
    billboards = db.relationship('Billboard', back_populates='store', lazy=True)
    categories = db.relationship('Category', back_populates='store', lazy=True)


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

class Billboard(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    label = db.Column(db.String(50), nullable=False)
    imageUrl = db.Column(db.String(100), nullable=False)
    store_id = db.Column(db.String(50), db.ForeignKey('store.id'), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.current_timestamp())
    store = db.relationship('Store', back_populates='billboards')
    categories = db.relationship('Category', back_populates='billboard', lazy=True)

    def __repr__(self):
        return f"<Billboard {self.id} >"

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self,label,imageUrl):
        self.label = label
        self.imageUrl = imageUrl
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

class Category(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()), unique=True)
    store_id = db.Column(db.String(50), db.ForeignKey('store.id'), nullable=False)
    store = db.relationship('Store', back_populates='categories')
    billboard_id = db.Column(db.String(50), db.ForeignKey('billboard.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.current_timestamp())
    billboard = db.relationship('Billboard', back_populates='categories')


    def __repr__(self):
        return f"<Category {self.id} >"

    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self,name,billboard_id):
        self.name = name
        self.billboard_id = billboard_id
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()


