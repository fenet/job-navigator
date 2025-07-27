import streamlit as st
import pandas as pd
import sqlite3
import re


# --- Connect to SQLite DB ---
conn = sqlite3.connect("jobs.db")  # Ensure this path matches your DB location

# --- Sidebar Filters ---
st.sidebar.header("Filter Jobs")

location_filter = st.sidebar.text_input("Location contains (e.g., Vienna)")
keyword_filter = st.sidebar.text_input("Keyword in description (e.g., Python)")

# --- SQL Query with Dynamic Filtering ---
query = "SELECT positionname, company, location, description FROM jobs WHERE 1=1"

if location_filter:
    query += f" AND location LIKE '%{location_filter}%'"
if keyword_filter:
    query += f" AND description LIKE '%{keyword_filter}%'"

# --- Load Filtered Data ---
try:
    df = pd.read_sql_query(query, conn)

    st.subheader("Filtered Job Listings")
    if df.empty:
        st.info("No jobs found with the selected filters.")
    else:
        st.dataframe(df)

except Exception as e:
    st.error(f"An error occurred: {e}")

st.sidebar.subheader("Advanced SQL")
custom_query = st.sidebar.text_area("Run your own SQL query on the jobs table:")

if custom_query:
    try:
        custom_df = pd.read_sql_query(custom_query, conn)
        st.subheader("Custom Query Results")
        st.dataframe(custom_df)
    except Exception as e:
        st.error(f"SQL error: {e}")
skills = ['Python', 'SQL', 'Excel', 'Power BI', 'Tableau', 'R', 'Java', 'C++', 'AWS', 'Azure', 'Git']

st.subheader("Trend of Python Mentions Across Listings")

if 'description' in df.columns:
    df['python_mentioned'] = df['description'].str.contains('Python', case=False, na=False).astype(int)
    df['cumulative_python'] = df['python_mentioned'].cumsum()

    st.line_chart(df['cumulative_python'])
else:
    st.warning("Description column not found.")
st.subheader(" Job Recommendations Based on Your Skills")

# Skills to choose from
skills = ['Python', 'SQL', 'Power BI', 'Excel', 'Tableau', 'R', 'Java', 'C++', 'AWS', 'Azure', 'Git']

# Multiselect input
selected_skills = st.multiselect("Select your skills", skills)

# Filter jobs based on selected skills
if selected_skills:
    # Create a regex pattern like: Python|SQL|Tableau
    pattern = '|'.join([re.escape(skill) for skill in selected_skills])

    # Filter the DataFrame
    matching_jobs = df[df['description'].str.contains(pattern, case=False, na=False)]

    st.write(f"Found {len(matching_jobs)} jobs matching your skills:")
    st.dataframe(matching_jobs[['positionname', 'company', 'location', 'description']].head(10))
else:
    st.info("Please select at least one skill to get job recommendations.")

# --- Resume Gap Analysis ---
st.subheader("Resume Gap Analyzer")

user_resume = st.text_area("Paste your resume or skills here (comma-separated):", height=150)

if user_resume:
    user_skills = [skill.strip().lower() for skill in user_resume.split(",")]

    market_skills = [s.lower() for s in skills]  # 'skills' is defined from earlier

    matched = set(user_skills) & set(market_skills)
    missing = set(market_skills) - set(user_skills)

    st.success(f"Matched Skills: {', '.join(matched) if matched else 'None'}")
    st.warning(f"Skills in demand but missing from your resume: {', '.join(missing) if missing else 'None'}")

# --- Job Alert Suggestions ---
st.subheader("Job Suggestions Based on Your Resume")

if user_resume:
    suggestions = df[df['description'].str.contains('|'.join([re.escape(skill) for skill in user_skills]), case=False, na=False)]
    st.write(f"Found {len(suggestions)} matching job listings:")
    st.dataframe(suggestions[['positionname', 'company', 'location', 'description']].head(10))

st.set_page_config(page_title="Job Navigator", layout="wide")
st.title("Job Market Insight Dashboard")
st.markdown("Gain insights into job trends, skills in demand, and match your resume to real listings.")

# --- Close DB Connection ---
conn.close()

