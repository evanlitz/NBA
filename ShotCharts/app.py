import streamlit as st

st.set_page_config(page_title="NBA Shot Chart", layout="centered")

import pandas as pd
from main import load_shooting_data, load_league_averages, get_player_shot_profile, plot_shot_chart

@st.cache_data
def load_data():
    return load_shooting_data(), load_league_averages()

df, league_avg_df = load_data()

st.title("📐 NBA Player Shot Chart Explorer")
st.markdown("Enter a player name and season to explore their shooting zones and efficiency.")

# Sidebar input
st.sidebar.header("Select Player and Enter Season")
players = sorted(df["player"].dropna().unique())
selected_player = st.sidebar.selectbox("Player", players)

min_season = int(df["season"].min())
max_season = int(df["season"].max())
selected_season = st.sidebar.number_input("Season (Year)", min_value=min_season, max_value=max_season, value=max_season, step=1)

# Submit Button
if st.sidebar.button("Generate Shot Chart"):
    try:
        shot_profile = get_player_shot_profile(df, selected_player, selected_season, league_avg_df)
        fig = plot_shot_chart(shot_profile, selected_player, selected_season)
        st.pyplot(fig)
    except ValueError as e:
        st.warning(str(e))
else:
    st.info("Select a player and season, then click 'Generate Shot Chart'.")
