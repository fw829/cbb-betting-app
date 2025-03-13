import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Function to connect to the database and fetch data (with caching)
def get_data(team, season, spread_range, tempo_range, adj_o_range, adj_d_range, fg3_range):
    conn = sqlite3.connect("basketball_data.db")

    # Start SQL query
    query = "SELECT * FROM games WHERE 1=1"

    # Ensure string values are properly formatted
    if team != "All Teams":
        query += f" AND TEAM = '{team}'"
    if season != "All Seasons":
        query += f" AND Season = '{season}'"  # Treating season as a string

    # Ensure numeric values are cast correctly
    query += f" AND CLOSING_SPREAD BETWEEN {int(spread_range[0])} AND {int(spread_range[1])}"
    query += f" AND AdjTempo BETWEEN {float(tempo_range[0])} AND {float(tempo_range[1])}"
    query += f" AND AdjOE BETWEEN {float(adj_o_range[0])} AND {float(adj_o_range[1])}"
    query += f" AND AdjDE BETWEEN {float(adj_d_range[0])} AND {float(adj_d_range[1])}"
    query += f" AND FG3Pct BETWEEN {float(fg3_range[0])} AND {float(fg3_range[1])}"

    # **Debugging: Print query to check for issues**
    print("SQL Query:", query)

    try:
        df = pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"SQL Query Failed: {e}")
        df = pd.DataFrame()  # Return empty DataFrame on failure

    conn.close()
    return df
st.title("College Basketball Betting Analysis")

# Fetch available teams & seasons (caching this too)
@st.cache_data
def get_teams_and_seasons():
    conn = sqlite3.connect("basketball_data.db")
    teams = pd.read_sql("SELECT DISTINCT TEAM FROM games ORDER BY TEAM", conn)['TEAM'].tolist()
    seasons = pd.read_sql("SELECT DISTINCT Season FROM games ORDER BY Season DESC", conn)['Season'].tolist()
    conn.close()
    return teams, seasons

teams, seasons = get_teams_and_seasons()

# User Inputs
selected_team = st.selectbox("Select a Team", ["All Teams"] + teams)
selected_season = st.selectbox("Select a Season", ["All Seasons"] + [str(s) for s in seasons])
spread_range = st.slider("Filter by Closing Spread", -25, 25, (-25, 25))
tempo_range = st.slider("Filter by Tempo (AdjTempo)", 50, 80, (50, 80))
adj_o_range = st.slider("Filter by Offensive Efficiency (AdjOE)", 80, 130, (80, 130))
adj_d_range = st.slider("Filter by Defensive Efficiency (AdjDE)", 80, 130, (80, 130))
fg3_range = st.slider("Filter by 3PT % (FG3Pct)", 25, 45, (25, 45))

# Fetch Data (Uses Caching)
df = get_data(selected_team, selected_season, spread_range, tempo_range, adj_o_range, adj_d_range, fg3_range)

# Cover % Calculation
if not df.empty:
    total_games = len(df)
    covered_games = df[df["Covered_Spread"] == "Y"].shape[0]
    cover_pct = round((covered_games / total_games) * 100, 2)

    # Display Cover % Summary
    st.write(f"### Cover Percentage for Selected Filters: **{cover_pct}%**")

    # Over/Under Hit Rate
    over_games = df[df["Hit_Over"] == "Y"].shape[0]
    over_pct = round((over_games / total_games) * 100, 2)
    st.write(f"### Over/Under Hit Rate: **{over_pct}%**")

    # Cover Rate by Spread Buckets
    spread_buckets = {
        "-25 to -21": (-25, -21),
        "-20 to -16": (-20, -16),
        "-15 to -11": (-15, -11),
        "-10 to -6": (-10, -6),
        "-5 to -1": (-5, -1),
        "0 to 5": (0, 5),
        "6 to 10": (6, 10),
        "11 to 15": (11, 15),
        "16 to 20": (16, 20),
        "21 to 25": (21, 25),
    }

    bucket_data = []
    for bucket, (low, high) in spread_buckets.items():
        bucket_df = df[(df["CLOSING_SPREAD"] >= low) & (df["CLOSING_SPREAD"] <= high)]
        if not bucket_df.empty:
            bucket_cover_pct = round((bucket_df[bucket_df["Covered_Spread"] == "Y"].shape[0] / len(bucket_df)) * 100, 2)
            bucket_data.append((bucket, bucket_cover_pct))

    # Convert to DataFrame for Chart
    bucket_df = pd.DataFrame(bucket_data, columns=["Spread Range", "Cover %"])

    # Plot Cover % by Spread Bucket
    fig, ax = plt.subplots()
    ax.bar(bucket_df["Spread Range"], bucket_df["Cover %"], color="blue")
    ax.set_xlabel("Spread Range")
    ax.set_ylabel("Cover %")
    ax.set_title("Cover % by Spread Bucket")
    plt.xticks(rotation=45)

    # Show Chart in Streamlit
    st.pyplot(fig)

else:
    st.write("No games found for selected filters.")