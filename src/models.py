from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    favorite = db.relationship('Favorite', backref='user')

    def __repr__(self):
        return '<User %r>' % self.username
    
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'created': self.created,
            'favorites': list(map(lambda fav: fav.serialize(), self.favorite))
        }

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('character.id'), nullable=True)
    planet_id = db.Column(db.Integer, db.ForeignKey('planet.id'), nullable=True)

    def __repr__(self):
        return '<Favorite %r>' % self.id
    
    def serialize(self):
        return {
            'id': self.id,
            'created': self.created,
            'user_id': self.user_id,
            'username': self.user.username,
            'character_id': self.character_id,
            'planet_id': self.planet_id
        }

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    gender = db.Column(db.String(20), nullable=True)
    hair_color = db.Column(db.String(20), nullable=True)
    eye_color = db.Column(db.String(20), nullable=True)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    favorite = db.relationship('Favorite', backref='character')

    def __repr__(self):
        return '<Character %r>' % self.name
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'hair_color': self.hair_color,
            'eyes_color': self.eye_color,
            'created': self.created
        }


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    terrain = db.Column(db.String(120), nullable=False)
    climate = db.Column(db.String(120), nullable=False)
    population = db.Column(db.String(120), nullable=False)
    created= db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    favorite = db.relationship('Favorite', backref='planet')

    def __repr__(self):
        return '<Planet %r>' % self.name
    
    def serialize(self):
        return {
            'name': self.name,
            'terrain': self.terrain,
            'climate': self.climate,
            'population': self.population,
            'created': self.created
        }