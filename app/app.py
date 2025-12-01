import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "win_predictor.pkl")
FEATURE_PATH = os.path.join(BASE_DIR, "..", "models", "feature_columns.json")

MODEL_PATH = os.path.normpath(MODEL_PATH)
FEATURE_PATH = os.path.normpath(FEATURE_PATH)

model = joblib.load(MODEL_PATH)

with open(FEATURE_PATH, "r") as f:
    feature_cols = json.load(f)

team_labels = [
    'Chennai Super Kings','Deccan Chargers','Delhi Capitals','Delhi Daredevils',
    'Gujarat Lions','Gujarat Titans','Kings XI Punjab','Kochi Tuskers Kerala',
    'Kolkata Knight Riders','Lucknow Super Giants','Mumbai Indians','Pune Warriors',
    'Punjab Kings','Rajasthan Royals','Rising Pune Supergiant','Rising Pune Supergiants',
    'Royal Challengers Bangalore','Royal Challengers Bengaluru','Sunrisers Hyderabad'
]

team_display_names = {
    "Chennai Super Kings": "Chennai Super Kings",
    "Deccan Chargers": "Deccan Chargers",
    "Delhi Capitals": "Delhi Capitals",
    "Delhi Daredevils": "Delhi Capitals",
    "Gujarat Lions": "Gujarat Lions",
    "Gujarat Titans": "Gujarat Titans",
    "Kings XI Punjab": "Punjab Kings",
    "Punjab Kings": "Punjab Kings",
    "Kochi Tuskers Kerala": "Kochi Tuskers Kerala",
    "Kolkata Knight Riders": "Kolkata Knight Riders",
    "Lucknow Super Giants": "Lucknow Super Giants",
    "Mumbai Indians": "Mumbai Indians",
    "Pune Warriors": "Pune Warriors",
    "Rajasthan Royals": "Rajasthan Royals",
    "Rising Pune Supergiant": "Rising Pune Supergiant",
    "Rising Pune Supergiants": "Rising Pune Supergiant",
    "Royal Challengers Bangalore": "Royal Challengers Bangalore",
    "Royal Challengers Bengaluru": "Royal Challengers Bangalore",
    "Sunrisers Hyderabad": "Sunrisers Hyderabad"
}

team_list = sorted(list(set(team_display_names.values())))
def find_original_label(clean_name):
    for original, mapped in team_display_names.items():
        if mapped == clean_name:
            return original
    return clean_name


# UI
st.title("IPL Match Winner Predictor")
st.write("Select match details below to predict the winning team:")

venue_list = [c.replace("venue_", "") for c in feature_cols if c.startswith("venue_")]

team1 = st.selectbox("Team 1", team_list)
team2 = st.selectbox("Team 2", team_list)
venue = st.selectbox("Venue", venue_list)

season = st.number_input("Season Year", min_value=2008, max_value=2025, value=2023)

toss_winner = st.selectbox("Toss Winner", [team1, team2])
toss_decision = st.selectbox("Toss Decision", ["bat", "field"])

toss_winner_original = find_original_label(toss_winner)

team1_original = find_original_label(team1)
team2_original = find_original_label(team2)
toss_winner_original = find_original_label(toss_winner)

input_data = pd.DataFrame(np.zeros((1, len(feature_cols))), columns=feature_cols)

input_data["match_type"] = 0
input_data["season_year"] = season
input_data["is_modern_ipl"] = 1 if season >= 2018 else 0

input_data["team1_toss"] = 1 if toss_winner_original == team1_original else 0
input_data["team2_toss"] = 1 if toss_winner_original == team2_original else 0

col = f"team1_{team1_original}"
if col in feature_cols:
    input_data[col] = 1

col = f"team2_{team2_original}"
if col in feature_cols:
    input_data[col] = 1

venue_col = "venue_" + venue
if venue_col in feature_cols:
    input_data[venue_col] = 1

if toss_decision == "field":
    input_data["toss_decision_field"] = 1


# PREDICTION
if st.button("Predict Winner"):
    proba = model.predict_proba(input_data)[0]
    pred = np.argmax(proba)

    winner = team_labels[pred]
    confidence = proba[pred] * 100

    st.success(f" Predicted Winner: **{winner}** ({confidence:.2f}% probability)")

    # Probability chart
    st.subheader("Win Probability Distribution")
    prob_df = pd.DataFrame({
        "Team": team_labels,
        "Probability": proba
    })
    st.bar_chart(prob_df.set_index("Team"))
