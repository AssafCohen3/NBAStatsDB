from __future__ import print_function
import sys
from flask import Flask
from flask_cors import CORS
from flask_restx import Api, Resource, reqparse

API_VERSION = "1.1.0"

app = Flask(__name__)
CORS(app)
api = Api(
	app,
	version=API_VERSION,
	title="Flask backend api",
	description="The backend api system for the Electron Vue app",
	doc="/docs",
)


@api.route("/api_version", endpoint="apiVersion")
class ApiVersion(Resource):
	def get(self):
		return API_VERSION


@api.route("/echo", endpoint="echo")
class HelloWorld(Resource):
	@api.response(200, "Success")
	@api.response(400, "Validation Error")
	def get(self):
		return "Server active!!"


if __name__ == "__main__":
	app.run(host="127.0.0.1", port=int(sys.argv[1]), debug=sys.argv[2] == 'true')
