import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st



# Load and clean the primary data (Per 100 Poss)
df_main = pd.read_csv("data/Per 100 Poss.csv")
df_main = df_main[df_main['season'] >= 1997].copy()
df_main.drop(columns=['birth_year'], inplace=True, errors='ignore')

# Load and clean Player Shooting data
df_shooting = pd.read_csv("data/Player Shooting.csv")
df_shooting.drop(columns=['season', 'player_id', 'player', 'pos', 'age', 'experience', 'lg', 'tm', 'fg_percent', 'birth_year'], errors='ignore', inplace=True)
df_shooting.fillna(0, inplace=True)

# Merge shooting data on seas_id
df = df_main.merge(df_shooting, on='seas_id', how='left')
df.fillna(0, inplace=True)

# Identity columns (non-numeric, metadata)
identity_cols = [
    'seas_id', 'season', 'player_id', 'player', 'pos',
    'age', 'experience', 'lg', 'tm'
]

# Keep only numeric stat columns (exclude identity)
numeric_cols = [col for col in df.select_dtypes(include=[np.number]).columns if col not in identity_cols]

# Fill missing numeric values
df[numeric_cols] = df[numeric_cols].fillna(0)

# Final assembled DataFrame
df = df[identity_cols + numeric_cols].copy()
df = df.loc[:, ~df.columns.duplicated()]
df = df.reset_index(drop=True)

# Scale numeric features
features = df[numeric_cols].values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

weights_by_stat = {
    # === Role and Output (Tier 1: 3.0) ===
    'pts_per_100_poss': 3.0,
    'ast_per_100_poss': 3.0,
    'x3pa_per_100_poss': 3.0,
    'o_rtg': 3.0,

    # === Efficiency (Tier 2: 2.0) ===
    'fg_percent': 2.0,
    'x3p_percent': 2.0,
    'ft_percent': 2.0,
    'd_rtg': 2.0,
    'fg_percent_from_x2p_range': 2.0,
    'fg_percent_from_x3p_range': 2.0,

    # === Shot Location Profile (Tier 2–1.5) ===
    'avg_dist_fga': 2.0,
    'percent_fga_from_x3p_range': 2.0,
    'percent_fga_from_x0_3_range': 1.5,
    'percent_fga_from_x3_10_range': 1.5,
    'percent_fga_from_x10_16_range': 1.5,
    'percent_fga_from_x16_3p_range': 1.5,
    'percent_assisted_x3p_fg': 1.5,
    'percent_assisted_x2p_fg': 1.5,
    'percent_corner_3s_of_3pa': 1.5,
    'corner_3_point_percent': 1.5,

    # === Style Context / Usage (Tier 1.5) ===
    'fga_per_100_poss': 1.5,
    'fta_per_100_poss': 1.5,
    'orb_per_100_poss': 1.5,
    'drb_per_100_poss': 1.5,
    'trb_per_100_poss': 1.5,
    'pf_per_100_poss': 1.5,
    'mp': 1.5,
    'g': 1.5,
    'gs': 1.5,

    # === Defensive Contribution (Tier 2) ===
    'stl_per_100_poss': 2.0,
    'blk_per_100_poss': 2.0,
    'tov_per_100_poss': 2.0,

    # === Redundant or Support Stats (Tier 1.0) ===
    'fg_per_100_poss': 1.0,
    'x3p_per_100_poss': 1.0,
    'x2p_per_100_poss': 1.0,
    'x2pa_per_100_poss': 1.0,
    'x2p_percent': 1.0,
    'fg_percent_from_x0_3_range': 1.0,
    'fg_percent_from_x3_10_range': 1.0,
    'fg_percent_from_x10_16_range': 1.0,
    'fg_percent_from_x16_3p_range': 1.0,

    # === Rare/Quirky (Tier 0.5–1.0) ===
    'percent_dunks_of_fga': 0.5,
    'num_of_dunks': 1.0,
    'num_heaves_attempted': 0.05,
    'num_heaves_made': 0.05
}

# Apply weights
weights = np.ones(len(numeric_cols))
for i, col in enumerate(numeric_cols):
    weights[i] = weights_by_stat.get(col, 1.0)

features_weighted = features_scaled * weights
similarity_matrix = cosine_similarity(features_weighted)

# Player similarity function
def find_similar_players(player_name, season, top_n=10):
    idx = df[(df['player'] == player_name) & (df['season'] == season)].index
    if len(idx) == 0:
        return f"No data for {player_name} in {season}"
    idx = idx[0]

    scores = similarity_matrix[idx]
    top_indices = np.argsort(scores)[::-1][1:top_n+1]

    result_df = df.iloc[top_indices][['player', 'season', 'tm']].copy()
    result_df['similarity'] = scores[top_indices]

    return result_df

