import pandas as pd

#FillOpponentInfo

# File path
file_path = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\Merged_Odds.csv"

# Load data
merged_data = pd.read_csv(file_path)

# Create a dictionary to map GAME-ID to both team names
game_id_map = merged_data.groupby("GAME-ID")["TEAM"].apply(list).to_dict()

# Create a dictionary to store team stats by GAME-ID and TEAM
team_stats = merged_data.set_index(["GAME-ID", "TEAM"])[["1H", "2H", "OT TOTAL", "F"]].to_dict(orient="index")

# Fill in missing opponent-related fields
for index, row in merged_data.iterrows():
    game_id = row["GAME-ID"]
    team = row["TEAM"]
    
    # Get opponent team name
    teams = game_id_map.get(game_id, [])
    opponent = [t for t in teams if t != team]

    if opponent:
        opp_team = opponent[0]
        opp_stats = team_stats.get((game_id, opp_team), {})

        # Only fill in missing values
        if pd.isna(row["Opp"]): merged_data.at[index, "Opp"] = opp_team
        if pd.isna(row["Opp 1H"]): merged_data.at[index, "Opp 1H"] = opp_stats.get("1H", None)
        if pd.isna(row["Opp 2H"]): merged_data.at[index, "Opp 2H"] = opp_stats.get("2H", None)
        if pd.isna(row["Opp OT Total"]): merged_data.at[index, "Opp OT Total"] = opp_stats.get("OT TOTAL", None)
        if pd.isna(row["Opp F"]): merged_data.at[index, "Opp F"] = opp_stats.get("F", None)

# Calculate Covered Spread (Only if missing)
for index, row in merged_data.iterrows():
    if pd.isna(row["Covered Spread"]) and pd.notna(row["F"]) and pd.notna(row["CLOSING SPREAD"]) and pd.notna(row["Opp F"]):
        result = row["F"] + row["CLOSING SPREAD"]
        
        if result > row["Opp F"]:
            merged_data.at[index, "Covered Spread"] = "Y"
        elif result < row["Opp F"]:
            merged_data.at[index, "Covered Spread"] = "N"
        else:
            merged_data.at[index, "Covered Spread"] = "PUSH"

# Calculate Hit Over (Only if missing)
for index, row in merged_data.iterrows():
    if pd.isna(row["Hit Over"]) and pd.notna(row["F"]) and pd.notna(row["Opp F"]) and pd.notna(row["CLOSING TOTAL"]):
        total_score = row["F"] + row["Opp F"]
        
        if total_score > row["CLOSING TOTAL"]:
            merged_data.at[index, "Hit Over"] = "Y"
        elif total_score < row["CLOSING TOTAL"]:
            merged_data.at[index, "Hit Over"] = "N"
        else:
            merged_data.at[index, "Hit Over"] = "PUSH"
# Save the updated file
merged_data.to_csv(file_path, index=False)

print(f"Updated file saved as {file_path}")