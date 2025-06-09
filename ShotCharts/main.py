import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def load_shooting_data(file_path="../data/Player Shooting.csv"):
    return pd.read_csv(file_path)

def load_league_averages(file_path="../data/League Average Shooting.csv"):
    return pd.read_csv(file_path).set_index("Season")

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





