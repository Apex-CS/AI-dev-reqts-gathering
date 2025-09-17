import streamlit as st
import src.components.streamlit_elements as st_elems
import src.functions.utility_functions as utility_functions
from src.functions.helpers import MODEL_MAPPINGS, MODEL_OPTIONS

from src.functions.settings import (
    save_llm_settings, get_llm_settings, save_project_details, get_projects_details, edit_project_details, delete_project_details
)

def delete_project(db_path, project_name):
    delete_project_details(db_path, project_name)
    st.session_state["load_tree"] = True

def render():
    st.session_state.setdefault("current_page", "Global Settings")
    st.session_state["projects"] = []
    st.session_state.setdefault("project_config", {})
    # --- Tabs ---
    tab_general, tab_project_admin = st.tabs(["General", "Project Administration"])

    # --- General Settings Tab ---
    with tab_general:
        st.header("General Settings")
        st.subheader("LLM configuration settings.")

        llm_settings = get_llm_settings(utility_functions.SETTINGS_DB)
        model_index = MODEL_OPTIONS.index(llm_settings.get("LLM_MODEL_NAME", "apex-demos-gpt-4o"))

        def on_llm_model_change():
            save_llm_settings(
                db_path=utility_functions.SETTINGS_DB,
                settings={
                    "LLM_MODEL_NAME": st.session_state.get("LLM_MODEL_NAME", "apex-demos-gpt-4o"),
                    "LLM_MODEL_TEMPERATURE": st.session_state.get("LLM_MODEL_TEMPERATURE", 0.0)
                }
            )
            st.toast("LLM settings saved successfully.")

        st.selectbox(
            label="LLM Model",
            index=model_index,
            options=MODEL_OPTIONS,
            key="LLM_MODEL_NAME",
            placeholder="Select Model",
            format_func=lambda x: MODEL_MAPPINGS.get(x),
            disabled=not st.session_state.get("is_logged_in", True),
            on_change=on_llm_model_change
        )

        def on_temperature_change():
            save_llm_settings(
                db_path=utility_functions.SETTINGS_DB,
                settings={"LLM_MODEL_TEMPERATURE": st.session_state.get("LLM_MODEL_TEMPERATURE", 0.0)}
            )
            st.toast("Temperature setting saved successfully.")

        st.slider(
            label="Temperature",
            min_value=0.0,
            max_value=1.0,
            value=float(llm_settings.get("LLM_MODEL_TEMPERATURE", 0.0)),
            step=0.1,
            key="LLM_MODEL_TEMPERATURE",
            disabled=not st.session_state.get("is_logged_in", True),
            on_change=on_temperature_change
        )
    with tab_project_admin:
        st.subheader("Project Administration")
        with st.popover("Add New Project", use_container_width=True):
            with st.form("add_new_project_form", clear_on_submit=True):
                new_tool_project = st.text_input("Project Name", key="new_alm_tool_project", placeholder="Enter project name")
                new_tool_project_description = st.text_area("Project Description", key="new_alm_tool_description", placeholder="Enter project description", height=100)
                submitted = st.form_submit_button("Save Project", key="save_new_alm_tool")
                if submitted:
                    save_project_details(
                        db_path=utility_functions.SETTINGS_DB,
                        project_name=new_tool_project,
                        project_description=new_tool_project_description,
                        project_summary=""
                    )
                    st.session_state["load_tree"] = True
                    st.toast("Project added successfully.")
                    st.rerun()


        st.session_state["projects"] = get_projects_details(utility_functions.SETTINGS_DB)
        if st.session_state["projects"]:
            st.write("### Existing Projects")
            for project in st.session_state["projects"]:
                cols = st.columns([1, 3, 2, 2])
                with cols[0]:
                    st.markdown(f"{project['project_name']}")
                with cols[1]:
                    st.markdown(f"{project['project_description']}")
                with cols[2]:
                    with st.popover("✏️ Edit Project", use_container_width=True):
                        new_title = st.text_input(
                            "Edit Project Title",
                            value=project['project_name'],
                            key=f"edit_{project['project_name']}_title"
                        )
                        new_description = st.text_area(
                            "Edit Project Description",
                            value=project['project_description'],
                            key=f"edit_{project['project_name']}_description",
                            height=100
                        )
                        if st.button("Save Changes", key=f"save_edit_{project['project_name']}_description"):
                            edit_project_details(
                                db_path=utility_functions.SETTINGS_DB,
                                project_name=project['project_name'],
                                new_title=new_title,
                                new_description=new_description,
                                new_summary=project['project_summary']
                            )
                            st.toast("Project description updated successfully.")
                            st.session_state["load_tree"] = True
                            st.session_state["projects"] = get_projects_details(utility_functions.SETTINGS_DB)
                            st.rerun()
                with cols[3]:
                    st.button(
                        "Delete",
                        key=f"delete_{project['project_name']}",
                        on_click=delete_project,
                        args=(utility_functions.SETTINGS_DB, project['project_name']),
                        icon="❌"
                    )
