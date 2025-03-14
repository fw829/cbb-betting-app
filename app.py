import os
import sqlite3
import streamlit as st
import matplotlib.pyplot as plt

# Set the correct database path
db_path = os.path.join(os.getcwd(), "basketball_data.db")

# Debugging: Print the database path
if not os.path.exists(db_path):
    st.error(f"🚨 Database file not found at: {db_path}")
else:
    st.write(f"✅ Connected to database: {db_path}")

# Now, create the connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()



# Define available stat pairs for Offense vs. Defense comparisons
stat_pairs = {
    "AdjOE": "AdjDE",
    "FG2Pct": "OppFG2Pct",
    "FG3Pct": "OppFG3Pct",
    "ARate": "OppARate"
}

# Define stats that should be filterable even if not part of a pair
filterable_stats = ["AdjOE", "AdjDE", "FG2Pct", "FG3Pct", "OppFG2Pct", "OppFG3Pct"]

# Function to fetch data with or without Offense-Defense comparisons
@st.cache_data
def get_data(compare_vs_opponent, selected_stat, filters):
    conn = sqlite3.connect("basketball_data.db")

    # Determine if selected_stat has a defensive pair
    opponent_stat = stat_pairs.get(selected_stat, None)

    if not compare_vs_opponent or opponent_stat is None:
        query = f"""
            SELECT GAME_ID, TEAM, {selected_stat}, CLOSING_SPREAD, Covered_Spread
            FROM games
            WHERE 1=1
        """
    else:
        query = f"""
            SELECT g1.GAME_ID, g1.TEAM, g1.{selected_stat} AS Team_Stat, 
                   g2.TEAM AS Opponent, g2.{opponent_stat} AS Opponent_Stat,
                   g1.CLOSING_SPREAD, g1.Covered_Spread
            FROM games g1
            JOIN games g2 ON g1.GAME_ID = g2.GAME_ID 
            WHERE g1.TEAM <> g2.TEAM
        """

    # Apply additional filters
for stat, value in filters.items():
    if value is not None:
        if compare_vs_opponent:
            query += f" AND g1.{stat} BETWEEN {value[0]} AND {value[1]}"
        else:
            query += f" AND {stat} BETWEEN {value[0]} AND {value[1]}"

    print("Executing SQL Query:", query)  # Debugging Output

    try:
    print("Executing SQL Query:", query)  # Debugging Output
    df = pd.read_sql(query, conn)
except Exception as e:
    st.error(f"🚨 SQL Query Failed: {e}")
    st.write(f"🔎 Query that caused the error: {query}")  # Show query in Streamlit UI
    df = pd.DataFrame()  # Return an empty DataFrame on failure

    conn.close()
    return df

# Streamlit UI
st.title("College Basketball Betting Analysis")

# Toggle for Offense vs. Defense Comparison
compare_vs_opponent = st.checkbox("Compare with Opponent's Defense?")

# Select the stat to analyze
selected_stat = st.selectbox("Select a Stat to Analyze", list(stat_pairs.keys()) + filterable_stats)

# Sliders for additional filters (only applied if the stat is in filterable_stats)
filters = {}
for stat in filterable_stats:
    if stat != selected_stat:
        filters[stat] = st.slider(f"Filter {stat}", 0.0, 100.0, (0.0, 100.0))

# Fetch Data
df = get_data(compare_vs_opponent, selected_stat, filters)

# Visualization
if not df.empty:
    if compare_vs_opponent and selected_stat in stat_pairs:
        st.write(f"### {selected_stat} vs. Opponent's {stat_pairs[selected_stat]}")
        fig, ax = plt.subplots()
        ax.scatter(df["Team_Stat"], df["Opponent_Stat"])
        ax.set_xlabel(f"Team {selected_stat}")
        ax.set_ylabel(f"Opponent {stat_pairs[selected_stat]}")
        ax.set_title(f"{selected_stat} vs. Opponent Defense")
        st.pyplot(fig)
    else:
        st.write(f"### Distribution of {selected_stat}")
        st.bar_chart(df[selected_stat])
else:
    st.write("No data found for the selected filters.")