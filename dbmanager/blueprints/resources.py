from flask import Blueprint, jsonify

from dbmanager.extensions import db_manager

resources_bp = Blueprint('resources', __name__, url_prefix='/resources')


@resources_bp.route('/', methods=['GET'])
def get_resources_list():
    to_ret = db_manager.get_resources_list_compact()
    to_ret = jsonify(to_ret)
    return to_ret


@resources_bp.route('/<resource_id>', methods=['GET'])
def get_resource_details(resource_id):
    to_ret = db_manager.get_resource_details(resource_id)
    to_ret = jsonify(to_ret)
    return to_ret
