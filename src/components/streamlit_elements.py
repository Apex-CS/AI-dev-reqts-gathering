import os
import streamlit as st
from dotenv import load_dotenv
import streamlit_antd_components as sac

from src.functions import utility_functions
from src.functions.settings import (
    get_all_rqm_tool_details,
    get_projects_details,
    get_work_items_project,
)

import src.functions.ado_connector as ado_connector
import src.functions.jira_connector as jira_connector

load_dotenv()

# Session state defaults
DEFAULT_SESSION_STATE = {
    "sprintsTree": False,
    "load_improved": False,
    "show_home": "Home",
    "current_project": "",
    "project_config": {},
    "connection_ado": {},
    "connection_jira": {},
    "current_connector": None,
    "alm_project_connector": {},
    "equivalence_classes_response": {},
    "story_improved_title": {},
    "story_improved_description": {},
    "story_improved_acceptance_criteria": {},
    "story_improved_explanation_changes": {},
    "project_rqm": {},
    "load_tree": True,
    "leaving_work_item": 0,
    "story_item_selector": 0,
    "test_item_selector": 0,
    "last_work_item_selector": 0,
}

for key, value in DEFAULT_SESSION_STATE.items():
    st.session_state.setdefault(key, value)

# Query params and environment
query_params = st.query_params
work_item_id = st.session_state.get("work_item_selector") or query_params.get("id", [None])
os.environ["work_item_selected"] = str(work_item_id)

# Icons mapping
ICONS = {
    "Epic": "list",
    "Issue": "cone",
    "Bug": "bug",
    "Task": "card-list",
    "Feature": "trophy",
    "User Story": "book",
    "Test Case": "check-circle",
    "Test Plan": "file-text",
    "Test Suite": "folder",
    "Unknown": "folder",
}

# Globals for tree state
tree_project = ""
tree_project_items = {}
project_items_count = 0
tree_items_info = {}
main_project = []

def build_tree_with_links(work_items, connector):
    tree_data, parents = {}, {}
    if not work_items:
        return tree_data, parents
    for wi in work_items:
        parents.setdefault(str(wi.id), set())
        wi_id = str(wi.id)
        type = "User Story" if wi.__class__.__name__ == "WorkItem" else "Test Case"
        tree_data.setdefault(
            wi_id,
            {
                "value": wi.title,
                "type": type,
                "title": wi_id,
                "icon": ICONS.get(type, 'folder'),
                "connector_type": connector.__class__.__name__
            }
        )
        if wi.relations:
            for rel in wi.relations:
                if rel.__class__.__name__ == "IssueLink":
                    get_issue = "inwardIssue" if rel.raw.get('inwardIssue') else "outwardIssue" if rel.raw.get('outwardIssue') else None
                    if rel.raw.get(get_issue):
                        raw_obj = rel.raw.get(get_issue)
                        if hasattr(raw_obj, 'to_dict'):
                            raw_obj = raw_obj.to_dict()
                        elif not isinstance(raw_obj, dict):
                            raw_obj = dict(raw_obj)
                        if raw_obj.get('fields').get('issuetype').get('name') == 'Test Case':
                            rel_id = raw_obj.get('key')
                            parents[wi_id].add(rel_id)
                            if rel_id not in tree_data:
                                wi_rel = connector.fetch_work_item_by_id(rel_id)
                                type = "User Story" if wi_rel.__class__.__name__ == "WorkItem" else "Test Case"
                                tree_data[rel_id] = {
                                    "value": wi_rel.title,
                                    "type": type,
                                    "title": wi_rel.id,
                                    "icon": ICONS.get(type, 'folder'),
                                    "connector_type": connector.__class__.__name__
                                }


                elif hasattr(rel, 'attributes') and rel.attributes.get('name') == 'Tests':
                    rel_id = rel.url.split('/')[-1]
                    parents[wi_id].add(rel_id)
                    if rel_id not in tree_data:
                        wi_rel = connector.fetch_work_item_by_id(rel_id)
                        if wi_rel:
                            type = "User Story" if wi_rel.__class__.__name__ == "WorkItem" else "Test Case"
                            tree_data[rel_id] = {
                                "value": wi_rel.title,
                                "type": type,
                                "title": wi_rel.id,
                                "icon": ICONS.get(type, 'folder'),
                                "connector_type": connector.__class__.__name__
                            }
    return tree_data, parents

