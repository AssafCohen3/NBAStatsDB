from flask import Blueprint, jsonify
import dbmanager.AppI18n

locale_bp = Blueprint('locale', __name__, url_prefix='/locale')


@locale_bp.route('/available', methods=['GET'])
def get_available_locales():
    return jsonify(dbmanager.AppI18n.get_available_locales())


@locale_bp.route('/default', methods=['GET'])
def get_default_locale():
    return dbmanager.AppI18n.get_default_locale()
