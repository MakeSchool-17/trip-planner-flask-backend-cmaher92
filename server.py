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

#Implement REST Resource
class MyObject(Resource):

    def post(self):
      new_myobject = request.json        # access object provided by request
      myobject_collection = app.db.myobjects  # acess collection in which new object will be stored
      result = myobject_collection.insert_one(request.json)  # insert document into collection

      myobject = myobject_collection.find_one({"_id": ObjectId(result.inserted_id)})
      # retrieve result, take result and fetch specified document

      return myobject
      # return selected document to the client

    def get(self, myobject_id):
      myobject_collection = app.db.myobjects  # reference the collection where the document will be selected from
      myobject = myobject_collection.find_one({"_id": ObjectId(myobject_id)})
      # query based om the myobject_id received as part of the clients' request

      if myobject is None:  # if no object is found a 404 error is returned to client
        response = jsonify(data=[])
        response.status_code = 404
        return response
      else:
        return myobject

# Add REST resource to API
api.add_resource(MyObject, '/myobject/','/myobject/<string:myobject_id>')

# provide a custom JSON serializer for flaks_restful
@api.representation('application/json')
def output_json(data, code, headers=None):
    resp = make_response(JSONEncoder().encode(data), code)
    resp.headers.extend(headers or {})
    return resp

if __name__ == '__main__':
    # Turn this on in debug mode to get detailled information about request related exceptions: http://flask.pocoo.org/docs/0.10/config/
    app.config['TRAP_BAD_REQUEST_ERRORS'] = True
    app.run(debug=True)
