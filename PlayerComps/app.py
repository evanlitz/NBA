import streamlit as st
from main import df, find_similar_players

player_list = sorted(df['player'].unique())
st.title("NBA Player Similarity Finder")

selected_player = st.selectbox("Select a player", player_list)
season = st.number_input("Select season", min_value=1976, max_value=2025, value=2023)

if st.button("Find Similar Players"):
    result = find_similar_players(selected_player, season)
    if isinstance(result, str):
        st.error(result)
    else:
        st.dataframe(result)
