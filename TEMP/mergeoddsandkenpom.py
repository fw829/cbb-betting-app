#mergeoddsandkenpom
import pandas as pd
from fuzzywuzzy import process

def load_data(kenpom_path, odds_path):
    """Loads KenPom and Odds data from CSV files."""
    kenpom_df = pd.read_csv(kenpom_path)
    odds_df = pd.read_csv(odds_path)
    return kenpom_df, odds_df

def standardize_team_names(df, column):
    """Standardizes team names to lowercase and strips whitespace."""
    df[column] = df[column].str.lower().str.strip()
    return df

def resolve_team_name_discrepancies(kenpom_df, odds_df):
    """Resolves mismatches between team names using manual mapping and fuzzy matching."""
    manual_mapping = {
        "florida st.": "florida state seminoles",
        "iowa st.": "iowa state cyclones",
        "kansas st.": "kansas state wildcats",
        "illinois chicago": "uic flames",
        "jacksonville st.": "jacksonville state gamecocks",
        "mcneese": "mcneese cowboys",
        "siue": "siu edwardsville cougars",
        "texas a&m corpus chris": "texas a&m-corpus christi islanders",
        "texas st.": "texas state bobcats",
        "purdue fort wayne": "purdue fort wayne mastodons",
        "ohio st.": "ohio state buckeyes",
        "oklahoma st.": "oklahoma state cowboys",
        "oregon st.": "oregon state beavers",
        "portland st.": "portland state vikings",
        "sam houston st.": "sam houston bearkats",
        "san diego st.": "san diego state aztecs",
        "tennessee st.": "tennessee state tigers",
        "tennessee tech": "tennessee tech golden eagles",
        "utah st.": "utah state aggies",
        "washington st.": "washington state cougars",
        "west virginia": "west virginia mountaineers",
        "western kentucky": "western kentucky hilltoppers",
        "western michigan": "western michigan broncos",
        "duquesne": "duquesne dukes",
        "nicholls": "nicholls colonels",
        "southern miss": "southern miss golden eagles",
        "csun": "cal state northridge matadors",
        "fiu": "florida international panthers",
        "liu": "long island university sharks",
        "louisiana monroe": "ul monroe warhawks",
        "nebraska omaha": "omaha mavericks",
        "southeastern louisiana": "se louisiana lions",
        "umkc": "kansas city roos",
    }
    
    # Apply manual mapping
    kenpom_df["TeamName"] = kenpom_df["TeamName"].replace(manual_mapping)
    
    # Find remaining unmatched teams
    kenpom_teams = set(kenpom_df["TeamName"])
    odds_teams = set(odds_df["TeamName"])
    missing_in_odds = kenpom_teams - odds_teams
    missing_in_kenpom = odds_teams - kenpom_teams
    
    # Fuzzy matching for remaining teams
    fuzzy_mapping = {}
    for team in missing_in_odds:
        best_match, score = process.extractOne(team, list(missing_in_kenpom))
        if score > 85:  # High confidence threshold
            fuzzy_mapping[team] = best_match
    
    # Apply fuzzy mapping
    kenpom_df["TeamName"] = kenpom_df["TeamName"].replace(fuzzy_mapping)
    return kenpom_df

def merge_datasets(kenpom_df, odds_df):
    """Merges Odds and KenPom datasets on TeamName and Season."""
    merged_df = pd.merge(odds_df, kenpom_df, on=["TeamName", "Season"], how="left")
    return merged_df

def save_merged_data(merged_df, output_path):
    """Saves the merged dataset to a CSV file."""
    merged_df.to_csv(output_path, index=False)

if __name__ == "__main__":
    # File paths
    kenpom_path = "mergedkenpom.csv"
    odds_path = "oddspremerge.csv"
    output_path = "merged_oddsandkenpom.csv"
    
    # Load data
    kenpom_df, odds_df = load_data(kenpom_path, odds_path)
    
    # Standardize team names
    kenpom_df = standardize_team_names(kenpom_df, "TeamName")
    odds_df = standardize_team_names(odds_df, "TeamName")
    
    # Resolve team name discrepancies
    kenpom_df = resolve_team_name_discrepancies(kenpom_df, odds_df)
    
    # Merge datasets
    merged_df = merge_datasets(kenpom_df, odds_df)
    
    # Save merged data
    save_merged_data(merged_df, output_path)
    
    print(f"Merged dataset saved to {output_path}")
