import streamlit as st
import pandas as pd

# Load data
@st.cache_data
def load_data():
    per_game = pd.read_csv("data/Player Per Game.csv")
    per_100 = pd.read_csv("data/Per 100 Poss.csv")
    totals = pd.read_csv("data/Player Totals.csv")
    return per_game, per_100, totals

per_game_df, per_100_df, totals_df = load_data()

# UI Inputs
st.title("NBA Stat Presenter")

selected_player = st.text_input("Enter Player Name (e.g., LeBron James):")
selected_season = st.number_input("Enter Season Year (e.g., 2023):", min_value=1947, max_value=2025, step=1)
mode = st.selectbox("Select Stat View:", ["Per Game", "Per 100 Possessions", "Total"])

# Display logic
def filter_stats(df, player_name, season):
    return df[(df["player"].str.lower() == player_name.lower()) & (df["season"] == season)]

if selected_player and selected_season:
    if mode == "Per Game":
        filtered = filter_stats(per_game_df, selected_player, selected_season)
    elif mode == "Per 100 Possessions":
        filtered = filter_stats(per_100_df, selected_player, selected_season)
    else:  # Total
        filtered = filter_stats(totals_df, selected_player, selected_season)

    if not filtered.empty:
        st.subheader(f"{selected_player} - {selected_season} Season Stats ({mode})")
        st.dataframe(filtered.drop(columns=["season", "player_id", "birth_year", "lg", "tm"], errors="ignore"))
    else:
        st.warning("No stats found for that player/season.")
