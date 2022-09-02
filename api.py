from __future__ import print_function
import sys
from threading import Thread
from flask import Flask
from flask_cors import CORS
import json
from flask_sqlalchemy import SQLAlchemy
from dbmanager.FlaskLanguage import Language
from dbmanager.TaskManager import run_tasks_loop
from dbmanager.blueprints.resources import resources_bp
from dbmanager.constants import DATABASE_PATH, DATABASE_NAME_NEW
from dbmanager.extensions import db_manager, CustomJSONEncoder, init_socket, socketio
from dbmanager.test2 import test_socket

API_VERSION = "1.1.0"

app = Flask(__name__)
app.config.from_file("flask.config.json", load=json.load)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbmanager/' + DATABASE_PATH + DATABASE_NAME_NEW + '.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json_encoder = CustomJSONEncoder
CORS(app)
db = SQLAlchemy(app)
Language(app)
# engine = create_engine()
# session_factory = sessionmaker(bind=engine)
# app_session = scoped_session(session_factory)
# app_session = ScopedSession()
db_manager.init(db.engine, db.session)
init_socket(app)
tasks_thread = Thread(target=run_tasks_loop, daemon=True)
tasks_thread.start()

app.register_blueprint(resources_bp)
app.config['firstConnect'] = True


@socketio.on('first-connect')
def handle_connection(msg):
    if app.config['firstConnect']:
        test_thread = Thread(target=test_socket, daemon=True)
        test_thread.start()
        app.config['firstConnect'] = False


if __name__ == "__main__":
    port = 5000
    debug = True
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = sys.argv[2] == 'true'
    socketio.run(app, '127.0.0.1', port=port, debug=debug, allow_unsafe_werkzeug=True, log_output=False)
# app.run(host="127.0.0.1", port=port, debug=debug)
