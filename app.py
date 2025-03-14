import streamlit as st
import sqlite3
import pandas as pd
import os

# ✅ Database Path
DB_PATH = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\basketball_data.db"

# ✅ Define Offense-Defense stat pairs
STAT_PAIRS = {
    "AdjOE": "AdjDE",
    "FG2Pct": "OppFG2Pct",
    "FG3Pct": "OppFG3Pct",
    "ARate": "OppARate"
}

# ✅ Check if database exists
if not os.path.exists(DB_PATH):
    st.error("❌ Database file NOT FOUND. Ensure it's in the correct location.")
    st.stop()

# ✅ Load data from the database
@st.cache_data
def get_data(filters, paired_filters):
    conn = sqlite3.connect(DB_PATH)

    # ✅ Base Query
    query = """
        SELECT g1.GAME_ID, g1.TEAM, g1.AdjOE, g1.AdjDE, g1.FG2Pct, g1.FG3Pct, g1.ARate, g1.AdjTempo,
               g2.TEAM AS Opponent, g2.AdjDE AS OppAdjDE, g2.FG2Pct AS OppFG2Pct, g2.FG3Pct AS OppFG3Pct, g2.ARate AS OppARate
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
        if stat in ["AdjDE", "OppFG2Pct", "OppFG3Pct", "OppARate"]:  # Ensure the column exists
            conditions.append(f"g2.{stat} BETWEEN {value[0]} AND {value[1]}")

    # ✅ Add Conditions to SQL Query
    if conditions:
        query += " AND " + " AND ".join(conditions)

    print("🔎 Executing SQL Query:", query)  # Debugging Output

    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"🚨 SQL Query Failed: {e}")
        st.write(f"🔎 Query that caused the error: ```{query}```")  # Show query in Streamlit UI
        df = pd.DataFrame()  # Return an empty DataFrame on failure
    finally:
        conn.close()

    return df


# ✅ Streamlit UI
st.title("College Basketball Betting Analysis")

# ✅ Sidebar Header
st.sidebar.header("Filter Options")

# ✅ Define reasonable default ranges for filters
FILTER_DEFAULTS = {
    "AdjOE": (80.0, 120.0),
    "AdjDE": (85.0, 115.0),
    "FG2Pct": (40.0, 65.0),
    "FG3Pct": (25.0, 45.0),
    "ARate": (10.0, 30.0),
    "AdjTempo": (50.0, 80.0),
}

# ✅ Initialize Filters
filters = {}
paired_filters = {}

# ✅ Standard Filters (Team Stats)
for stat, default_range in FILTER_DEFAULTS.items():
    slider_key = f"slider_{stat}"
    filters[stat] = st.sidebar.slider(f"{stat} Range", default_range[0], default_range[1], default_range, key=slider_key)

# ✅ Opponent Filters (Only appear if enabled)
for i, (off_stat, def_stat) in enumerate(STAT_PAIRS.items()):
    enable_pair = st.sidebar.checkbox(f"Enable {off_stat} vs. {def_stat} Filter", key=f"checkbox_pair_{i}")
    if enable_pair:
        slider_key = f"slider_{def_stat}_opponent"  # ✅ Ensure uniqueness
        paired_filters[def_stat] = st.sidebar.slider(
            f"{def_stat} (Opponent) Range", FILTER_DEFAULTS[off_stat][0], FILTER_DEFAULTS[off_stat][1], FILTER_DEFAULTS[off_stat], key=slider_key
        )

# ✅ Load Data With Filters
df = get_data(filters, paired_filters)

# ✅ Display Data
st.write("### Filtered Data")
st.dataframe(df)

# ✅ Visualization (Example: AdjOE vs. OppAdjDE)
if not df.empty:
    st.write("### Visualization: AdjOE vs. OppAdjDE")
    st.scatter_chart(df[["AdjOE", "OppAdjDE"]])
