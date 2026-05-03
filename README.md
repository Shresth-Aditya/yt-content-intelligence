# 📺 YouTube Data Pipeline (Minimal End-to-End)

A minimal end-to-end data pipeline that extracts YouTube channel videos, transforms key fields, and stores them in a SQLite database.

The goal of this project is to **start simple and evolve based on real problems**, rather than over-engineering upfront.

---

## 🚀 What This Pipeline Does

1. **Extract**
   - Fetch latest videos from a YouTube channel using YouTube Data API

2. **Transform**
   - Extract relevant fields:
     - video_id
     - title
     - description
     - published_at

3. **Load**
   - Store data into a local SQLite database

---

## 🧱 Project Structure
project/
│
├── extract.py # API calls
├── transform.py # Data cleaning & structuring
├── load.py # DB operations
├── main.py # Pipeline runner
├── logger.py # Logging setup
├── config.py # API keys / constants
│
├── db.sqlite # Database (auto-created)
├── logs/ # Logs per run
│
└── README.md