#setup kenpom scraper

from kenpompy.utils import login
from kenpompy.summary import get_misc, get_efficiency
import pandas as pd

# Replace with your actual KenPom login details
username = "kenpom.0m3of@passmail.net"
password = "2p7Cp*54d4DYKhFxhDwj"

import time
session = login(username, password)  # Authenticates your session
time.sleep(5) #wait 5 seconds
print(session.cookies) #see if auth worked

# Fetch Miscellaneous Stats (misc25)
misc_df = get_misc(session)
misc_df.to_csv("misc25.csv", index=False)  # Save as CSV
print("Fetching Misc25 stats...")
misc_df = get_misc(session)
print("Misc25 stats downloaded successfully!")

# Fetch Efficiency Stats (summary25)
efficiency_df = get_efficiency(session)
efficiency_df.to_csv("summary25.csv", index=False)  # Save as CSV
print("Fetching Summary25 stats...")
efficiency_df = get_efficiency(session)
print("Summary25 stats downloaded successfully!")

misc_df.to_csv("misc25.csv", index=False)
efficiency_df.to_csv("summary25.csv", index=False)

print("KenPom data successfully saved as two separate CSV files!")


