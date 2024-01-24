from database import db
from sqlalchemy import ForeignKey,Integer,Column, String,DateTime,func
from sqlalchemy import String
from sqlalchemy.orm import relationship
from datetime import datetime



class Store(db.Model):
    __tablename__ = 'store'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.current_timestamp())
    updated_at = Column(DateTime(timezone=True), onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<Store {self.id} >"

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
