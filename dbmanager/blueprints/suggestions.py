from flask import Blueprint, request, jsonify

from dbmanager.SharedData.PlayersIndex import players_index

suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@suggestions_bp.route('/players', methods=['GET'])
def get_resource_details():
    to_ret = players_index.search_for_players(request.args['search'])
    to_ret = [
        {
            'player_id': p.player_id,
            'player_name': p.player_name,
            'first_season': p.first_season,
            'last_season': p.last_season,
        }
        for p in to_ret
    ]
    return jsonify(to_ret)
