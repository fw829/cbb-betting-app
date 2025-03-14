import streamlit as st
import sqlite3
import pandas as pd

# ✅ Database Path
DB_PATH = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\basketball_data.db"

# ✅ Define Offense-Defense stat pairs
STAT_PAIRS = {
    "AdjOE": "AdjDE",
    "FG2Pct": "OppFG2Pct",
    "FG3Pct": "OppFG3Pct",
    "ARate": "OppARate"
}

# ✅ Load data from the database
@st.cache_data
def get_data(filters, paired_filters):
    conn = sqlite3.connect(DB_PATH)

    # ✅ Base Query
    query = """
        SELECT g1.GAME_ID, g1.TEAM, g1.AdjOE, g1.AdjDE, g1.FG2Pct, g1.FG3Pct, g1.ARate, g1.AdjTempo,
               g2.TEAM AS Opponent, g2.AdjDE AS OppAdjDE, g2.OppFG2Pct, g2.OppFG3Pct, g2.OppARate
        FROM games g1
        JOIN games g2 ON g1.GAME_ID = g2.GAME_ID
        WHERE g1.TEAM <> g2.TEAM
    """

    # ✅ Apply Filters (Standard Sliders)
    conditions = []
    for stat, value in filters.items():
        conditions.append(f"g1.{stat} BETWEEN {value[0]} AND {value[1]}")

    # ✅ Apply Opponent Filters (If Enabled)
    for stat, value in paired_filters.items():
        conditions.append(f"g2.{stat} BETWEEN {value[0]} AND {value[1]}")

    # ✅ Add Conditions to SQL Query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ✅ Streamlit UI
st.title("College Basketball Betting Analysis")

# ✅ Create Sliders for Filtering
filters = {}
paired_filters = {}

st.sidebar.header("Filter Options")

# ✅ Standard Filters
for stat in ["AdjOE", "AdjDE", "FG2Pct", "FG3Pct", "ARate", "AdjTempo"]:
    filters[stat] = st.sidebar.slider(f"{stat} Range", 50.0, 150.0, (90.0, 110.0))

# ✅ Paired Offense-Defense Filters (With Checkbox)
st.sidebar.header("Opponent Matchup Filters")
for off_stat, def_stat in STAT_PAIRS.items():
    enable_pair = st.sidebar.checkbox(f"Enable {off_stat} vs. {def_stat} Filter")
    if enable_pair:
        paired_filters[def_stat] = st.sidebar.slider(f"{def_stat} Range", 50.0, 150.0, (90.0, 110.0))

# ✅ Load Data With Filters
df = get_data(filters, paired_filters)

# ✅ Display Data
st.write("### Filtered Data")
st.dataframe(df)

# ✅ Visualization (Example: AdjOE vs. OppAdjDE)
if not df.empty:
    st.write("### Visualization: AdjOE vs. OppAdjDE")
    st.scatter_chart(df[["AdjOE", "OppAdjDE"]])