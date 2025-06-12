import streamlit as st
import pandas as pd

# Load all stat types

def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

@st.cache_data
def load_stats():
    per_game = pd.read_csv("../data/Player Per Game.csv")
    per_100 = pd.read_csv("../data/Per 100 Poss.csv")
    totals = pd.read_csv("../data/Player Totals.csv")
    return per_game, per_100, totals

@st.cache_data
def load_honors():
    all_star = pd.read_csv("../data/All-Star Selections.csv")
    eos_teams = pd.read_csv("../data/End of Season Teams.csv")  # Use this for honors, not the Voting one
    award_shares = pd.read_csv("../data/Player Award Shares.csv")
    career_info = pd.read_csv("../data/Player Career Info.csv")
    return all_star, eos_teams, award_shares, career_info

all_star_df, eos_teams_df, award_shares_df, career_info_df = load_honors()



per_game_df, per_100_df, totals_df = load_stats()

# Combine player list and year range
all_players = sorted(set(per_game_df["player"].dropna()))
all_seasons = sorted(per_game_df["season"].unique(), reverse=True)

# Sidebar Inputs
st.title("📊 NBA Stat Presenter")

selected_player = st.selectbox("Select Player", all_players, index=all_players.index("LeBron James") if "LeBron James" in all_players else 0)
selected_season = st.selectbox("Select Season", all_seasons)
view_mode = st.radio("Stat View Mode", ["Per Game", "Per 100 Possessions", "Total"])

# Filter honors
is_all_star = not all_star_df[
    (all_star_df["player"] == selected_player) &
    (all_star_df["season"] == selected_season)
].empty

season_honors = eos_teams_df[
    (eos_teams_df["player"] == selected_player) &
    (eos_teams_df["season"] == selected_season)
]

season_awards = award_shares_df[
    (award_shares_df["player"] == selected_player) &
    (award_shares_df["season"] == selected_season)
]

hof_status = career_info_df[
    (career_info_df["player"].str.lower() == selected_player.lower())
]

is_hof = not hof_status.empty and hof_status.iloc[0]["hof"] == True

# Choose correct dataset
if view_mode == "Per Game":
    stat_df = per_game_df
    priority_stats = [
    "pts_per_game", "ast_per_game", "trb_per_game",
    "stl_per_game", "blk_per_game", "tov_per_game",
    "fg_per_game", "fga_per_game", "fg_percent",
    "x3p_per_game", "x3pa_per_game", "x3p_percent",
    "x2p_per_game", "x2pa_per_game", "x2p_percent",
    "ft_per_game", "fta_per_game", "ft_percent", "e_fg_percent", "orb_per_game", "drb_per_game", "pf_per_game", "mp_per_game", "g", "gs",
]

elif view_mode == "Per 100 Possessions":
    stat_df = per_100_df
    priority_stats = [
        "pts_per_100_poss", "ast_per_100_poss", "trb_per_100_poss",
        "stl_per_100_poss", "blk_per_100_poss", "tov_per_100_poss",
        "fg_per_100_poss", "fga_per_100_poss", "fg_percent",
        "x3p_per_100_poss", "x3pa_per_100_poss", "x3p_percent",
        "x2p_per_100_poss", "x2pa_per_100_poss", "x2p_percent",
        "ft_per_100_poss", "fta_per_100_poss", "ft_percent",
        "orb_per_100_poss", "drb_per_100_poss", "pf_per_100_poss",
        "o_rtg", "d_rtg", "mp", "g", "gs"
    ]
else:
    stat_df = totals_df
    priority_stats = [
        "pts", "ast", "trb", "stl", "blk", "tov",  
        "fg", "fga", "fg_percent",
        "x3p", "x3pa", "x3p_percent",
        "ft", "fta", "ft_percent",
        "orb", "drb", "pf", "mp", "g", "gs"
    ]

# --- Filter player and season ---
filtered = stat_df[(stat_df["player"] == selected_player) & (stat_df["season"] == selected_season)]

if filtered.empty:
    st.error("No stats available for this player in that season.")
else:
    st.subheader(f"{selected_player} — {selected_season} Season ({view_mode})")

    stats = filtered.iloc[0]

    # Show only numeric stats (including g, gs, mp)
    numeric_stats = stats.drop(labels=["seas_id", "player_id", "season"], errors="ignore")
    numeric_stats = numeric_stats.apply(pd.to_numeric, errors="coerce").dropna()
    
    ordered_stats = [(stat, numeric_stats.pop(stat)) for stat in priority_stats if stat in numeric_stats]
    ordered_stats_df = pd.Series(dict(ordered_stats))
    numeric_stats = pd.concat([ordered_stats_df, numeric_stats])


    # Display in labeled metric boxes
    cols = st.columns(4)
    for i, (stat, value) in enumerate(numeric_stats.items()):
        with cols[i % 4]:
            st.metric(label=stat.replace("_", " ").title(), value=round(value, 2))


    st.markdown("### 🏅 Awards & Honors")

    if is_all_star:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, gold, goldenrod);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: black;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 16px;
        ">
            All-Star Selection ⭐
        </div>
        """, unsafe_allow_html=True)


    for _, row in season_honors.iterrows():
        honor_text = f"{row['type']} {row['number_tm']} Team"
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, gold, goldenrod);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: black;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 16px;
        ">
        {honor_text}
        </div>
        """, unsafe_allow_html=True)


    for _, row in season_awards.iterrows():
        award_name = row['award'].upper()
        season = row['season']

        # Get all players for this award & season
        award_season_df = award_shares_df[
        (award_shares_df["season"] == season) & (award_shares_df["award"] == row["award"])
        ].sort_values(by="pts_won", ascending=False).reset_index(drop=True)

        # Rank placement (1-based)
        player_rank = (
            award_season_df[award_season_df["player"] == selected_player].index[0] + 1
            if selected_player in award_season_df["player"].values else None
        )

        if row['winner'] == "TRUE":
            banner_text = f"{award_name} Winner 🏆"
        else:
            banner_text = f"{award_name}: {ordinal(player_rank)} Place ({round(row['share'] * 100, 1)}% Vote Share)"

        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, gold, goldenrod);
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
            color: black;
            margin-top: 10px;
            margin-bottom: 10px;
            font-size: 16px;
        ">
            {banner_text}
        </div>
        """, unsafe_allow_html=True)

    if is_hof:
        st.markdown(f"""
        <div style="
        background: linear-gradient(90deg, #ffd700, #ffcc00);
        padding: 12px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        color: black;
        margin-bottom: 15px;
        font-size: 18px;
        border: 2px solid #b8860b;
        box-shadow: 0px 0px 10px rgba(218,165,32,0.6);
    ">
        🏛️ Hall of Fame Inductee
    </div>
    """, unsafe_allow_html=True)
