import re
import streamlit as st
from src.functions.helpers import invoke_with_history
from src.functions.work_items import ImprovedWorkItem
import src.classes.prompt_templates as pt
from src.functions.utility_functions import (
    get_field,
    clean_html,
    REFS_DB
)
import requests

def format_acceptance_criteria(criteria):
    try:
        if isinstance(criteria, list):
            return "\n".join(map(str, criteria))
        return criteria or ""
    except Exception as e:
        st.toast(f"Error formatting acceptance criteria: {e}")
        return ""

def render_improved_work_item(work_item_id, response):
    try:
        improved_work_item = ImprovedWorkItem.from_content(
            ImprovedWorkItem, 
            response.replace('```json', '').replace('```', '').strip()
        )
        st.session_state.setdefault("story_improved_title", {})[work_item_id] = improved_work_item.improved_title
        st.session_state.setdefault("story_improved_description", {})[work_item_id] = improved_work_item.improved_description
        st.session_state.setdefault("story_improved_acceptance_criteria", {})[work_item_id] = improved_work_item.improved_acceptance_criteria
        st.session_state.setdefault("story_improved_explanation_changes", {})[work_item_id] = improved_work_item.explanation_changes
    except Exception as e:
        st.error(f"Error processing AI response, please try again.")
        print(f"Error processing AI response: {e}")
        st.session_state.setdefault("story_improved_explanation_changes", {})[work_item_id] = f"Error processing AI response"

def update_work_item_callback(alm_work_item_id, work_item_id, connector):
    st.toast("Updating work item...")
    try:
        improved_title = st.session_state.get(f"improved_title_{work_item_id}", "")
        improved_description = st.session_state.get(f"improved_description_{work_item_id}", "")
        improved_acceptance_criteria = st.session_state.get(f"improved_acceptance_criteria_{work_item_id}", "")
        acceptance_criteria = format_acceptance_criteria(improved_acceptance_criteria)
        connector.update_work_item(
            work_item_id=alm_work_item_id,
            title=improved_title,
            description=improved_description,
            acceptance_criteria=acceptance_criteria
        )
        st.toast(f"Work item ID {alm_work_item_id} updated successfully.")
    except Exception as e:
        st.toast(f"Failed to update work item ID {alm_work_item_id}: {e}")

def extract_link_content(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        st.toast(f"Error extracting link content from {url}: {e}")
        return ""

def ai_analysis_callback(type):
    try:
        st.toast("Analysing description...")
        work_item = st.session_state.get("work_item", {})
        documents = []
        work_item_id = st.session_state.get("story_item_selector")
        project =  st.session_state["project_rqm"][st.session_state.get("current_project")]

        prompt = pt.requirements_validations_template.format(
            title=work_item.title,
            description=work_item.description,
            acceptance_criteria=work_item.acceptance_criteria,
            work_item_id=work_item_id,
            documents="\n".join(documents) if documents else ""
        )
        improved_description = invoke_with_history(prompt, work_item_id)
        print("AI analysis response:", improved_description)
        render_improved_work_item(work_item_id, improved_description)
    except Exception as e:
        st.toast(f"Error during AI analysis: {e}")

def requirements_fields(work_item_id, work_item):
    try:
        improved_title = st.session_state.get("story_improved_title", {}).get(
            work_item_id, work_item.title
        )
        improved_description = st.session_state.get("story_improved_description", {}).get(
            work_item_id, clean_html(work_item.description)
        )
        improved_acceptance_criteria = format_acceptance_criteria(
            st.session_state.get("story_improved_acceptance_criteria", {}).get(
                work_item_id, clean_html(work_item.acceptance_criteria)
            )
        )
        st.text_input("Suggested Title", value=improved_title, key=f"improved_title_{work_item_id}")
        st.text_area("Suggested Description", value=improved_description, height=150, key=f"improved_description_{work_item_id}")
        st.text_area("Suggested Acceptance Criteria", value=improved_acceptance_criteria, height=400, key=f"improved_acceptance_criteria_{work_item_id}")
        st.header("**Analysis Result:**")
        st.markdown(
            st.session_state.get("story_improved_explanation_changes", {}).get(
                work_item_id, "No analysis available."
            )
        )
    except Exception as e:
        st.toast(f"Error rendering requirements fields: {e}")

def render(type=None):
    try:
        work_item_id = st.session_state.get("story_item_selector")
        work_item = st.session_state.get("work_item")
        connector = st.session_state["current_connector"]

        st.markdown("""
            <style>
            .buttonST button {
                background-color: #0078D4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 1em;
                cursor: pointer;
                transition: background 0.2s;
            }
            .buttonST button:hover {
                background-color: #005A9E;
            }
            </style>
        """, unsafe_allow_html=True)

        if not work_item:
            st.markdown("### Work item not found.")
            return

        st.button(
            label="AI Inspection",
            key="improve_description_button",
            on_click=ai_analysis_callback,
            args=(type,),
            type="primary"
        )

        tab1, tab2 = st.tabs(["Suggested Changes", "Original Data"])

        # --- Tab 1: Suggested Changes ---
        with tab1:
            requirements_fields(work_item_id, work_item)
            st.button(
                label="Update Work Item",
                key="update_work_item_button_req",
                on_click=lambda: update_work_item_callback(work_item.id, work_item_id, connector),
                type="primary",
            )
                

        # --- Tab 2: Original Data ---
        with tab2:
            st.markdown("### Original Requirements Data")
            st.text_input(
                "Title",
                value=work_item.title,
                disabled=True
            )
            st.text_area(
                "Description",
                value=clean_html(work_item.description),
                height=150,
                disabled=True
            )
            st.text_area(
                "Acceptance Criteria",
                value=format_acceptance_criteria(work_item.acceptance_criteria),
                height=400,
                disabled=True
            )
    except Exception as e:
        st.toast(f"Error rendering page: {e}")