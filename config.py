import os


DEFAULT_NICHE_QUERIES = [
    "Python",
    "Python Tutorial",
    "Python Programming",
    "Python Automation",
    "Python Selenium",
    "Python Pytest",
    "Python FastAPI",
    "Python Django",
    "Python Flask",
    "Python Data Science",
    "Python Machine Learning",
    "Python AI",
    "Python Pandas",
    "Python NumPy",
    "Python Data Engineering",
    "Python Web Scraping",
    "Python Backend Development",
    "Python APIs",
    "Python Projects",
    "Python Developer"
]


def get_niche_queries():

    raw_queries = os.getenv("NICHE_QUERIES")

    if not raw_queries:
        return DEFAULT_NICHE_QUERIES

    queries = [
        query.strip()
        for query in raw_queries.split(",")
        if query.strip()
    ]

    return queries or DEFAULT_NICHE_QUERIES
