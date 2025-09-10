import os
import streamlit as st
import re

from src.functions.helpers import (
    MODEL_MAPPINGS, 
    MODEL_OPTIONS, 
    ALM_TOOL_TYPES, 
    LLMModelConfig, 
    construct_model,
    invoke_with_history
)
from src.classes.prompt_templates import multiple_history_analysis_template 
from src.functions.settings import (
    get_project_info,
    save_rqm_tool_details,
    get_all_rqm_tool_details,
    delete_rqm_tool_details,
    get_work_items_project,
    save_remove_work_items_project,
)
from src.functions import utility_functions
import json

st.session_state.setdefault("current_page", "Settings")
st.session_state.setdefault("project_config", {})
st.session_state.setdefault("selected_work_items", {})

def clean_html(text):
    if not text:
        return ""
    text = re.sub('<[^<]+?>', '', text)
    return text.replace("</br>", "\n").replace("</li>", "\n")

def render(type=None):
    project_name = st.session_state.get("current_project", "Unknown Project")
    st.header(project_name)

    # --- Tabs ---
    tab_info, tab_general = st.tabs(
        ["Info", "Tool Administration"]
    )

    # --- Load Data ---
    project_info = get_project_info(
        "planningverse/settings.db", project_name
    )

    alm_tools = get_all_rqm_tool_details(
        utility_functions.SETTINGS_DB, project_name
    )

    # --- Info Tab ---
    with tab_info:
        render_info_tab(project_info, alm_tools)

    # --- General Settings Tab ---
    with tab_general:
        render_general_tab(alm_tools, project_name)

def render_info_tab(project_info, alm_tools):
    st.write("### Current Description")
    st.write(project_info.get("project_description", "No description available."))
    st.divider()
    if st.button("Trigger IA Analysis", key="trigger_ia_analysis"):
        st.toast("IA analysis triggered.")
        # Add your IA analysis logic here
        history_json = {}
        for project in st.session_state["selected_work_items"]:
            for item in st.session_state["selected_work_items"][project]:
                connector = st.session_state["current_connector"]
                work_item_history = connector.get_work_item_history(item)
                if not work_item_history:
                    st.warning("No history available for this work item.")
                    return
                for entry in work_item_history:
                    if entry and entry.fields:
                        history_json[item] = json.dumps(entry.fields, default=str)
        model_name = st.session_state.get("LLM_MODEL_NAME")
        temperature = st.session_state.get("LLM_MODEL_TEMPERATURE")
        llm_config = LLMModelConfig(model_name=model_name, temperature=temperature)
        llm_model = construct_model(llm_config=llm_config)
        prompt_text = multiple_history_analysis_template.format(
            json.dumps(history_json, indent=2)
        )
        print("prompt_text", prompt_text)
        response = invoke_with_history(prompt_text)
        st.markdown(response)

    if alm_tools:
        for tool in alm_tools:
            st.markdown(
                f"**{tool['tool_type']}**: {tool['tool_name']} (URL: {tool['url']})"
            )
    else:
        st.write("No RQM tools configured.")

def render_general_tab(alm_tools, project_name):
    st.subheader("Tool Administration")
    with st.popover("Add New Tool", use_container_width=True):
        add_new_tool_form(project_name)

    if alm_tools:
        tool_categories = [
            ("Requirements Management", "Requirements Management Tools"),
            ("Test Case Management", "Test Case Management Tools"),
            ("Code Repository", "Code Repository Tools"),
        ]
        for rqm_type, header in tool_categories:
            filtered_tools = [tool for tool in alm_tools if tool.get("rqm_type") == rqm_type]
            if filtered_tools:
                st.write(f"### {header}")
                for tool in filtered_tools:
                    render_tool_expander(tool)


