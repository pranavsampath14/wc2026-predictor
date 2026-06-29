# WC 2026 Predictor

An end-to-end machine learning system for predicting FIFA World Cup 2026 match outcomes and simulating tournament results. Built as a data science portfolio project covering the full lifecycle: data cleaning, feature engineering, model training, REST API, and React frontend.

**Live demo:** [wc2026-predictor-mocha.vercel.app](https://wc2026-predictor-mocha.vercel.app)

---

## Features

- **Match predictor** - select any group stage fixture and get win/draw/loss probabilities from a trained XGBoost model
- **Tournament simulator** - Monte Carlo simulation across 10,000 runs produces stage-by-stage advancement probabilities for all 48 teams
- **Group browser** - all 12 groups with fixtures, kickoff times in AEST, and venues

---

## How It Works

### Data

Three datasets underpin the project:

- **Match results** ([martj42/international-football-results](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017)) - 32,000+ international matches from 1990–2026, used for feature computation and model training
- **Historical Elo ratings** ([saifalnimri/international-football-elo-ratings](https://www.kaggle.com/datasets/saifalnimri/international-football-elo-ratings)) - match-level Elo updates used in historical feature engineering
- **WC 2026 Elo snapshots** - annual Elo snapshots for all 48 qualified teams, used for current team strength at inference time

### Feature Engineering

Each match is represented by 12 features computed from historical data up to (but not including) the match date, avoiding any data leakage:

| Feature | Description |
|---|---|
| `elo_diff` | Difference in Elo ratings between home and away team |
| `home_form` / `away_form` | Tournament-weighted win rate over last 10 games |
| `form_diff` | Difference in recent form |
| `h2h_home_winrate` / `h2h_away_winrate` / `h2h_draw_rate` | Historical head-to-head rates, shrunk toward a 0.33 prior (full trust after 10 meetings) |
| `neutral` | Whether the match is at a neutral venue |
| `home_goals_scored` / `home_goals_conceded` | Average goals over last 10 games |
| `away_goals_scored` / `away_goals_conceded` | Average goals over last 10 games |

**Tournament weighting** - recent form is weighted by match importance. World Cup games carry 4× the weight of friendlies (0.5×). These weights were chosen using domain knowledge rather than derived from data, after identifying that knockout tournament mechanics create a structural imbalance that biases data-derived weights.

**H2H shrinkage** - head-to-head win rates are blended with a 0.33 uninformative prior, reaching full trust only after 10 meetings. This prevents sparse matchup histories from producing overconfident estimates - a technique drawn from actuarial credibility theory.

**Neutral venue handling** - for neutral venue games, the model is run in both directions (home/away swapped) and the output probabilities are averaged. This removes sensitivity to which team is arbitrarily listed as "home" on a neutral fixture.

### Modelling

A time-based train/test split was used throughout (train: 1990–2021, test: 2022–2026) to ensure the model is always evaluated on matches it has never seen.

**Baseline:** Logistic regression (with StandardScaler normalisation)

**Final model:** XGBoost classifier, selected for superior predictive power over interpretability

Log loss was chosen as the primary metric rather than accuracy. Well-calibrated probabilities matter more than binary classification accuracy for two reasons: (1) the downstream Monte Carlo simulator samples from these probabilities, so miscalibration compounds across thousands of simulations, and (2) accuracy can be gamed by always predicting the majority class.

| Model | Accuracy | Log Loss |
|---|---|---|
| Logistic Regression (unbalanced) | 58.3% | 0.908 |
| Logistic Regression (balanced) | 55.3% | 0.945 |
| XGBoost (unbalanced) | 59.1% | 0.897 |
| XGBoost (balanced) | 55.5% | 0.934 |

**Validation against bookmaker odds** - predictions were spot-checked against real bookmaker odds for upcoming WC 2026 fixtures. The model produces probabilities within 3–8 percentage points of professional odds on most matchups, without access to squad news, injuries, or betting market data.

Example (Norway vs Senegal, Group I):
- Bookmaker implied: Norway 46.7%, Draw 28.2%, Senegal 28.6%
- Model output: Norway 39.9%, Draw 27.9%, Senegal 32.2%

### Monte Carlo Simulation

The tournament simulator runs 10,000 complete tournament simulations. In each run:

1. All 12 group stages are simulated - 6 matches per group using win/draw/loss probabilities from the model
2. Scorelines are sampled from a Poisson distribution parameterised by each team's average goals scored and conceded, constrained to be consistent with the match outcome
3. Group standings are determined by points, then goal difference, then goals scored
4. The 8 best third-placed teams advance alongside the 12 group winners and 12 runners-up (32 teams total)
5. Knockout rounds are simulated with draws renormalised out (no draws in knockout football)

Aggregating across 10,000 runs produces each team's probability of reaching each stage.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data & modelling | Python, pandas, NumPy, scikit-learn, XGBoost |
| API | Flask, Flask-CORS, Gunicorn |
| Frontend | React, Vite, React Router |
| Backend hosting | Render |
| Frontend hosting | Vercel |

---

## Known Limitations

**Draw prediction** - the model struggles to predict draws, correctly identifying only ~2% of actual draws. This is a known hard problem in football prediction; draws are structurally underrepresented in the win/loss signal the model learns from.

**Host nation inflation** - Mexico, USA, and Canada receive a home advantage boost for group stage games. The model's home advantage signal may slightly overstate the benefit, particularly for Mexico (simulated at ~4.5% tournament win probability vs bookmaker ~2-3%).

**Static features** - the model uses pre-tournament data only. It does not update with live results as the tournament progresses. A team that gets a key player injured in game 1 will not have that reflected in game 2 predictions.

**Squad quality signal** - FIFA player rating data (which would capture squad depth and individual brilliance) only covers from 2017, which would have required cutting 75% of training data. Elo ratings are used as the primary quality signal instead, which is outcome-based and therefore slower to reflect sudden quality changes.

**Cold start delay** - the backend runs on Render's free tier, which spins down after 15 minutes of inactivity. The first prediction after a period of inactivity may take 30–60 seconds.

**Third-place bracket assignment is simplified** - the official FIFA rules assign third-place teams to specific bracket slots based on which groups they came from. The simulator randomly assigns the 8 best third-place teams to available slots instead. This affects which teams meet in the round of 32 but has negligible impact on overall tournament win probabilities across 10,000 simulations.

---

## Local Setup

**Prerequisites:** Python 3.9+, Node.js 18+

**Backend**
```bash
# Clone the repo
git clone https://github.com/pranavsampath14/wc2026-predictor.git
cd wc2026-predictor

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
cd api
pip install -r requirements.txt

# Start Flask server
python app.py
# Runs on http://localhost:5001
```

**Frontend**
```bash
# In a separate terminal
cd frontend
npm install
npm run dev
# Runs on http://localhost:5173
```

---

## Project Structure

```
wc2026-predictor/
├── api/
│   ├── app.py              # Flask API - /predict and /simulate endpoints
│   ├── features.py         # Feature computation and model loading
│   ├── simulation.py       # Monte Carlo tournament simulator
│   └── requirements.txt
├── data/
│   └── raw/                # Source datasets (results, Elo ratings)
├── model/
│   ├── xgb_model.pkl       # Trained XGBoost model
│   ├── label_encoder.pkl   # Class label encoder
│   └── simulation_cache.json  # Pre-generated simulation results
├── frontend/
│   └── src/
│       ├── pages/          # Home, Group, Simulation views
│       ├── components/     # GroupCard, PredictionPanel, Header
│       └── data/           # Hardcoded tournament draw and schedule
└── notebooks/
    ├── 01_exploration.ipynb
    ├── 02_feature_engineering.ipynb
    └── 03_model_training.ipynb
```

---

## Author

Pranav Sampath - UNSW Actuarial Studies / Computer Science

[GitHub](https://github.com/pranavsampath14)