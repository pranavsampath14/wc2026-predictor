from flask import Flask, request, jsonify
from flask_cors import CORS
from features import run_prediction
import json
import os

app = Flask(__name__)
CORS(app)

CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../model/simulation_cache.json')
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    home_team = data['home_team']
    away_team = data['away_team']

    result_prob = run_prediction(home_team, away_team)

    result = {
        home_team: round(float(result_prob[0]), 3),
        'draw': round(float(result_prob[1]), 3),
        away_team: round(float(result_prob[2]), 3)
    }

    return jsonify(result), 200

@app.route('/simulate', methods=['GET'])
def simulate():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, 'r') as f:
            return jsonify(json.load(f)), 200

    from simulation import simulate_tournament
    results = simulate_tournament()

    with open(CACHE_PATH, 'w') as f:
        json.dump(results, f)

    return jsonify(results), 200

@app.route('/simulate/refresh', methods=['POST'])
def simulate_refresh():
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)

    from simulation import simulate_tournament
    results = simulate_tournament()

    with open(CACHE_PATH, 'w') as f:
        json.dump(results, f)

    return jsonify(results), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)