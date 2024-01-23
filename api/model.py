from database import db
from sqlalchemy import ForeignKey
from sqlalchemy import String


class Items(db.Model):
    id=db.Column(db.Integer(), primary_key=True)
    title=db.Column(db.String(50),nullable=False)
    price=db.Column(db.Float(),nullable=False)

    def __repr__(self):
        return f"<Recipe {self.title} >"
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()