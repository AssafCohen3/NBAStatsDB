from flask import Blueprint, request, jsonify

from dbmanager.SharedData.FranchisesHistory import franchises_history
from dbmanager.SharedData.PlayersIndex import players_index

suggestions_bp = Blueprint('suggestions', __name__, url_prefix='/suggestions')


@suggestions_bp.route('/players', methods=['GET'])
def suggest_players():
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


@suggestions_bp.route('/teams', methods=['GET'])
def suggest_teams():
    to_ret = franchises_history.search_franchise(request.args['search'])
    to_ret = [
        {
            'team_id': t.franchise_id,
            'team_name': t.franchise_name,
            'first_season': t.span_start_year,
            'last_season': t.span_end_year,
        }
        for t in to_ret
    ]
    return jsonify(to_ret)
