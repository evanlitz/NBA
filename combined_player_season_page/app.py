import streamlit as st
import pandas as pd
from main import (
    df,  # season similarity df
    find_similar_players,  # similarity logic
    load_shooting_data,
    load_league_averages,
    get_player_shot_profile,
    plot_shot_chart
)

# Page setup
st.set_page_config(page_title="NBA Player Profile Viewer", layout="centered")
st.title("NBA Player Season Explorer")

# Load data
@st.cache_data
def load_all_data():
    df_shooting = load_shooting_data()
    league_avg = load_league_averages()
    return df_shooting, league_avg

df_shooting, league_avg_df = load_all_data()

# Sidebar: Player & Season Selector
st.sidebar.header("Select Player and Season")
players = sorted(df["player"].unique())
selected_player = st.sidebar.selectbox("Player", players)
season = st.sidebar.number_input("Season", min_value=1976, max_value=2025, value=2023)

if st.sidebar.button("Generate Profile"):
    st.header(f"{selected_player} - {season} Season")

    # --- SHOT CHART ---
    try:
        shot_profile = get_player_shot_profile(df_shooting, selected_player, season, league_avg_df)
        fig = plot_shot_chart(shot_profile, selected_player, season)
        st.subheader("Shot Profile vs League Average")
        st.pyplot(fig)
    except ValueError as e:
        st.warning(str(e))

    # --- SIMILAR PLAYERS ---
    st.subheader("Most Similar Players This Season")
    sim_result = find_similar_players(selected_player, season)
    if isinstance(sim_result, str):
        st.error(sim_result)
    else:
        st.dataframe(sim_result)
else:
    st.info("Select a player and season, then click 'Generate Profile'.")
