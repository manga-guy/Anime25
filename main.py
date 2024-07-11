import requests
import pandas as pd
import time

BASE_URL = "https://api.jikan.moe/v4"
START_YEAR = 1999
END_YEAR = 2024
SEASONS = ["winter", "spring", "summer", "fall"]

# Initialize an empty DataFrame
columns = ["Name", "Season", "Rating", "Genre", "Viewer Count", "In Top 200"]
anime_data = pd.DataFrame(columns=columns)

def get_top_anime(season, year):
    url = f"{BASE_URL}/seasons/{year}/{season}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"Failed to fetch data for {season} {year}, status code: {response.status_code}")
        return []

def check_top_200(anime_id):
    url = f"{BASE_URL}/top/anime"
    response = requests.get(url)
    if response.status_code == 200:
        top_200 = response.json().get("data", [])
        for anime in top_200:
            if anime["mal_id"] == anime_id:
                return True
    return False

for year in range(START_YEAR, END_YEAR + 1):
    for season in SEASONS:
        print(f"Fetching data for {season} {year}...")
        top_anime = get_top_anime(season, year)
        for anime in top_anime[:20]:  # Get top 20 anime only
            name = anime["title"]
            rating = anime["score"]
            genres = ", ".join([genre["name"] for genre in anime["genres"]])
            viewer_count = anime["members"]
            in_top_200 = check_top_200(anime["mal_id"])
            anime_data = pd.concat([anime_data, pd.DataFrame([{
                "Name": name,
                "Season": f"{season} {year}",
                "Rating": rating,
                "Genre": genres,
                "Viewer Count": viewer_count,
                "In Top 200": "Yes" if in_top_200 else "No"
            }])], ignore_index=True)
        time.sleep(1)  # To avoid hitting the API rate limit

# Save the data to an Excel file
anime_data.to_excel("anime_data.xlsx", index=False)

print("Data collection complete. Saved to anime_data.xlsx")

# Analysis
season_stats = anime_data.groupby("Season").agg({
    "Rating": "mean",
    "Viewer Count": "mean",
    "In Top 200": lambda x: (x == "Yes").sum()
}).reset_index()

# Rename columns for clarity
season_stats.columns = ["Season", "Average Rating", "Average Viewer Count", "Top 200 Count"]

# Save the season stats to an Excel file
season_stats.to_excel("season_stats.xlsx", index=False)

print("Analysis complete. Saved to season_stats.xlsx")