def build_tree_result(tree_data, parents):
    tree_result = []
    for parent, children_set in parents.items():
        children = [{
            "value": tree_data.get(child, {}).get("value", ""),
            "title": child,
            "type": tree_data.get(child, {}).get("type", "Unknown"),
            "icon": tree_data.get(child, {}).get("icon", "folder"),
            "connector_type": tree_data.get(child, {}).get("connector_type", "Unknown")
        } for child in children_set]
        tree_result.append({
            "value": tree_data.get(parent, {}).get("value", ""),
            "title": parent,
            "type": tree_data.get(parent, {}).get("type", "Unknown"),
            "icon": tree_data.get(parent, {}).get("icon", "folder"),
            "connector_type": tree_data.get(parent, {}).get("connector_type", "Unknown"),
            "children": children
        })
    return tree_result

def build_tree_result_multiple_parents(tree_data):
    global tree_items_info

    tree_result = []

    # Find all nodes that are not children (i.e., roots)
    all_nodes = set(tree_items_info.keys())
    all_children = set()
    for children in tree_data.values():
        for child in children:
            all_children.add(str(child['title']))
    roots = list(all_nodes - all_children)

    def build_node(node_id):
        node_info = tree_items_info.get(node_id, {})
        children = tree_data.get(node_id, [])
        return {
            "value": node_info.get("value", ""),
            "title": node_id,
            "icon": ICONS.get(node_info.get("type", "Unknown"), "folder"),
            "connector_type": node_info.get("connector_type", "Unknown"),
            "children": [build_node(str(child['title'])) for child in children]
        }

    for root_id in roots:
        tree_result.append(build_node(root_id))

    tree_items_info = {}
    return tree_result

def build_tree_items(tree_result):
    def make_tree_item(node):
        global tree_project, project_items_count
        tree_project_items[project_items_count] = {"project": tree_project, "work_item_id": node['title'], "type": node.get('type', 'Unknown')}
        project_items_count += 1
        children = node.get('children', [])
        if children:
            return sac.TreeItem(
                node['title'],
                icon=node.get('icon'),
                tag=sac.Tag(node.get('connector_type').replace("Connector", "").upper(), color='lime' if node.get('connector_type') == "JiraConnector" else 'blue'),
                description=node.get('value', ''),
                children=[make_tree_item(child) if isinstance(child, dict)
                          else sac.TreeItem(child['title'], description=child.get('value', ''), icon=child.get('icon'))
                          for child in children]
            )
        return sac.TreeItem(node['title'], description=node.get('value', ''), tag=sac.Tag(node.get('connector_type').replace("Connector", "").upper(), color='lime' if node.get('connector_type') == "JiraConnector" else 'blue'), icon=node.get('icon'))
    return [make_tree_item(item) for item in tree_result]

def go_home():
    st.session_state["show_home"] = "Home"
    st.session_state["work_item_selector"] = 0

def go_settings():
    st.session_state["show_home"] = "Global_Settings"
    st.session_state["leaving_work_item"] = st.session_state["work_item_selector"]
    st.session_state["work_item_selector"] = None

def go_command_center():
    st.session_state["show_home"] = "Command_Center"
    st.session_state["leaving_work_item"] = st.session_state["work_item_selector"]
    st.session_state["work_item_selector"] = None

