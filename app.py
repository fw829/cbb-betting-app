import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Database connection
DB_PATH = "basketball_data.db"
conn = sqlite3.connect(DB_PATH)

st.title("College Basketball Betting Analysis")

# Fetch available teams & seasons
teams = pd.read_sql("SELECT DISTINCT TEAM FROM games ORDER BY TEAM", conn)['TEAM'].tolist()
seasons = pd.read_sql("SELECT DISTINCT Season FROM games ORDER BY Season DESC", conn)['Season'].tolist()

# User Inputs: Filters
selected_team = st.selectbox("Select a Team", ["All Teams"] + teams)
selected_season = st.selectbox("Select a Season", ["All Seasons"] + [str(s) for s in seasons])
spread_range = st.slider("Filter by Closing Spread", -25, 25, (-25, 25))

# Build the Query with Filters
query = "SELECT * FROM games WHERE 1=1"
if selected_team != "All Teams":
    query += f" AND TEAM = '{selected_team}'"
if selected_season != "All Seasons":
    query += f" AND Season = {selected_season}"
query += f" AND CLOSING_SPREAD BETWEEN {spread_range[0]} AND {spread_range[1]}"

# Fetch Data
df = pd.read_sql(query, conn)

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

# Close Connection
conn.close()