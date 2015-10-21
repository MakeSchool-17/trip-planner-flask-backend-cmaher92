from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder
import bcrypt

# Basic Setup
app = Flask(__name__)                    # create flask instance and assign var
mongo = MongoClient('localhost', 27017)  # establish connection to database
app.db = mongo.develop_database          # specify database used to store data
api = Api(app)                           # creates instance of flask rest_api


# creates, retrieves, and updates a trip instance
class Trip(Resource):

    # when invoked creates new instance of a trip
    def post(self):
        new_trip = request.json  # why not 'get_json' instead?
        trip_collection = app.db.trips
        result = trip_collection.insert_one(new_trip)
        # then check the result after inserting doc into collection
        # find_one() returns a single doc from the database
        # see api.mongodb.org for docs
        my_trip = trip_collection.find_one(
            {'_id': ObjectId(result.inserted_id)})
        return my_trip

    # retrieves an instance of a trip
    def get(self, trip_id=None):
        # checks trip_collection for the doc that client is accessing
        trip_collection = app.db.trips
        # query based on passed trip_id
        trip = trip_collection.find_one_or_404({'_id': ObjectId(trip_id)})
        return trip

    # update trip
    def put(self, trip_id=None):
        trip_update = request.json          # access JSON passed in
        trip_collection = app.db.trips      # access collection of Trips

        # find the trip_id passed in and update using $set
        trip_collection.update_one({'_id': ObjectId(trip_id)},
                                   {'$set': trip_update})
        # retrieve the updated Trip
        updated = trip_collection.find_one({'_id': ObjectId(trip_id)})
        return updated                      # return updated Trip doc

    # delete trip
    def delete(self, trip_id):
        trip_collection = app.db.trips
        trip_collection.delete_one({'_id': ObjectId(trip_id)})
        deleted_trip = trip_collection.find_one_or_404(
            {'_id': ObjectId(trip_id)})
        return deleted_trip


class User(Resource):

    def post(self):
        user = request.json  # requests json doc
        user_collection = app.db.users  # collection of users to store
        encoded_password = user['password'].encode('utf-8')  # encodes pass
        hashed_password = bcrypt.hashpw(encoded_password,  # hashes password
                                        bcrypt.gensalt(app.bcrypt_rounds))
        user['password'] = hashed_password  # updates
        user_collection.insert_one(user)  # inserts
        return

    def get(self):
        resp = jsonify(message=[])
        resp.status_code = 200
        return resp

# Add REST resource to API
# Route defines a URL that can be called by a client application
# Parameter 1: resource which we want ot map to a specific URL
# Parameter 2/3: one is used to create an instance the other is used to retrieve a specific instance
api.add_resource(Trip, '/trip/', '/trip/<string:trip_id>')
api.add_resource(User, '/user/', '/user/<string:user_id>')

# provide a custom JSON serializer for flaks_restful
# JSON encoder takes python objects and turns them into JSON text representation
# Using a custom serializer here because the default doesn't know MongoDB's object IDs
# Remember object_id is not a string
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
