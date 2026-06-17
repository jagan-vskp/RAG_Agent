"""
Data Analyst Learning Tracker
A Streamlit app to track your progress through the Data Analyst roadmap.
Data is persisted in tracker_data.json.
"""

import json
import os
import streamlit as st
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

DATA_FILE = "tracker_data.json"

DEFAULT_DATA = {
    "roadmap_steps": [
        {
            "id": 1,
            "title": "Understand the Role & Set Your Target",
            "description": "Decide what kind of Data Analyst you want to become and map required skills from 10–20 job postings.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 2,
            "title": "Build Core Statistics & Analytical Thinking",
            "description": "Learn descriptive stats, probability, hypothesis testing, confidence intervals, and experiment interpretation.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 3,
            "title": "Master Spreadsheets",
            "description": "Get strong in Excel/Google Sheets: lookup functions, pivot tables, charts, data cleaning, and business reporting.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 4,
            "title": "Learn SQL Deeply",
            "description": "Practice filtering, joins, aggregations, window functions, CTEs, and performance basics on real datasets.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 5,
            "title": "Learn One Analysis Language (Python)",
            "description": "Learn pandas, NumPy, visualization libraries, and notebook workflows for data cleaning, EDA, and reporting.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 6,
            "title": "Learn Visualization & Storytelling",
            "description": "Use Tableau or Power BI to build clear dashboards and KPI views focused on business narrative.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 7,
            "title": "Build Domain Knowledge",
            "description": "Choose one industry and learn its key metrics (e.g., CAC/LTV, churn/retention, margin/revenue).",
            "completed": False,
            "notes": ""
        },
        {
            "id": 8,
            "title": "Create a Portfolio with Real Projects",
            "description": "Build 4–6 end-to-end projects covering question, dataset, cleaning, analysis, dashboard, and recommendations.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 9,
            "title": "Develop Communication Skills",
            "description": "Practice presenting findings to non-technical audiences and writing concise insight summaries.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 10,
            "title": "Prepare for Interviews",
            "description": "Train on SQL challenges, case studies, dashboard critiques, and behavioral stories.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 11,
            "title": "Gain Practical Experience",
            "description": "Apply for internships, freelance gigs, volunteer analytics work, or internal projects.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 12,
            "title": "Execute a Focused Job Search",
            "description": "Tailor resume to analyst keywords, use portfolio links, network with analysts/recruiters, and track applications.",
            "completed": False,
            "notes": ""
        },
        {
            "id": 13,
            "title": "Keep Leveling Up After First Role",
            "description": "Strengthen experimentation, forecasting, data modeling, and stakeholder management.",
            "completed": False,
            "notes": ""
        }
    ],
    "courses": [
        {"id": 1, "name": "Statistics for Data Science", "platform": "Coursera", "category": "Statistics", "completed": False, "added_on": ""},
        {"id": 2, "name": "Excel Skills for Business", "platform": "Coursera", "category": "Spreadsheets", "completed": False, "added_on": ""},
        {"id": 3, "name": "SQL for Data Analysis", "platform": "Udacity", "category": "SQL", "completed": False, "added_on": ""},
        {"id": 4, "name": "Python for Everybody", "platform": "Coursera", "category": "Python", "completed": False, "added_on": ""},
        {"id": 5, "name": "Pandas & NumPy Fundamentals", "platform": "DataCamp", "category": "Python", "completed": False, "added_on": ""},
        {"id": 6, "name": "Tableau Desktop Specialist", "platform": "Tableau", "category": "Visualization", "completed": False, "added_on": ""},
        {"id": 7, "name": "Google Data Analytics Certificate", "platform": "Coursera", "category": "General", "completed": False, "added_on": ""}
    ],
    "projects": [
        {"id": 1, "name": "Exploratory Data Analysis on Sales Data", "description": "Clean and analyze a real sales dataset to find trends.", "status": "not_started", "added_on": ""},
        {"id": 2, "name": "SQL Business Insights Dashboard", "description": "Write advanced SQL queries and visualize results.", "status": "not_started", "added_on": ""},
        {"id": 3, "name": "Customer Churn Analysis", "description": "Predict and analyze churn factors using Python.", "status": "not_started", "added_on": ""},
        {"id": 4, "name": "Marketing Funnel Analysis", "description": "Track CAC, LTV, and conversion rates end-to-end.", "status": "not_started", "added_on": ""},
        {"id": 5, "name": "Interactive Tableau Dashboard", "description": "Build a KPI dashboard for a chosen domain dataset.", "status": "not_started", "added_on": ""}
    ],
    "skills": [
        {"id": 1, "name": "Descriptive Statistics", "category": "Statistics", "level": "beginner", "completed": False},
        {"id": 2, "name": "Hypothesis Testing", "category": "Statistics", "level": "beginner", "completed": False},
        {"id": 3, "name": "Excel Pivot Tables", "category": "Spreadsheets", "level": "beginner", "completed": False},
        {"id": 4, "name": "VLOOKUP / INDEX-MATCH", "category": "Spreadsheets", "level": "beginner", "completed": False},
        {"id": 5, "name": "SQL Joins & Aggregations", "category": "SQL", "level": "beginner", "completed": False},
        {"id": 6, "name": "SQL Window Functions", "category": "SQL", "level": "intermediate", "completed": False},
        {"id": 7, "name": "SQL CTEs", "category": "SQL", "level": "intermediate", "completed": False},
        {"id": 8, "name": "Python pandas", "category": "Python", "level": "beginner", "completed": False},
        {"id": 9, "name": "Python NumPy", "category": "Python", "level": "beginner", "completed": False},
        {"id": 10, "name": "Matplotlib / Seaborn", "category": "Python", "level": "beginner", "completed": False},
        {"id": 11, "name": "Tableau Dashboards", "category": "Visualization", "level": "beginner", "completed": False},
        {"id": 12, "name": "Data Storytelling", "category": "Communication", "level": "beginner", "completed": False},
        {"id": 13, "name": "A/B Testing", "category": "Statistics", "level": "intermediate", "completed": False},
        {"id": 14, "name": "Git & GitHub", "category": "Tools", "level": "beginner", "completed": False},
        {"id": 15, "name": "Business Metrics (CAC, LTV, Churn)", "category": "Domain", "level": "beginner", "completed": False}
    ]
}

