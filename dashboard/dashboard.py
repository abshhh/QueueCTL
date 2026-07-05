from pathlib import Path
import sys
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from app.services.worker_registry import WorkerRegistry

# ----------------------------------------------------
# Page
# ----------------------------------------------------

st.set_page_config(
    page_title="QueueCTL Dashboard",
    page_icon="⚙️",
    layout="wide",
)

st_autorefresh(
    interval=2000,
    key="dashboard_refresh",
)

# ----------------------------------------------------
# Database
# ----------------------------------------------------

DB_PATH = ROOT / "data" / "queue.db"


@st.cache_data(ttl=2)
def load_jobs():

    conn = sqlite3.connect(DB_PATH)

    df = pd.read_sql_query(
        """
        SELECT
            id,
            command,
            state,
            attempts,
            max_retries,
            locked_by,
            output,
            error,
            created_at,
            updated_at
        FROM jobs
        ORDER BY created_at DESC
        """,
        conn,
    )

    conn.close()

    return df


df = load_jobs()

registry = WorkerRegistry()

# ----------------------------------------------------
# Title
# ----------------------------------------------------

st.title("⚙️ QueueCTL Dashboard")
st.caption("Live Queue Monitoring")

# ----------------------------------------------------
# KPI Cards
# ----------------------------------------------------

pending = (df["state"] == "pending").sum()
processing = (df["state"] == "processing").sum()
completed = (df["state"] == "completed").sum()
failed = (df["state"] == "failed").sum()
dead = (df["state"] == "dead").sum()

c1, c2, c3, c4 = st.columns(4)

c1.metric("📦 Total Jobs", len(df))
c2.metric("🟡 Pending", pending)
c3.metric("🟢 Completed", completed)
c4.metric("🔴 Dead", dead)

c5, c6, c7 = st.columns(3)

c5.metric("🔵 Processing", processing)
c6.metric("🟠 Failed", failed)
c7.metric("👷 Active Workers", registry.active_count())

st.divider()

# ----------------------------------------------------
# Charts
# ----------------------------------------------------

left, right = st.columns(2)

with left:

    st.subheader("Job State Distribution")

    state_counts = (
        df["state"]
        .value_counts()
        .reset_index()
    )

    state_counts.columns = [
        "State",
        "Count",
    ]

    fig = px.pie(
        state_counts,
        values="Count",
        names="State",
        hole=0.45,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

with right:

    st.subheader("Retry Distribution")

    retry_counts = (
        df.groupby("attempts")
        .size()
        .reset_index(name="Jobs")
    )

    fig = px.bar(
        retry_counts,
        x="attempts",
        y="Jobs",
        labels={
            "attempts": "Retry Attempts",
            "Jobs": "Jobs",
        },
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

st.divider()

# ----------------------------------------------------
# Filters
# ----------------------------------------------------

f1, f2 = st.columns(2)

search = f1.text_input(
    "🔍 Search Job ID",
)

state = f2.selectbox(
    "Filter State",
    [
        "All",
        "pending",
        "processing",
        "completed",
        "failed",
        "dead",
    ],
)

filtered = df.copy()

if search:

    filtered = filtered[
        filtered["id"].str.contains(
            search,
            case=False,
            na=False,
        )
    ]

if state != "All":

    filtered = filtered[
        filtered["state"] == state
    ]

# ----------------------------------------------------
# Table
# ----------------------------------------------------

st.subheader("Jobs")

display = filtered[
    [
        "id",
        "state",
        "attempts",
        "max_retries",
        "locked_by",
        "created_at",
    ]
]

st.dataframe(
    display,
    use_container_width=True,
    hide_index=True,
)

# ----------------------------------------------------
# Job Details
# ----------------------------------------------------

st.subheader("Job Details")

for _, job in filtered.head(10).iterrows():

    with st.expander(job["id"]):

        st.write(f"**State:** {job['state']}")
        st.write(f"**Attempts:** {job['attempts']}")
        st.write(f"**Command:**")

        st.code(job["command"])

        st.write("**Output**")

        st.code(
            job["output"]
            if job["output"]
            else "No Output"
        )

        st.write("**Error**")

        st.code(
            job["error"]
            if job["error"]
            else "No Error"
        )

st.divider()

st.success("Dashboard auto-refreshes every 2 seconds.")