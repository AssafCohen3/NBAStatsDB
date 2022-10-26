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
from dbmanager.blueprints.presets import presets_bp
from dbmanager.blueprints.suggestions import suggestions_bp
from dbmanager.blueprints.tasks import tasks_bp
from dbmanager.tasks.TaskManager import run_tasks_loop
from dbmanager.blueprints.resources import resources_bp
from dbmanager.extensions import db_manager, CustomJSONEncoder

API_VERSION = "1.1.0"

app = Flask(__name__)
app.config.from_file("flask.config.json", load=json.load)
app.json_encoder = CustomJSONEncoder
CORS(app)
lang = Language(app)

tasks_thread = Thread(target=run_tasks_loop, daemon=True)
tasks_thread.start()
app.register_blueprint(resources_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(presets_bp)
app.register_blueprint(suggestions_bp)


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


if __name__ == "__main__":
    port = 5000
    debug = True
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = sys.argv[2] == 'true'
    app.run('127.0.0.1', port=port, debug=debug, threaded=True)
