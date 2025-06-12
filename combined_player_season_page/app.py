import streamlit as st
import pandas as pd
from collections import defaultdict
from main import (
    df,  # season similarity df
    find_similar_players,  # similarity logic
    load_shooting_data,
    load_league_averages,
    get_player_shot_profile,
    plot_shot_chart,
    load_award_data,
    load_basic_stats,
    display_awards_and_honors
)

category_map_per_game = {
    "🏀 Scoring": ["pts_per_game", "fg_per_game", "fga_per_game", "fg_percent", "ft_per_game", "fta_per_game", "ft_percent"],
    "🎯 3PT Shooting": ["x3p_per_game", "x3pa_per_game", "x3p_percent"],
    "💥 Inside Game": ["x2p_per_game", "x2pa_per_game", "x2p_percent", "e_fg_percent"],
    "🎨 Playmaking": ["ast_per_game", "tov_per_game"],
    "🛡️ Defense": ["stl_per_game", "blk_per_game", "pf_per_game"],
    "🧱 Rebounding": ["orb_per_game", "drb_per_game", "trb_per_game"],
    "🧭 Context": ["mp_per_game", "g", "gs"]
}
category_map_per_100 = {
    "🏀 Scoring": ["pts_per_100_poss", "fg_per_100_poss", "fga_per_100_poss", "fg_percent", "ft_per_100_poss", "fta_per_100_poss", "ft_percent"],
    "🎯 3PT Shooting": ["x3p_per_100_poss", "x3pa_per_100_poss", "x3p_percent"],
    "💥 Inside Game": ["x2p_per_100_poss", "x2pa_per_100_poss", "x2p_percent"],
    "🎨 Playmaking": ["ast_per_100_poss", "tov_per_100_poss", "o_rtg"],
    "🛡️ Defense": ["stl_per_100_poss", "blk_per_100_poss", "pf_per_100_poss", "d_rtg"],
    "🧱 Rebounding": ["orb_per_100_poss", "drb_per_100_poss", "trb_per_100_poss"],
    "🧭 Context": ["mp", "g", "gs"]
}
category_map_totals = {
    "🏀 Scoring": ["pts", "fg", "fga", "fg_percent", "ft", "fta", "ft_percent"],
    "🎯 3PT Shooting": ["x3p", "x3pa", "x3p_percent"],
    "💥 Inside Game": ["x2p", "x2pa", "x2p_percent"],
    "🎨 Playmaking": ["ast", "tov"],
    "🛡️ Defense": ["stl", "blk", "pf"],
    "🧱 Rebounding": ["orb", "drb", "trb"],
    "🧭 Context": ["mp", "g", "gs"]
}

# Page setup
st.set_page_config(page_title="NBA Player Explorer", layout="wide")
st.title("NBA Player Season Explorer")

def section_header(title):
    st.markdown(f"""
    <h3 style='margin-top: 30px; color: #004080; border-bottom: 2px solid #cccccc; padding-bottom: 5px;'>
        {title}
    </h3>
    """, unsafe_allow_html=True)



# Load data
@st.cache_data
def load_all_data():
    df_shooting = load_shooting_data()
    league_avg = load_league_averages()
    return df_shooting, league_avg

df_shooting, league_avg_df = load_all_data()
per_game_df, per_100_df, totals_df = load_basic_stats()
all_star_df, eos_teams_df, award_shares_df, career_info_df = load_award_data()

if "last_player" not in st.session_state:
    st.session_state.last_player = None
    st.session_state.last_season = None
    st.session_state.profile_loaded = False

if "last_view_mode" not in st.session_state:
    st.session_state.last_view_mode = None

# Sidebar: Player & Season Selector
st.sidebar.header("Select Player and Season")
players = sorted(df["player"].unique())
selected_player = st.sidebar.selectbox("Player", players)
season = st.sidebar.number_input("Season", min_value=1996, max_value=2025, value=2025)
view_mode = st.sidebar.radio("Stat View Mode", ["Per Game", "Per 100 Possessions", "Total"])


triggered = st.sidebar.button("Generate Profile")