def add_new_tool_form(project_name):
    new_tool_name = st.selectbox(
        "Tool Name",
        options=["ADO", "Jira", "Custom"],
        key="new_alm_tool_name",
        placeholder="Select tool name",
    )
    with st.form(key="add_new_tool_form", clear_on_submit=True):
        if new_tool_name == "Jira":
            new_tool_project = st.text_input(
                "Jira Project Key", key="new_alm_jira_project_key", placeholder="Enter Jira project key"
            )
            new_user_email = st.text_input(
                "Jira User Email", key="new_alm_jira_user_email", placeholder="Enter Jira user email"
            )
        elif new_tool_name == "ADO":
            new_tool_project = st.text_input(
                "Project Name", key="new_alm_tool_project", placeholder="Enter project name"
            )
            new_user_email = ""
        else:
            new_tool_project = st.text_input(
                "Tool Project", key="new_alm_custom_project", placeholder="Enter tool project"
            )
            new_user_email = st.text_input(
                "User Email", key="new_alm_custom_user_email", placeholder="Enter user email"
            )
        alm_type = st.selectbox(
            "Tool Type",
            options=["Requirements Management", "Test Case Management", "Code Repository"],
            key="new_alm_type",
            placeholder="Select tool type",
        )
        new_tool_url = st.text_input(
            "Tool URL", key="new_alm_tool_url", placeholder="Enter tool URL"
        )
        new_tool_token = st.text_input(
            "Access Token",
            key="new_alm_tool_token",
            placeholder="Enter access token",
            type="password",
        )
        submitted = st.form_submit_button("Save Tool")
        if submitted:
            rr = save_rqm_tool_details(
                db_path=utility_functions.SETTINGS_DB,
                project=project_name,
                tool_type=new_tool_name,
                rqm_type=alm_type,
                url=new_tool_url,
                tool_name=new_tool_project,
                pat=new_tool_token,
                user_email=new_user_email
            )
            print(f"Tool save result: {rr}")
            st.toast(f"New RQM tool '{new_tool_name}' added successfully.")

            st.session_state["load_tree"] = True
            st.rerun()

def save_work_items_project(db_path, project, tool_name):
    if tool_name in st.session_state["selected_work_items"]:
        work_items = st.session_state["selected_work_items"][tool_name]
        for item in work_items:
            save_remove_work_items_project(db_path, project, tool_name, item)
        st.toast(f"Work items saved for {tool_name} in project {project}.")
    else:
        st.error(f"No work items selected for {tool_name}.")
    st.session_state["load_tree"] = True

def render_tool_expander(tool):
    tool_name = tool["tool_name"]
    project = tool["project"]
    url = tool["url"]
    pat = tool["pat"]
    user_email = tool["user_email"]


    # Load selected work items for this tool
    st.session_state["selected_work_items"][tool_name] = get_work_items_project(
        utility_functions.SETTINGS_DB, project, tool_name
    )

    with st.expander(
        f"{tool_name} selected: {len(st.session_state['selected_work_items'][tool_name])}",
        expanded=False,
    ):
        cols = st.columns([2, 2, 2])
        with cols[0]:
            st.markdown(f"URL: {url}")
        with cols[1]:
            st.button(
                "Delete",
                key=f"delete_{tool_name}",
                on_click=delete_rqm_tool_details,
                args=(utility_functions.SETTINGS_DB, project, tool_name),
                icon="❌",
            )
        with cols[2]:
            st.button(
                "Save Selected Items",
                key=f"save_work_items_{tool_name}",
                on_click=save_work_items_project,
                args=(utility_functions.SETTINGS_DB, project, tool_name),
                icon="💾",
            )

            # Fetch work items if not cached
            connector = st.session_state["alm_project_connector"][tool_name]
            connector.change_connection(url, tool_name, pat, user_email)
            work_items = connector.fetch_data()
            st.session_state["project_config"][tool_name] = {
                "url": url,
                "tool_name": tool_name,
                "personal_access_token": pat,
                "work_items": work_items,
                "user_email": user_email
            }

        if work_items:
            st.write(f"Total Work Items Fetched: {len(work_items)}")
            for item in work_items:
                if True or item.type == "User Story" or item.type == "Story": # Example filter
                    checked = st.checkbox(
                        f"Select ID: {item.id}, Title: {item.title}, Description: {clean_html(item.description)}",
                        key=f"check_{tool_name}_{item.id}",
                        value=item.id in st.session_state["selected_work_items"][tool_name],
                    )
                    if checked :
                        st.session_state["selected_work_items"][tool_name].append(item.id)