def common_sidebar():
    global tree_project, project_items_count, main_project
    if st.session_state.get("load_tree") or len(main_project) < 1:
        tree_items = []
        main_project = []
        project_items_count = 1
        st.session_state["work_item_selector"] = None
        for project in get_projects_details("planningverse/settings.db"):
            tree_items_emb = []
            project_name = project['project_name']
            tree_project_items[project_items_count] = {"project": project_name, "work_item_id": project_name, "type": "project"}
            project_items_count += 1
            for project_rqm in get_all_rqm_tool_details("planningverse/settings.db", project_name=project_name):
                st.session_state["project_rqm"][project_rqm['tool_name']] = project_name
                tree_project = project_rqm['tool_name']
                if True or project_rqm and "tool_name" in project_rqm and project_rqm['tool_name'] not in st.session_state["project_config"]:
                    alm_tool_class = ado_connector.AdoConnector if project_rqm['tool_type'] == "ADO" else jira_connector.JiraConnector
                    alm_tool = alm_tool_class()
                    st.session_state["alm_project_connector"][project_rqm['tool_name']] = alm_tool
                    alm_tool.change_connection(
                        project_rqm['url'],
                        project_rqm['tool_name'],
                        project_rqm['pat'],
                        project_rqm['user_email']
                    )
                    selected_work_items = get_work_items_project(
                        utility_functions.SETTINGS_DB, project_name, project_rqm['tool_name']
                    )
                    work_items = alm_tool.fetch_data_by_ids(selected_work_items)
                    st.session_state["project_config"][project_rqm['tool_name']] = {
                        "alm_tool": alm_tool,
                        "url": project_rqm['url'],
                        "tool_name": project_rqm['tool_name'],
                        "personal_access_token": project_rqm['pat'],
                        "user_email": project_rqm['user_email'],
                        "work_items": work_items
                    }
                    tree_data, parents = build_tree_with_links(work_items, alm_tool)
                    tree_result = build_tree_result(tree_data, parents)
                    
                    tree_items_emb.extend(build_tree_items(tree_result))
            tree_items.append(sac.TreeItem(
                project_name,
                icon='kanban',
                description=project['project_description'],
                children=tree_items_emb
            ))
        if not tree_items:
            tree_items.append(sac.TreeItem(
                "No Projects",
                icon='folder',
                description="No projects found in the database."
            ))
        main_project.insert(0, sac.TreeItem(
            "Analysis Project",
            icon='diagram-2',
            children=tree_items
        ))
    
    st.session_state["load_tree"] = False

    with st.sidebar:
        st.markdown(
            """
            <style>
            [kind="secondary"] {
            border: none !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.button('🏠 Home', on_click=go_home)
        sac.tree(
            items=main_project,
            key='work_item_selector',
            align='left',
            size='sm',
            icon='folder',
            open_all=False,
            return_index=True,
            open_index=[0] if len(main_project) else [],
            index=0
        )
        st.sidebar.button('⚙️ Enterprise Settings', on_click=go_settings)
        st.sidebar.button('📊 Traceability Matrix', on_click=go_command_center)

        os.environ["LLM_MODEL_NAME"] = st.session_state.get("LLM_MODEL_NAME", "apex-demos-gpt-4-32k")
        os.environ["LLM_MODEL_TEMPERATURE"] = str(st.session_state.get("LLM_MODEL_TEMPERATURE", 0.0))
        
        work_item_selector = st.session_state.get("work_item_selector")
        if st.session_state["work_item_selector"] == st.session_state["leaving_work_item"] and (st.session_state["show_home"] == "Global_Settings" or st.session_state["show_home"] == "Command_Center"):
            return
        elif not work_item_selector is None:
            st.session_state["show_home"] = "Home"
        if work_item_selector is not None and not isinstance(work_item_selector, list) and work_item_selector in tree_project_items:
            work_item_selector = int(work_item_selector)
            work_item = tree_project_items[work_item_selector]["work_item_id"]
            project_name = tree_project_items[work_item_selector]["project"]

            print(  f"Selected work item: {work_item} of type {tree_project_items[work_item_selector]['type']} in project {project_name}"  )

            if work_item:
                if not str(work_item).isdigit() and not tree_project_items[work_item_selector]['type'] == "User Story" and not tree_project_items[work_item_selector]['type'] == "Test Case":
                    st.session_state["current_project"] = project_name
                    st.session_state["show_home"] = "Settings"
                    return
                if project_name in st.session_state["project_config"]:
                    project_config = st.session_state["project_config"].get(project_name, {})
                    connector = st.session_state["alm_project_connector"][project_config['tool_name']]
                    st.session_state["current_connector"] = connector

                    connector.change_connection(
                        project_config.get('url'),
                        project_config.get('tool_name'),
                        project_config.get('personal_access_token'),
                        project_config.get('user_email')
                    )
                    st.session_state["current_project"] = project_name
                if tree_project_items[work_item_selector]["type"] == "project":
                    st.session_state["show_home"] = "Settings"
                elif tree_project_items[work_item_selector]["type"] == "User Story":
                    st.session_state["story_item_selector"] = work_item_selector
                    st.session_state["work_item"] = connector.fetch_work_item_by_id(str(work_item))
                    st.session_state["show_home"] = "Info"
                elif tree_project_items[work_item_selector]["type"] == "Test Case":
                    st.session_state["test_item_selector"] = work_item_selector
                    st.session_state["work_item_test"] = connector.fetch_work_item_by_id(str(work_item))
                    st.session_state["show_home"] = "Test_Cases"
                
                st.session_state["load_improved"] = os.environ["work_item_selected"] != str(work_item)
                os.environ["work_item_selected"] = str(work_item if work_item else False)
