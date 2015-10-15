from flask import Flask, request, make_response, jsonify
from flask_restful import Resource, Api
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.mongo_json_encoder import JSONEncoder

# Basic Setup
app = Flask(__name__)                    # create flask instance and assign var
mongo = MongoClient('localhost', 27017)  # establish connection to database
app.db = mongo.develop_database          # specify database used to store data
api = Api(app)                           # creates instance of the flask_restful api


# creates, retrieves, and updates a trip instance
class Trip(Resource):

    # when invoked creates new instance of a trip
    def post(self):
        # sets variable to client-provided JSON
        trip = request.json
        # access collection where the new trip will be stored
        trip_collection = app.db.trips
        # inserts one trip (JSON) into the trip_collection
        result = trip_collection.insert_one(trip)
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
    def put(self, trip_id):
        trip_update = request.json
        trip_collection = app.db.trips

        result = trip_collection.update_one({'_id': ObjectId(trip_id)},
                                            {'$set': trip_update})
        updated = trip_collection.find_one({'_id': ObjectId(trip_id)})
        return updated

    # delete trip



# Add REST resource to API
# Route defines a URL that can be called by a client application
# Parameter 1: resource which we want ot map to a specific URL
# Parameter 2/3: one is used to create an instance the other is used to retrieve a specific instance
api.add_resource(MyObject, '/myobject/','/myobject/<string:myobject_id>')

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
