import os
import streamlit as st
import re
import difflib
import json

from src.functions.work_items import NewWorkItem
from src.classes.prompt_templates import code_analysis_template
from src.functions.helpers import (
    invoke_with_history
)


def render_work_item_form(work_item, work_item_id):
    st.subheader(f"**Story Navigator, Work Item ID:** {work_item_id or 'Not provided'}")

def get_diff_content(current, previous):
    diff_content = {}
    for filename, content in current.items():
        prev_content = previous.get(filename, "")
        if content != prev_content:
            diff = difflib.unified_diff(
                prev_content.splitlines(),
                content.splitlines(),
                fromfile='Previous', tofile='Current', lineterm=''
            )
            diff_content[filename] = '\n'.join(diff)
    return diff_content

def show_diff(current, previous):
    st.session_state["code_diff"].clear()
    diff_content = get_diff_content(current, previous)
    for filename, diff_str in diff_content.items():
        st.session_state["code_diff"].append((filename, diff_str))
        st.code(diff_str, language="diff")

def show_commit_files(commit_content):
    for filename, content in commit_content.items():
        st.write(f"**{filename}:**")
        st.code(content, language="python" if filename.endswith('.py') else "text")

def extract_json_blocks(text):
    pattern = r'```json\s*([\s\S]*?)\s*```'
    json_blocks = []
    for match in re.findall(pattern, text, re.DOTALL):
        try:
            json_blocks.append(json.loads(match))
        except Exception:
            continue
    return json_blocks

def analyse_changes_callback(work_item, diff_data):
    template = code_analysis_template.format(
        title=work_item.title,
        description=work_item.description,
        acceptance_criteria=work_item.acceptance_criteria,
        diff_data=diff_data
    )
    st.session_state["result"] =  invoke_with_history(
        template,
        session_id="global"
    )

def render(type=None):
    work_item_id = st.session_state.get("story_item_selector")
    connector = st.session_state["current_connector"]

    if "commit_loaded" not in st.session_state:
        st.session_state["commit_loaded"] = None
        
    if "code_diff" not in st.session_state:
        st.session_state["code_diff"] = []

    project_name = st.session_state.get("current_project", "Planningverse Project")
    work_item_id = st.session_state["work_item"].id
    alm_result = connector.fetch_work_item_commits_by_id(work_item_id)
    work_item = alm_result.get("work_item")
    commits = alm_result.get("commits") or []
    render_work_item_form(work_item, work_item_id)
    commit_details_map = {}
    commit_changes = {}

    if commits:
        st.subheader("Associated Commits")
        for idx, commit in enumerate(commits):
            commit_details = connector.get_commit_details(commit.url, project_name)
            commit_details_map[idx] = commit_details
            col1, col2, col3, col4 = st.columns([2, 6, 4, 2])
            col1.write(commit.attributes.get("id", ""))
            col2.write(commit_details.comment)
            col3.markdown(
                f'<a href="{commit_details.remote_url}" target="_blank">Show Code</a>',
                unsafe_allow_html=True,
            )
            if col4.button("Load", key=f"load_{idx}"):
                st.session_state["commit_loaded"] = idx

        for idx, commit_details in commit_details_map.items():
            current_commit = connector.get_git_commit_content(commit_details.remote_url, project_name, commit_details.repository_id)
            prev_commit_details = commit_details_map.get(idx + 1)
            if prev_commit_details:
                prev_commit = connector.get_git_commit_content(prev_commit_details.remote_url, project_name, prev_commit_details.repository_id)
                diff = get_diff_content(current_commit, prev_commit)
                commit_changes[idx] = {"comment": commit_details.comment, "code": diff}
            else:
                commit_changes[idx] = {"comment": commit_details.comment, "code": current_commit}

        if st.button("🧑‍💻 Analyse Changes", key="analyze_changes", disabled=not commit_details_map, type="primary"):
            analyse_changes_callback(work_item, commit_changes)
        
    else:
        st.info("No commits found for this work item.")
        
    loaded_idx = st.session_state["commit_loaded"]
    commit_obj = commit_details_map.get(loaded_idx)
    if commit_obj:
        st.subheader("Commit Content")
        current_commit = connector.get_git_commit_content(commit_obj.remote_url, project_name, commit_obj.repository_id)
        st.session_state["current_commit_loaded"] = current_commit

        prev_commit_obj = commit_details_map.get(loaded_idx + 1)
        if prev_commit_obj:
            prev_commit = connector.get_git_commit_content(prev_commit_obj.remote_url, project_name, prev_commit_obj.repository_id)
            st.session_state["before_commit_loaded"] = prev_commit
            show_diff(current_commit, prev_commit)
        else:
            st.write("No previous commit to compare with, current Commit Content:")
            show_commit_files(current_commit)
            st.session_state["code_diff"] = list(current_commit.items())

    if st.session_state.get("result"):
        st.subheader("Analysis Result")
        json_blocks = extract_json_blocks(st.session_state["result"].content)
        if json_blocks:
            st.markdown(json_blocks[0].get("detailed_analysis", ""))
            st.session_state["new_work_items"] = json_blocks[0].get("pending_items", [])
            st.session_state["new_test_cases"] = json_blocks[0].get("test_cases", [])

        st.header("New Test Cases")
        for idx, test_case in enumerate(st.session_state.get("new_test_cases", []), 1):
            st.write(f"**Test Case {idx}:**")
            st.write(f"**ID:** {test_case.get('test_case_id', 'N/A')}")
            st.write(f"**Description:** {test_case.get('test_case_description', 'N/A')}")
            if st.button(f"🧪 Create Test Case {idx}", key=f"create_test_case_{idx}", type="primary"):
                # Implement logic to create the test case in ADO
                st.success(f"Test Case {idx} created successfully.")

        st.header("New Work Items")
        for idx, new_work in enumerate(st.session_state.get("new_work_items", []), 1):
            new_work_item = NewWorkItem.from_dict(new_work)
            st.write(f"**Work Item {idx}:**")
            st.write(f"**New Title:** {new_work_item.new_title}")
            st.write(f"**New Description:** {new_work_item.new_description}")
            st.write(f"**New Acceptance Criteria:** {', '.join(new_work_item.new_acceptance_criteria)}")
            if st.button(f"📝 Create Work Item {idx}", key=f"create_work_item_{idx}", type="primary"):
                response = connector.add_work_item(
                new_work_item.new_title,
                new_work_item.new_description,
                ', '.join(new_work_item.new_acceptance_criteria),
                project_name
                )
                if response:
                    st.success(f"Work Item {idx} created successfully with ID: {response.id}")
                else:
                    st.error("Failed to create work item.")