import os
from datetime import datetime

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(page_title="Task Manager", page_icon="✅", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None
if "email" not in st.session_state:
    st.session_state.email = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def api_get(path, params=None):
    return requests.get(f"{API_BASE_URL}{path}", headers=auth_headers(), params=params)


def api_post(path, json=None):
    return requests.post(f"{API_BASE_URL}{path}", headers=auth_headers(), json=json)


def api_put(path, json=None):
    return requests.put(f"{API_BASE_URL}{path}", headers=auth_headers(), json=json)


def api_delete(path):
    return requests.delete(f"{API_BASE_URL}{path}", headers=auth_headers())


# ---------- Auth screens ----------

def show_login_register():
    st.title("Task Manager Login")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log in"):
            res = requests.post(
                f"{API_BASE_URL}/auth/login",
                data={"username": email, "password": password},
            )
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.session_state.email = email
                st.rerun()
            else:
                st.error(res.json().get("detail", "Login failed"))

    with tab_register:
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        if st.button("Register"):
            res = requests.post(
                f"{API_BASE_URL}/auth/register",
                json={"email": email, "password": password},
            )
            if res.status_code == 201:
                st.success("Account created — switch to the Login tab.")
            else:
                st.error(res.json().get("detail", "Registration failed"))


# ---------- Task screens ----------

def render_task(task):
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"**{task['title']}**  ·  `{task['status']}`  ·  `{task['priority']}`")
            if task.get("description"):
                st.caption(task["description"])
            if task.get("deadline"):
                st.caption(f"Due: {task['deadline'][:16].replace('T', ' ')}")
        with col2:
            if st.button("Delete", key=f"del_{task['id']}"):
                api_delete(f"/tasks/{task['id']}")
                st.rerun()

        new_status = st.selectbox(
            "Status",
            ["todo", "in_progress", "done"],
            index=["todo", "in_progress", "done"].index(task["status"]),
            key=f"status_{task['id']}",
            label_visibility="collapsed",
        )
        if new_status != task["status"]:
            api_put(f"/tasks/{task['id']}", json={"status": new_status})
            st.rerun()


def show_task_list():
    st.subheader("My Tasks")

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by status", ["all", "todo", "in_progress", "done"])
    with col2:
        priority_filter = st.selectbox("Filter by priority", ["all", "low", "medium", "high"])

    params = {}
    if status_filter != "all":
        params["status_filter"] = status_filter
    if priority_filter != "all":
        params["priority"] = priority_filter

    res = api_get("/tasks", params=params)
    if res.status_code != 200:
        st.error("Could not load tasks.")
        return

    tasks = res.json()
    if not tasks:
        st.info("No tasks yet.")
    for task in tasks:
        render_task(task)


def show_create_task():
    st.subheader("Create Task")
    title = st.text_input("Title")
    description = st.text_area("Description", value="")
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
    has_deadline = st.checkbox("Set deadline")
    deadline = None
    if has_deadline:
        d = st.date_input("Deadline date")
        t = st.time_input("Deadline time")
        deadline = datetime.combine(d, t).isoformat()

    if st.button("Create"):
        if not title.strip():
            st.error("Title is required.")
            return
        payload = {"title": title, "description": description or None, "priority": priority}
        if deadline:
            payload["deadline"] = deadline
        res = api_post("/tasks", json=payload)
        if res.status_code == 201:
            st.success("Task created.")
            st.rerun()
        else:
            st.error(res.json().get("detail", "Could not create task"))


def show_ai_generate():
    st.subheader("Generate Tasks from Text")
    text = st.text_area(
        "Describe your day or week",
        placeholder="Finish the report by Friday, call the dentist, and prep for Monday's meeting",
        max_chars=2000,
    )
    if st.button("Generate"):
        if not text.strip():
            st.error("Please enter some text.")
            return
        with st.spinner("Generating tasks..."):
            res = api_post("/tasks/generate", json={"text": text})
        if res.status_code == 200:
            created = res.json()
            if not created:
                st.info("No tasks were found in that text.")
            else:
                st.success(f"Created {len(created)} task(s).")
                for task in created:
                    render_task(task)
        else:
            st.error(res.json().get("detail", "Generation failed"))


# ---------- Main ----------

if not st.session_state.token:
    show_login_register()
else:
    st.sidebar.write(f"Logged in as **{st.session_state.email}**")
    if st.sidebar.button("Log out"):
        st.session_state.token = None
        st.session_state.email = None
        st.rerun()

    page = st.sidebar.radio("Go to", ["My Tasks", "Create Task", "AI Generate"])
    if page == "My Tasks":
        show_task_list()
    elif page == "Create Task":
        show_create_task()
    elif page == "AI Generate":
        show_ai_generate()