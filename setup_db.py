import pandas as pd
import sqlite3

# Load CSV
df = pd.read_csv("data/jobs.csv")
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Connect to SQLite
conn = sqlite3.connect("jobs.db")

# Save to DB
df.to_sql("jobs", conn, if_exists="replace", index=False)

print("✅ Database created and data inserted.")

