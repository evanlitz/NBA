import streamlit as st
import pandas as pd

# Load all stat types
@st.cache_data
def load_stats():
    per_game = pd.read_csv("../data/Player Per Game.csv")
    per_100 = pd.read_csv("../data/Per 100 Poss.csv")
    totals = pd.read_csv("../data/Player Totals.csv")
    return per_game, per_100, totals

per_game_df, per_100_df, totals_df = load_stats()

# Combine player list and year range
all_players = sorted(set(per_game_df["player"].dropna()))
all_seasons = sorted(per_game_df["season"].unique(), reverse=True)

# Sidebar Inputs
st.title("📊 NBA Stat Presenter")

selected_player = st.selectbox("Select Player", all_players, index=all_players.index("LeBron James") if "LeBron James" in all_players else 0)
selected_season = st.selectbox("Select Season", all_seasons)
view_mode = st.radio("Stat View Mode", ["Per Game", "Per 100 Possessions", "Total"])

# Choose correct dataset
if view_mode == "Per Game":
    stat_df = per_game_df
elif view_mode == "Per 100 Possessions":
    stat_df = per_100_df
else:
    stat_df = totals_df

# --- Filter player and season ---
filtered = stat_df[(stat_df["player"] == selected_player) & (stat_df["season"] == selected_season)]

if filtered.empty:
    st.error("No stats available for this player in that season.")
else:
    st.subheader(f"{selected_player} — {selected_season} Season ({view_mode})")

    priority_stats = [
    "pts", "ast", "trb", "stl", "blk", "tov",  
    "fg", "fga", "fg_percent",
    "x3p", "x3pa", "x3p_percent",
    "ft", "fta", "ft_percent",
    "orb", "drb", "pf", "mp", "g", "gs"
]

    stats = filtered.iloc[0]

    # Show only numeric stats (including g, gs, mp)
    numeric_stats = stats.drop(labels=["seas_id", "player_id", "season"], errors="ignore")
    numeric_stats = numeric_stats.apply(pd.to_numeric, errors="coerce").dropna()
    # Display in labeled metric boxes
    cols = st.columns(4)
    for i, (stat, value) in enumerate(numeric_stats.items()):
        with cols[i % 4]:
            st.metric(label=stat.replace("_", " ").title(), value=round(value, 2))