# ============================================================
# DATA PERSISTENCE
# ============================================================

def load_data() -> dict:
    """Load tracker data from JSON file, creating defaults if missing."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                stored = json.load(f)
            # Ensure all top-level keys exist (handles partial files)
            for key in DEFAULT_DATA:
                if key not in stored:
                    stored[key] = DEFAULT_DATA[key]
            return stored
        except (json.JSONDecodeError, IOError):
            return json.loads(json.dumps(DEFAULT_DATA))
    return json.loads(json.dumps(DEFAULT_DATA))


def save_data(data: dict) -> None:
    """Persist tracker data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def next_id(items: list) -> int:
    """Return the next available integer ID."""
    return max((item["id"] for item in items), default=0) + 1


# ============================================================
# PROGRESS HELPERS
# ============================================================

def calc_progress(items: list, key: str = "completed", value: bool = True) -> tuple[int, int, float]:
    """Return (completed_count, total_count, percentage)."""
    total = len(items)
    if total == 0:
        return 0, 0, 0.0
    done = sum(1 for item in items if item.get(key) == value)
    return done, total, round(done / total * 100, 1)


def project_done_count(projects: list) -> tuple[int, int, float]:
    done = sum(1 for p in projects if p.get("status") == "completed")
    total = len(projects)
    pct = round(done / total * 100, 1) if total else 0.0
    return done, total, pct


def overall_progress(data: dict) -> float:
    """Weighted overall progress across all four sections."""
    _, _, r = calc_progress(data["roadmap_steps"])
    _, _, c = calc_progress(data["courses"])
    pd, pt, _ = project_done_count(data["projects"])
    p = round(pd / pt * 100, 1) if pt else 0.0
    _, _, s = calc_progress(data["skills"])
    return round((r + c + p + s) / 4, 1)


