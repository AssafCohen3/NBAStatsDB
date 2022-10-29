import sqlite3
import time
import sqlalchemy.exc
import os.path
import sys
from threading import Thread
from flask import Flask, request
from flask_cors import CORS
import json
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from dbmanager.FlaskLanguage import Language
from dbmanager.blueprints.locale import locale_bp
from dbmanager.blueprints.presets import presets_bp
from dbmanager.blueprints.suggestions import suggestions_bp
from dbmanager.blueprints.tasks import tasks_bp
from dbmanager.tasks.TaskManager import run_tasks_loop
from dbmanager.blueprints.resources import resources_bp
from dbmanager.extensions import db_manager, CustomJSONEncoder


app = Flask(__name__)
app.config.from_file("flask.config.json", load=json.load)
app.json_encoder = CustomJSONEncoder
CORS(app)
lang = Language(app)

tasks_thread = Thread(target=run_tasks_loop, daemon=True)
tasks_thread.start()


@resources_bp.before_request
@presets_bp.before_request
def validate_connection():
    if not db_manager.is_initiated():
        return 'DB is not initiated', 400
    try:
        db_manager.session.connection()
    except sqlite3.DatabaseError:
        return 'Could not connect to the database', 400
    except sqlalchemy.exc.DatabaseError:
        return 'Could not connect to the database', 400


app.register_blueprint(resources_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(presets_bp)
app.register_blueprint(suggestions_bp)
app.register_blueprint(locale_bp)


def init_sqlalchemy(db_name: str):
    database_uri = 'sqlite:///file:' + db_name + '?mode=rw&uri=true'
    engine = create_engine(database_uri, connect_args={'check_same_thread': False}, pool_pre_ping=True)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db_session = scoped_session(session_local)
    db_manager.init(engine, db_session)


def create_db(db_name: str):
    database_uri = 'sqlite:///' + db_name
    engine = create_engine(database_uri)
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE DB(id int);"))
        # noinspection SqlResolve
        connection.execute(text("DROP TABLE DB;"))
    engine.dispose()


@app.route('/init_db', methods=['POST'])
def init_db():
    db_name = request.json.get('db_name')
    to_create_db = request.json.get('create_db')
    if db_name:
        if not os.path.exists(db_name):
            if to_create_db:
                create_db(db_name)
            else:
                return f'{db_name} does not exist', 400
        init_sqlalchemy(db_name)
        return db_name
    return 'missing parameter db_name', 400


if __name__ == "__main__":
    port = 5000
    debug = True
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = sys.argv[2] == 'true'
    app.run('127.0.0.1', port=port, debug=debug, threaded=True)
