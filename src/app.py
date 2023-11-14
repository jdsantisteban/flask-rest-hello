"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorite, Character, Planet
import requests
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# [GET] /people Get a list of all the people in the database
@app.route('/people', methods=['GET'])
def get_characters():
    # characters = Character()
    characters = Character.query.all()
    # print(characters)

    return jsonify(list(map(lambda character: character.serialize(), characters))), 200

# [GET] /people/<int:people_id> Get a one single people information
@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_character(people_id=None):
    character = Character.query.get(people_id)
    if character:
        return jsonify(character.serialize()), 200
    else:
        return jsonify({'message': 'Character not found'}), 400

# [GET] /planets Get a list of all the planets in the database
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    print(planets)

    return jsonify(list(map(lambda planet: planet.serialize(), planets))), 200

# [GET] /planets/<int:planet_id> Get one single planet information
@app.route('/planets/<int:planet_id>')
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    else:
        return jsonify({'message': 'Planet not found'}), 400

# [GET] /users Get a list of all the blog post users
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()

    return jsonify(list(map(lambda user: user.serialize(), users))), 200

# [GET] /users/favorites Get all the favorites that belong to the current user.
@app.route('/users/favorites/<int:user_id>', methods=['GET'])
def get_user_favorites(user_id=None):
    user = User.query.get(user_id)
    if user is None:
        return jsonify({'message': 'User not found'})
    
    favorite = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify(list(map(lambda fav: fav.serialize(), favorite))), 200
    # user = User.query.filter_by(id=user_id).first()

    # return jsonify(user.serialize()), 200


# [POST] /favorite/planet/<int:planet_id> Add a new favorite planet to the current user with the planet id = planet_id.
@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favplanet_to_user(planet_id=None):
    body = request.get_json()
    user = User.query.get(body['user_id'])
    if user is None:
        raise APIException('User not found', status_code=404)
    planet = Planet.query.get(planet_id)
    if planet is None:
        raise APIException('Planet not found', status_code=404)
    favorite = Favorite()
    favorite.user_id = body['user_id']
    favorite.planet_id = planet_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify('OK'), 200

# [POST] /favorite/people/<int:people_id> Add new favorite people to the current user with the people id = people_id.
@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favpeople_to_user(people_id=None):
    body = request.get_json()
    user = User.query.get(body['user_id'])
    if user is None:
        raise APIException('User not found', status_code=404)
    person = Character.query.get(people_id)
    if person is None:
        raise APIException('Person not found', status_code=404)
    favorite = Favorite()
    favorite.user_id = body['user_id']
    favorite.character_id = people_id
    db.session.add(favorite)
    db.session.commit()
    return jsonify('OK'), 200

# [DELETE] /favorite/planet/<int:planet_id> Delete favorite planet with the id = planet_id.
@app.route('/favorite/planet/<int:planet_id>/<int:user_id>', methods=['DELETE'])
def del_fav_planet(planet_id=None, user_id=None):
    favorite = Favorite.query.filter_by(user_id=user_id, planet_id=planet_id).first()

    if favorite is None:
        raise APIException('Planet not found', status_code=404)
    else:
        db.session.delete(favorite)
        try:
            db.session.commit() 
            return jsonify('OK'), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify(f'error: {error}'), 400
    return jsonify([]), 200


# [DELETE] /favorite/people/<int:people_id> Delete favorite people with the id = people_id.
@app.route('/favorite/people/<int:people_id>/<int:user_id>', methods=['DELETE'])
def del_fav_people(people_id=None, user_id=None):
    favorite = Favorite.query.filter_by(user_id=user_id, character_id=people_id).first()

    if favorite is None:
        raise APIException('Character not found', status_code=404)
    else:
        db.session.delete(favorite)
        try:
            db.session.commit() 
            return jsonify('OK'), 200
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify(f'error: {error}'), 400
    return jsonify([]), 200

   
# populate character
@app.route('/people/population', methods=['GET'])
def get_characters_population():
    response = requests.get('https://www.swapi.tech/api/people?page=1&limit=300')
    response = response.json()
    response = response.get('results')

    for item in response:
        result = requests.get(item.get('url'))
        result = result.json()
        result = result.get('result')
        character = Character()
        character.name = result.get('properties').get('name')
        character.gender = result.get('properties').get('gender')
        character.hair_color = result.get('properties').get('hair_color')
        character.eye_color = result.get('properties').get('eye_color')

        try: 
            db.session.add(character)
            db.session.commit()
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify('error'), 500
    return jsonify('ok'), 200

# populate planet
@app.route('/planets/population', methods=['GET'])
def get_planets_population():
    response = requests.get("https://www.swapi.tech/api/planets?page=1&limit=300")
    response = response.json()
    response = response.get("results")

    for item in response:
        result = requests.get(item.get("url"))
        result = result.json()
        result = result.get("result")
        planet = Planet()
        planet.name = result.get("properties").get("name")
        planet.population = result.get("properties").get("population")
        planet.climate = result.get("properties").get("climate")
        planet.terrain = result.get("properties").get("terrain")
        
        try:
            db.session.add(planet)
            db.session.commit()
        except Exception as error:
            print(error)
            db.session.rollback()
            return jsonify("error"), 500
    return jsonify("ok"), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