if triggered or (
    st.session_state.profile_loaded and
    selected_player == st.session_state.last_player and
    season == st.session_state.last_season and
    view_mode != st.session_state.last_view_mode
):

    st.session_state.last_player = selected_player
    st.session_state.last_season = season
    st.session_state.profile_loaded = True
    st.session_state.last_view_mode = view_mode


    st.header(f"{selected_player} - {season} Season")

    # === STAT DISPLAY ===
    if view_mode == "Per Game":
        stat_df = per_game_df
        category_map = category_map_per_game
        # priority_stats = [
        #     "pts_per_game", "ast_per_game", "trb_per_game",
        #     "stl_per_game", "blk_per_game", "tov_per_game",
        #     "fg_per_game", "fga_per_game", "fg_percent",
        #     "x3p_per_game", "x3pa_per_game", "x3p_percent",
        #     "x2p_per_game", "x2pa_per_game", "x2p_percent",
        #     "ft_per_game", "fta_per_game", "ft_percent",
        #     "e_fg_percent", "orb_per_game", "drb_per_game",
        #     "pf_per_game", "mp_per_game", "g", "gs"
        # ]
    elif view_mode == "Per 100 Possessions":
        stat_df = per_100_df
        category_map = category_map_per_100
        # priority_stats = [
        #     "pts_per_100_poss", "ast_per_100_poss", "trb_per_100_poss",
        #     "stl_per_100_poss", "blk_per_100_poss", "tov_per_100_poss",
        #     "fg_per_100_poss", "fga_per_100_poss", "fg_percent",
        #     "x3p_per_100_poss", "x3pa_per_100_poss", "x3p_percent",
        #     "x2p_per_100_poss", "x2pa_per_100_poss", "x2p_percent",
        #     "ft_per_100_poss", "fta_per_100_poss", "ft_percent",
        #     "orb_per_100_poss", "drb_per_100_poss", "pf_per_100_poss",
        #     "o_rtg", "d_rtg", "mp", "g", "gs"
        # ]
    else:
        stat_df = totals_df
        category_map = category_map_totals
        # priority_stats = [
        #     "pts", "ast", "trb", "stl", "blk", "tov",
        #     "fg", "fga", "fg_percent",
        #     "x3p", "x3pa", "x3p_percent",
        #     "ft", "fta", "ft_percent",
        #     "orb", "drb", "pf", "mp", "g", "gs"
        # ]

    filtered = stat_df[(stat_df["player"] == selected_player) & (stat_df["season"] == season)]
    if not filtered.empty:
        stats = filtered.iloc[0]
        numeric_stats = stats.drop(labels=["seas_id", "player_id", "season"], errors="ignore")
        numeric_stats = numeric_stats.apply(pd.to_numeric, errors="coerce").dropna()
        st.subheader(f"{selected_player} — {season} Season ({view_mode})")

        grouped_stats = defaultdict(list)
        for stat, value in numeric_stats.items():
            for category, stats in category_map.items():
                if stat in stats:
                    grouped_stats[category].append((stat, value))
                    break

        for category, stats in grouped_stats.items():
            with st.container():
                st.markdown(f"#### {category}")
                st.markdown("""
                <div style='
                    background-color: #f8f9fa;
                    padding: 8px 10px;
                    border-radius: 8px;
                    margin-bottom: 12px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.08);
                '>
                """, unsafe_allow_html=True)
                cols = st.columns(len(stats) if len(stats) < 4 else 4)
                for i, (stat, value) in enumerate(stats):
                    with cols[i % 4]:
                        st.metric(stat.replace("_", " ").title(), round(value, 2))
                st.markdown("</div>", unsafe_allow_html=True)

    # Only load the rest once
    if st.session_state.profile_loaded:
        display_awards_and_honors(selected_player, season, all_star_df, eos_teams_df, award_shares_df, career_info_df)

        try:
            shot_profile = get_player_shot_profile(df_shooting, selected_player, season, league_avg_df)
            fig = plot_shot_chart(shot_profile, selected_player, season)
            section_header("📊 Shot Profile vs League Average 📊")
            st.pyplot(fig)
        except ValueError as e:
            st.warning(str(e))

        section_header("🔎 Most Similar Players This Season 🔎")
        sim_result = find_similar_players(selected_player, season)
        if isinstance(sim_result, str):
            st.error(sim_result)
        else:
            st.dataframe(sim_result)
else:
    st.info("Select a player and season, then click 'Generate Profile'.")

