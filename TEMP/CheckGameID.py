import pandas as pd

# File path
CSV_FILE = r"C:\Users\Frank W\OneDrive\Desktop\College Basketball Wagering\Database\merged_basketball_data.csv"

# Load data
merged_data = pd.read_csv(CSV_FILE)

# Count occurrences of each GAME-ID
game_id_counts = merged_data["GAME-ID"].value_counts()

# Identify GAME-IDs that appear more than twice
duplicated_game_ids = game_id_counts[game_id_counts > 2].index

# Remove rows with blank TeamName for duplicated GAME-IDs
merged_data = merged_data[~((merged_data["GAME-ID"].isin(duplicated_game_ids)) & (merged_data["TeamName"].isna()))]

# Save the cleaned data back to the CSV
merged_data.to_csv(CSV_FILE, index=False)

# Display results
print("Rows with blank TeamName removed for GAME-IDs appearing more than twice.")

