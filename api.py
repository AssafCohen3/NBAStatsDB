from __future__ import print_function
import os.path
import sys
from threading import Thread
from flask import Flask, request
from flask_cors import CORS
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from dbmanager.FlaskLanguage import Language
from dbmanager.TaskManager import run_tasks_loop
from dbmanager.blueprints.resources import resources_bp
from dbmanager.extensions import db_manager, CustomJSONEncoder, init_socket, socketio
from dbmanager.test2 import test_socket

API_VERSION = "1.1.0"

app = Flask(__name__)
app.config.from_file("flask.config.json", load=json.load)
app.json_encoder = CustomJSONEncoder
CORS(app)
Language(app)
init_socket(app)
tasks_thread = Thread(target=run_tasks_loop, daemon=True)
tasks_thread.start()
app.register_blueprint(resources_bp)
app.config['firstConnect'] = True


def init_sqlalchemy(db_name: str):
    database_uri = 'sqlite:///' + db_name
    engine = create_engine(database_uri, connect_args={'check_same_thread': False})
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = scoped_session(session_local)
    db_manager.init(engine, db_session)


@app.route('/init_db', methods=['POST'])
def init_db():
    db_name = request.json.get('db_name')
    create_db = request.json.get('create_db')
    if db_name and (os.path.exists(db_name) or create_db):
        # TODO try catch
        init_sqlalchemy(db_name)
        return {
            'status': 'ok',
            'db_name': db_name
        }
    return {
        'status': 'failed',
        'bd_name': ''
    }


@socketio.on('first-connect')
def handle_connection(_):
    if app.config['firstConnect']:
        # socketio.start_background_task(test_socket)
        app.config['firstConnect'] = False


if __name__ == "__main__":
    port = 5000
    debug = True
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = sys.argv[2] == 'true'
    socketio.run(app, '127.0.0.1', port=port, debug=debug, allow_unsafe_werkzeug=True)