__all__ = ['df', 'find_similar_players']

def load_shooting_data(file_path="data/Player Shooting.csv"):
    return pd.read_csv(file_path)

def load_league_averages(file_path="data/League Average Shooting.csv"):
    return pd.read_csv(file_path).set_index("Season")

@st.cache_data
def load_basic_stats():
    per_game = pd.read_csv("../data/Player Per Game.csv")
    per_100 = pd.read_csv("../data/Per 100 Poss.csv")
    totals = pd.read_csv("../data/Player Totals.csv")
    return per_game, per_100, totals

@st.cache_data
def load_award_data():
    all_star = pd.read_csv("../data/All-Star Selections.csv")
    eos_teams = pd.read_csv("../data/End of Season Teams.csv")
    award_shares = pd.read_csv("../data/Player Award Shares.csv")
    career_info = pd.read_csv("../data/Player Career Info.csv")
    return all_star, eos_teams, award_shares, career_info

def get_player_shot_profile(df, player_name, season, league_avg_df):
    df_player = df[(df["player"] == player_name) & (df["season"] == season)]
    if df_player.empty:
        raise ValueError(f"No data found for {player_name} in {season} season.")
    
    row = df_player.iloc[0]
    league_row = league_avg_df.loc[season]

    zones = [
        ("0–3 ft", "fg_percent_from_x0_3_range"),
        ("3–10 ft", "fg_percent_from_x3_10_range"),
        ("10–16 ft", "fg_percent_from_x10_16_range"),
        ("16 ft – 3PT", "fg_percent_from_x16_3p_range"),
        ("Corner 3", "corner_3_point_percent"),
        ("Non-Corner 3", "fg_percent_from_x3p_range"),
    ]

    corner_3_pct = row["percent_corner_3s_of_3pa"] * row["percent_fga_from_x3p_range"] * 100
    non_corner_3_pct = (row["percent_fga_from_x3p_range"] * 100) - corner_3_pct

    shot_zones = {}
    for label, col in zones:
        player_fg = row[col] * 100
        league_fg = league_row[col] * 100
        fga_pct = (
            corner_3_pct if label == "Corner 3"
            else non_corner_3_pct if label == "Non-Corner 3"
            else row["percent_fga_from_" + col.split("_from_")[1]] * 100
        )
        diff = player_fg - league_fg
        shot_zones[label] = (fga_pct, player_fg, diff)

    return shot_zones

def plot_shot_chart(shot_zones, player_name, season):
    labels = list(shot_zones.keys())
    fga_pct = [v[0] for v in shot_zones.values()]
    fg_pct = [v[1] for v in shot_zones.values()]
    diff = [v[2] for v in shot_zones.values()]

    # Normalize difference for color mapping
    max_diff = max(abs(min(diff)), abs(max(diff)), 1e-6)
    norm_diff = [d / max_diff for d in diff]
    colors = [plt.cm.RdYlGn((d + 1) / 2) for d in norm_diff]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(labels, fga_pct, color=colors)
    ax.set_xlabel("% of Field Goal Attempts")
    ax.set_title(f"{player_name} vs League Avg ({season})")

    for bar, fg, d in zip(bars, fg_pct, diff):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{fg:.1f}% ({'+' if d >= 0 else ''}{d:.1f}%)", va='center')

    ax.set_xlim(0, max(fga_pct) + 10)
    plt.tight_layout()
    return fig

def display_awards_and_honors(selected_player, selected_season, all_star_df, eos_teams_df, award_shares_df, career_info_df):
    def ordinal(n):
        if 10 <= n % 100 <= 20:
            suffix = "th"
        else:
            suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
        return f"{n}{suffix}"

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
        award_season_df = award_shares_df[
            (award_shares_df["season"] == row["season"]) & 
            (award_shares_df["award"] == row["award"])
        ].sort_values(by="pts_won", ascending=False).reset_index(drop=True)

        player_rank = (
            award_season_df[award_season_df["player"] == selected_player].index[0] + 1
            if selected_player in award_season_df["player"].values else None
        )

        if row['winner'] == "TRUE":
            banner = f"{award_name} Winner 🏆"
        else:
            banner = f"{award_name}: {ordinal(player_rank)} Place ({round(row['share'] * 100, 1)}% Vote Share)"
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
                {banner}
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