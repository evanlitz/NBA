import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Load and clean the data
df = pd.read_csv("../data/Per 100 Poss.csv")
df = df.drop(columns=['birth_year'], errors='ignore')  # Drop unused column

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
df = df.loc[:, ~df.columns.duplicated()]  # Remove any duplicate columns
df = df.reset_index(drop=True)

# Scale numeric features
features = df[numeric_cols].values
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# === Weight important stats ===
weights_by_stat = {
    'pts_per_100_poss': 3.0,
    'ast_per_100_poss': 3.0,
    'x3pa_per_100_poss': 3.0,
    'o_rtg': 3.0,

    'fg_percent': 2.0,
    'x3p_percent': 2.0,
    'ft_percent': 2.0,
    'trb_per_100_poss': 2.0,
    'stl_per_100_poss': 2.0,
    'blk_per_100_poss': 2.0,
    'tov_per_100_poss': 2.0,
    'd_rtg': 2.0,

    'fga_per_100_poss': 1.5,
    'fta_per_100_poss': 1.5,
    'orb_per_100_poss': 1.5,
    'drb_per_100_poss': 1.5,
    'pf_per_100_poss': 1.5,
    'mp': 1.5,
    'g': 1.5,
    'gs': 1.5,

    'fg_per_100_poss': 1.0,
    'x3p_per_100_poss': 1.0,
    'x2p_per_100_poss': 1.0,
    'x2pa_per_100_poss': 1.0,
    'x2p_percent': 1.0,
}

# Apply weights
weights = np.ones(len(numeric_cols))
for i, col in enumerate(numeric_cols):
    weights[i] = weights_by_stat.get(col, 1.0)

features_weighted = features_scaled * weights
similarity_matrix = cosine_similarity(features_weighted)

# Player similarity function
def find_similar_players(player_name, season, top_n=5):
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
