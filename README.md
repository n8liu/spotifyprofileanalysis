# Spotify Data Analysis Project

A comprehensive project for analyzing your personal Spotify listening data with a modern, interactive Flask dashboard and full ETL/data science pipeline.

<img width="1776" alt="analyticexample" src="https://github.com/user-attachments/assets/e9a74596-7e51-48f7-ada9-0edafba1916b" />

## Features
- **Live Spotify Analytics Dashboard** (Flask):
  - Login with Spotify (OAuth2)
  - Top 20 genres (from your top artists)
  - Top 50 most listened artists (by your Spotify listening habits)
  - Top 50 most listened tracks
  - All your top artists sorted by Spotify popularity (most → least popular)
  - Most and least popular artists highlighted
  - All playlists and all songs within each playlist, with collapsible/expandable UI
  - Minimal, scrollable, and responsive UI for easy exploration
- **ETL and Data Science**:
  - Extract playlist and track data from Spotify
  - ETL pipeline with Python and PySpark
  - Data analysis using SparkSQL
  - Visualizations in PowerBI
  - Recommendations based on playlist content

## Directory Structure
```
spotifyanalysis/
│
├── notebooks/               # Databricks or Jupyter notebooks
├── src/                     # Source code (API, ETL, PySpark)
├── requirements.txt         # Python dependencies
├── README.md                # Project overview
├── .env                     # Your Spotify API credentials
├── .env.example             # Example env file for API keys
├── server.py                # Flask web dashboard
├── tracks.csv, features.csv # CSVs for ETL/analysis
└── powerbi/                 # PowerBI dashboard files
```

## Setup
1. Copy `.env.example` to `.env` and add your Spotify API credentials.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the Flask dashboard:
   ```bash
   python3 server.py
   ```
   - Visit [https://localhost:5000](https://localhost:5000) and log in with Spotify.

## How to Run ETL & Data Science
- Use the Python scripts in `src/` to extract and process data.
- Use Databricks notebooks in `notebooks/` for PySpark analysis.
- Connect PowerBI to Databricks for visualization.

## Customization
- Change the playlist ID in the configuration or script arguments.
- Extend the dashboard with more analytics or visualizations as desired.

## Live Dashboard Analytics
- Top genres, artists, tracks, and playlists from your real Spotify account
- Collapsible playlist/song lists for clean navigation
- All tables are scrollable for large libraries

## Sample Visualizations
- Bar and pie charts of track features
- Table of recommended tracks
- Interactive web dashboard for personal Spotify usage

---

**Built for music lovers and data scientists to explore their Spotify data in depth!**
