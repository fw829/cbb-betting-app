#setup kenpom scraper

from kenpompy.utils import login

# Replace with your actual KenPom login details
username = "kenpom.0m3of@passmail.net"
password = "2p7Cp*54d4DYKhFxhDwj"

session = login(username, password)  # Authenticates your session

print("Login successful!")  # Quick check
