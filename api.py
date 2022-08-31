from __future__ import print_function
import sys
from threading import Thread
from flask import Flask, session
from flask_cors import CORS
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dbmanager.TaskManager import run_tasks_loop
from dbmanager.blueprints.resources import resources_bp
from dbmanager.constants import DATABASE_PATH, DATABASE_NAME_NEW
from dbmanager.extensions import db_manager, CustomJSONEncoder

API_VERSION = "1.1.0"

app = Flask(__name__)
app.config.from_file("flask.config.json", load=json.load)
app.json_encoder = CustomJSONEncoder
CORS(app)
engine = create_engine('sqlite:///dbmanager/' + DATABASE_PATH + DATABASE_NAME_NEW + '.sqlite')
session_factory = sessionmaker(bind=engine)
ScopedSession = scoped_session(session_factory)
app_session = ScopedSession()
db_manager.init(engine, app_session)
tasks_thread = Thread(target=run_tasks_loop, daemon=True)
tasks_thread.start()


app.register_blueprint(resources_bp)

if __name__ == "__main__":
	port = 5000
	debug = True
	if len(sys.argv) > 1:
		port = int(sys.argv[1])
	if len(sys.argv) > 2:
		debug = sys.argv[2] == 'true'
	app.run(host="127.0.0.1", port=port, debug=debug)
