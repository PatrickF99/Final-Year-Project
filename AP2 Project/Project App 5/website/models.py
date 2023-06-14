from . import db 
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, Float, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    meal_type = db.Column(db.String(10))
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'))
    calories = db.Column(db.Float, nullable=True)
    user = db.relationship('User')



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')

class UserSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    activity_level = db.Column(db.String(20), nullable=False)
    calorie_limit = db.Column(db.Float, nullable=True)
    weight_loss_goal = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('settings', lazy=True))

    def __repr__(self):
        return f"UserSettings('{self.age}', '{self.gender}', '{self.height}', '{self.weight}', '{self.activity_level}')"




class FoodEntry(db.Model):
    __tablename__ = 'food_entries'

    user_id = db.Column(db.Integer, primary_key=True)
    food_name = db.Column(db.String, nullable=False)
    calorie = db.Column(db.Float, nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)

#class Settings(db.Model):
    
    
