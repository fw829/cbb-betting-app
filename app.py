import streamlit as st
import pandas as pd
import sqlite3
import os

# Display current working directory for debugging
st.write("Current working directory:", os.getcwd())

# Set database path
DB_PATH = r"C:\\Users\\Frank W\\OneDrive\\Desktop\\College Basketball Wagering\\Database\\basketball_data.db"

# Define database connection function
def get_db_connection():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        return conn
    except Exception as e:
        st.error(f"❌ Database Connection Failed: {e}")
        return None

# Define stat pairs for Offense vs Defense comparison
STAT_PAIRS = {
    "AdjOE": "AdjDE",
    "FG2Pct": "OppFG2Pct",
    "FG3Pct": "OppFG3Pct",
    "ARate": "OppARate"
}

# Sidebar filters
filters = {}
paired_filters = {}

# Standard Filters (Team Stats)
st.sidebar.header("Filter Team Stats")
for stat in ["AdjOE", "AdjDE", "FG2Pct", "FG3Pct", "ARate", "AdjTempo"]:
    filters[stat] = st.sidebar.slider(f"{stat} Range", 50.0, 150.0, (90.0, 110.0), key=f"slider_{stat}")

# Paired Filters (Opponent Stats)
st.sidebar.header("Opponent Comparison")
for off_stat, def_stat in STAT_PAIRS.items():
    enable_pair = st.sidebar.checkbox(f"Enable {off_stat} vs. {def_stat} Filter", key=f"checkbox_{off_stat}")
    if enable_pair:
        paired_filters[def_stat] = st.sidebar.slider(f"{def_stat} Range", 50.0, 150.0, (90.0, 110.0), key=f"slider_{def_stat}")

# Function to load data based on filters
def get_data(filters, paired_filters):
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()
    
    query = f"""
        SELECT g1.GAME_ID, g1.TEAM, g1.AdjOE, g1.AdjDE, g1.FG2Pct, g1.FG3Pct, g1.ARate, g1.AdjTempo,
               g2.TEAM AS Opponent, g2.AdjDE AS OppAdjDE, g2.FG2Pct AS OppFG2Pct, g2.FG3Pct AS OppFG3Pct, g2.ARate AS OppARate
        FROM games g1
        JOIN games g2 ON g1.GAME_ID = g2.GAME_ID
        WHERE g1.TEAM <> g2.TEAM
    """

    # Apply filters dynamically
    for stat, value in filters.items():
        query += f" AND g1.{stat} BETWEEN {value[0]} AND {value[1]}"
    for stat, value in paired_filters.items():
        query += f" AND g2.{stat} BETWEEN {value[0]} AND {value[1]}"
    
    try:
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"🚨 SQL Query Failed: {e}")
        st.write(f"🔎 Query that caused the error: {query}")
        return pd.DataFrame()

# Load data
st.write("### Filtered Data View")
df = get_data(filters, paired_filters)
st.dataframe(df)
