import requests
import streamlit as st
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Task Manager", layout="centered")

if "token" not in st.session_state:
    st.session_state.token = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ---------- Auth screens ----------
def login_register_screen():
    st.title("Task Manager")
    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pw")
        if st.button("Login"):
            res = requests.post(
                f"{API_URL}/auth/login",
                data={"username": email, "password": password},
            )
            if res.status_code == 200:
                st.session_state.token = res.json()["access_token"]
                st.rerun()
            else:
                st.error(res.json().get("detail", "Login failed"))

    with tab_register:
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pw")
        if st.button("Register"):
            res = requests.post(
                f"{API_URL}/auth/register",
                json={"email": email, "password": password},
            )
            if res.status_code == 201:
                st.success("Registered — now log in.")
            else:
                st.error(res.json().get("detail", "Registration failed"))


# ---------- Main app ----------
def task_app():
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update(token=None))

    st.title("My Tasks")

    with st.expander("➕ Add task manually"):
        title = st.text_input("Title")
        description = st.text_area("Description", "")
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=1)
        if st.button("Create Task"):
            res = requests.post(
                f"{API_URL}/tasks",
                json={"title": title, "description": description, "priority": priority},
                headers=auth_headers(),
            )
            if res.status_code == 201:
                st.success("Task created")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Failed to create task"))

    with st.expander("🤖 Generate tasks with AI"):
        text = st.text_area("Describe your day/week")
        if st.button("Generate"):
            res = requests.post(
                f"{API_URL}/tasks/generate", json={"text": text}, headers=auth_headers()
            )
            if res.status_code == 200:
                st.success(f"Created {len(res.json())} task(s)")
                st.rerun()
            else:
                st.error(res.json().get("detail", "Generation failed"))

    st.divider()

    status_filter = st.selectbox("Filter by status", ["all", "todo", "in_progress", "done"])
    params = {} if status_filter == "all" else {"status_filter": status_filter}
    res = requests.get(f"{API_URL}/tasks", params=params, headers=auth_headers())

    if res.status_code != 200:
        st.error("Failed to load tasks")
        return

    tasks = res.json()
    if not tasks:
        st.info("No tasks yet.")

    for task in tasks:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{task['title']}**  \n{task.get('description') or ''}")
                st.caption(f"Status: {task['status']} · Priority: {task['priority']}")
            with col2:
                new_status = st.selectbox(
                    "Status",
                    ["todo", "in_progress", "done"],
                    index=["todo", "in_progress", "done"].index(task["status"]),
                    key=f"status_{task['id']}",
                    label_visibility="collapsed",
                )
                if new_status != task["status"]:
                    requests.put(
                        f"{API_URL}/tasks/{task['id']}",
                        json={"status": new_status},
                        headers=auth_headers(),
                    )
                    st.rerun()
                if st.button("Delete", key=f"del_{task['id']}"):
                    requests.delete(f"{API_URL}/tasks/{task['id']}", headers=auth_headers())
                    st.rerun()


# ---------- Router ----------
if st.session_state.token is None:
    login_register_screen()
else:
    task_app()