# ============================================================
# PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="DA Learning Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.metric-card {
    background: #f0f4f8;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    text-align: center;
}
.progress-label {
    font-size: 0.85rem;
    color: #555;
    margin-bottom: 0.2rem;
}
.badge-completed {
    background: #d4edda;
    color: #155724;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.badge-in-progress {
    background: #fff3cd;
    color: #856404;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
.badge-not-started {
    background: #f8d7da;
    color: #721c24;
    padding: 0.15rem 0.5rem;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD STATE
# ============================================================

if "tracker" not in st.session_state:
    st.session_state.tracker = load_data()

data = st.session_state.tracker

# ============================================================
# SIDEBAR — OVERALL PROGRESS
# ============================================================

with st.sidebar:
    st.title("📊 DA Learning Tracker")
    st.markdown("---")

    overall = overall_progress(data)
    st.subheader("🏆 Overall Progress")
    st.metric("Completion", f"{overall}%")
    st.progress(overall / 100)

    st.markdown("---")
    st.subheader("📈 Section Progress")

    rd, rt, rp = calc_progress(data["roadmap_steps"])
    st.markdown(f"<div class='progress-label'>🗺️ Roadmap Steps ({rd}/{rt})</div>", unsafe_allow_html=True)
    st.progress(rp / 100)

    cd, ct, cp = calc_progress(data["courses"])
    st.markdown(f"<div class='progress-label'>📚 Courses ({cd}/{ct})</div>", unsafe_allow_html=True)
    st.progress(cp / 100)

    projd, projt, projp = project_done_count(data["projects"])
    st.markdown(f"<div class='progress-label'>🔨 Projects ({projd}/{projt})</div>", unsafe_allow_html=True)
    st.progress(projp / 100)

    sd, st_, sp = calc_progress(data["skills"])
    st.markdown(f"<div class='progress-label'>🧠 Skills ({sd}/{st_})</div>", unsafe_allow_html=True)
    st.progress(sp / 100)

    st.markdown("---")
    if st.button("🔄 Reset to Defaults", use_container_width=True):
        st.session_state.tracker = json.loads(json.dumps(DEFAULT_DATA))
        save_data(st.session_state.tracker)
        st.rerun()

# ============================================================
# MAIN CONTENT — TABS
# ============================================================

st.title("📊 Data Analyst Learning Tracker")
st.caption("Track your journey through the Data Analyst roadmap step by step.")

tab1, tab2, tab3, tab4 = st.tabs(["🗺️ Roadmap", "📚 Courses", "🔨 Projects", "🧠 Skills"])

# ------------------------------------------------------------------
# TAB 1 — ROADMAP STEPS
# ------------------------------------------------------------------
with tab1:
    st.subheader("Data Analyst Roadmap — 13 Steps")
    st.caption(f"Completed: {rd} / {rt} steps ({rp}%)")
    st.progress(rp / 100)
    st.markdown("---")

    for step in data["roadmap_steps"]:
        col_check, col_body, col_notes = st.columns([0.5, 6, 3.5])

        with col_check:
            checked = st.checkbox(
                "",
                value=step["completed"],
                key=f"step_{step['id']}"
            )
            if checked != step["completed"]:
                step["completed"] = checked
                save_data(data)
                st.rerun()

        with col_body:
            label = f"~~{step['title']}~~" if step["completed"] else f"**{step['title']}**"
            st.markdown(f"**Step {step['id']}** — {label}")
            st.caption(step["description"])

        with col_notes:
            notes = st.text_input(
                "Notes",
                value=step.get("notes", ""),
                key=f"notes_{step['id']}",
                placeholder="Add notes...",
                label_visibility="collapsed"
            )
            if notes != step.get("notes", ""):
                step["notes"] = notes
                save_data(data)

        st.markdown("---")

# ------------------------------------------------------------------
# TAB 2 — COURSES
# ------------------------------------------------------------------
with tab2:
    st.subheader("Courses")
    st.caption(f"Completed: {cd} / {ct} courses ({cp}%)")
    st.progress(cp / 100)

    # Add new course
    with st.expander("➕ Add a New Course"):
        with st.form("add_course_form"):
            c1, c2, c3 = st.columns(3)
            new_name = c1.text_input("Course Name *")
            new_platform = c2.text_input("Platform (e.g. Coursera)")
            new_cat = c3.selectbox("Category", ["Statistics", "Spreadsheets", "SQL", "Python", "Visualization", "Communication", "Domain", "Tools", "General"])
            if st.form_submit_button("Add Course"):
                if new_name.strip():
                    data["courses"].append({
                        "id": next_id(data["courses"]),
                        "name": new_name.strip(),
                        "platform": new_platform.strip(),
                        "category": new_cat,
                        "completed": False,
                        "added_on": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(data)
                    st.success(f"Added '{new_name}'")
                    st.rerun()
                else:
                    st.error("Course name is required.")

    st.markdown("---")

    # Group by category
    categories = sorted({c["category"] for c in data["courses"]})
    for cat in categories:
        cat_courses = [c for c in data["courses"] if c["category"] == cat]
        done_in_cat = sum(1 for c in cat_courses if c["completed"])
        st.markdown(f"**{cat}** — {done_in_cat}/{len(cat_courses)} completed")

        for course in cat_courses:
            c1, c2, c3, c4 = st.columns([0.4, 4, 2, 0.8])
            with c1:
                checked = st.checkbox("", value=course["completed"], key=f"course_{course['id']}")
                if checked != course["completed"]:
                    course["completed"] = checked
                    save_data(data)
                    st.rerun()
            with c2:
                label = f"~~{course['name']}~~" if course["completed"] else course["name"]
                st.markdown(label)
            with c3:
                st.caption(course.get("platform", ""))
            with c4:
                if st.button("🗑️", key=f"del_course_{course['id']}", help="Delete"):
                    data["courses"] = [c for c in data["courses"] if c["id"] != course["id"]]
                    save_data(data)
                    st.rerun()
        st.markdown("---")

# ------------------------------------------------------------------
# TAB 3 — PROJECTS
# ------------------------------------------------------------------
with tab3:
    st.subheader("Projects")
    st.caption(f"Completed: {projd} / {projt} projects ({projp}%)")
    st.progress(projp / 100)

    STATUS_LABELS = {
        "not_started": ("🔴 Not Started", "badge-not-started"),
        "in_progress": ("🟡 In Progress", "badge-in-progress"),
        "completed": ("🟢 Completed", "badge-completed")
    }

    # Add new project
    with st.expander("➕ Add a New Project"):
        with st.form("add_project_form"):
            p_name = st.text_input("Project Name *")
            p_desc = st.text_area("Description", height=80)
            if st.form_submit_button("Add Project"):
                if p_name.strip():
                    data["projects"].append({
                        "id": next_id(data["projects"]),
                        "name": p_name.strip(),
                        "description": p_desc.strip(),
                        "status": "not_started",
                        "added_on": datetime.now().strftime("%Y-%m-%d")
                    })
                    save_data(data)
                    st.success(f"Added '{p_name}'")
                    st.rerun()
                else:
                    st.error("Project name is required.")

    st.markdown("---")

    for project in data["projects"]:
        p1, p2, p3 = st.columns([4, 2.5, 0.8])
        with p1:
            st.markdown(f"**{project['name']}**")
            st.caption(project.get("description", ""))
        with p2:
            statuses = ["not_started", "in_progress", "completed"]
            status_labels_list = [STATUS_LABELS[s][0] for s in statuses]
            current_idx = statuses.index(project.get("status", "not_started"))
            selected = st.selectbox(
                "Status",
                options=status_labels_list,
                index=current_idx,
                key=f"proj_status_{project['id']}",
                label_visibility="collapsed"
            )
            new_status = statuses[status_labels_list.index(selected)]
            if new_status != project.get("status"):
                project["status"] = new_status
                save_data(data)
                st.rerun()
        with p3:
            if st.button("🗑️", key=f"del_proj_{project['id']}", help="Delete"):
                data["projects"] = [p for p in data["projects"] if p["id"] != project["id"]]
                save_data(data)
                st.rerun()
        st.markdown("---")

# ------------------------------------------------------------------
# TAB 4 — SKILLS
# ------------------------------------------------------------------
with tab4:
    st.subheader("Skills")
    st.caption(f"Completed: {sd} / {st_} skills ({sp}%)")
    st.progress(sp / 100)

    LEVELS = ["beginner", "intermediate", "advanced"]

    # Add new skill
    with st.expander("➕ Add a New Skill"):
        with st.form("add_skill_form"):
            s1, s2, s3 = st.columns(3)
            sk_name = s1.text_input("Skill Name *")
            sk_cat = s2.selectbox("Category", ["Statistics", "Spreadsheets", "SQL", "Python", "Visualization", "Communication", "Domain", "Tools", "General"])
            sk_level = s3.selectbox("Level", LEVELS)
            if st.form_submit_button("Add Skill"):
                if sk_name.strip():
                    data["skills"].append({
                        "id": next_id(data["skills"]),
                        "name": sk_name.strip(),
                        "category": sk_cat,
                        "level": sk_level,
                        "completed": False
                    })
                    save_data(data)
                    st.success(f"Added '{sk_name}'")
                    st.rerun()
                else:
                    st.error("Skill name is required.")

    st.markdown("---")

    skill_categories = sorted({s["category"] for s in data["skills"]})
    for cat in skill_categories:
        cat_skills = [s for s in data["skills"] if s["category"] == cat]
        done_in_cat = sum(1 for s in cat_skills if s["completed"])
        st.markdown(f"**{cat}** — {done_in_cat}/{len(cat_skills)} mastered")

        for skill in cat_skills:
            sk1, sk2, sk3, sk4 = st.columns([0.4, 3.5, 2, 0.8])
            with sk1:
                checked = st.checkbox("", value=skill["completed"], key=f"skill_{skill['id']}")
                if checked != skill["completed"]:
                    skill["completed"] = checked
                    save_data(data)
                    st.rerun()
            with sk2:
                label = f"~~{skill['name']}~~" if skill["completed"] else skill["name"]
                st.markdown(label)
            with sk3:
                current_level_idx = LEVELS.index(skill.get("level", "beginner"))
                new_level = st.selectbox(
                    "Level",
                    options=LEVELS,
                    index=current_level_idx,
                    key=f"skill_level_{skill['id']}",
                    label_visibility="collapsed"
                )
                if new_level != skill.get("level"):
                    skill["level"] = new_level
                    save_data(data)
                    st.rerun()
            with sk4:
                if st.button("🗑️", key=f"del_skill_{skill['id']}", help="Delete"):
                    data["skills"] = [s for s in data["skills"] if s["id"] != skill["id"]]
                    save_data(data)
                    st.rerun()
        st.markdown("---")
