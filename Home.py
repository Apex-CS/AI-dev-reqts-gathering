import streamlit as st
import streamlit_antd_components as sac

import src.components.streamlit_elements as st_elems
import src.functions.helpers as helpers

import pages.Code_Analysis as code_analysis
import pages.Repository_Analysis as repo_analysis
import pages.History_Analysis as history_analysis
import pages.Project_Panel as project_panel
import pages.Global_Settings as global_settings
import pages.Transcript_tool as transcript_tool

from langchain.prompts import PromptTemplate

# --- Config ---
st.set_page_config(
    page_title="Apex Systems + Generative AI",
    page_icon="https://www.apexsystems.com/profiles/apex/themes/apex_bootstrap/favicon.ico",
    initial_sidebar_state="expanded",
    layout="wide",
    menu_items={
        'About': (
            "# Apex Systems + Generative AI \n"
            f"Welcome {getattr(st.user, 'email', '') if getattr(st.user, 'is_logged_in', False) else ''} "
            "to the Apex Systems spot for Generative AI demos, feel free to ask any questions and test out what we have built using your own API Key from any of the supported models."
        )
    }
)

# --- Globals ---
DEFAULT_SESSION_STATE = {
    "LLM_MODEL_NAME": "apex-demos-gpt-4o",
    "LLM_MODEL_TEMPERATURE": 0.0,
    "work_item": 0,
    "work_item_test": 0,
    "show_home": "Home",
    "project_config": {},
    "current_connector": None,
    "current_page": "Home",
    "alm_project_connector": {},
    "detailed_instructions": "",
    "messages": [],
    "chat_history": {},
    "current_project": "",
    "analysis_completed": False,
    "test_case_format": "Traditional",
    "selected_work_items": {},
    "project_rqm": {},
    "load_tree": True,
    "leaving_work_item": 0,
    "incorporate_from_test_gen": "",
    "selected_tab_index": 0,
    "history_json": {},
    "comments_json": {},
    "commits_json": {},
    "work_items_json": {},
    "history_response": {},
    "code_analysis_response": {},
    "connection_ado_default": {
        "base_url": "https://dev.azure.com/anflores",
        "tool_type": "Requirements Management",
        "tool_name": "ADO",
        "user_email": "",
        "project_name": "AI Requirements Gathering",
    },
}

def set_default_session_state():
    for k, v in DEFAULT_SESSION_STATE.items():
        st.session_state.setdefault(k, v)

def ask_to_ai(description):
    prompt = PromptTemplate(
        input_variables=["description"],
        template="{description}\n\n"
    )
    response = helpers.invoke_with_history(
        prompt.format(description=description),
        session_id=st.session_state.get("work_item_selector", "default_session")
    )
    return response.content

def login_flow():
    st.markdown("### Please Login!")
    if st.button("Log in with Auth0"):
        st.login("auth0")
    st.stop()

def home():
    st.image("logo_p.jpg", width=200)
    st.title("AI-powered project planning assistant")
    st.subheader("Leverage Generative AI to automatically extract actionable requirements from transcriptions and notes, streamlining the creation of user stories.")
    st.subheader("Estimate timelines, effort, and risks for your work items by analyzing their complete history.")
    st.subheader("Analyze code snippets to uncover performance bottlenecks, optimization opportunities, and potential issues.")
    st.subheader("Order issues by priority based on historical data and project context.")

def initialize_chat(messages):
    session_id = st.session_state.get("work_item_selector", "default_session")
    chat_history = st.session_state.get("chat_history", {}).get(session_id, {}).get("messages", [
        {"role": "assistant", "content": "Hello! I am Planningverse, your AI assistant. How can I help you today?"}
    ])
    for message in chat_history:
        messages.chat_message(message["role"]).write(message["content"])

def handle_chat(messages, work_item_selector, tab_type):
    prompt = st.chat_input("Ask something to AI")
    if prompt:
        messages.chat_message("user").write(prompt)
        chat_history_dict = st.session_state.setdefault("chat_history", {})
        chat_session = chat_history_dict.setdefault(work_item_selector, {"messages": []})
        chat_history = chat_session["messages"]
        chat_history.append({"role": "user", "content": prompt})
        response = ask_to_ai(prompt)
        chat_history.append({"role": "assistant", "content": response})
        work_item_id = st.session_state.get("work_item_selector", "default_session")

        if "{" in response:
            page = st.session_state.get("current_page")
            if page == "Requirements Validation":
                messages.chat_message("assistant").write("I'll update the response for you.")
            elif page == "Test Case Validation":
                messages.chat_message("assistant").write("I'll update the response for you.")
            elif page == "Test Design & Generation":
                if not st.session_state['analysis_completed']:
                    st.session_state["equivalence_classes_response"] = qa_a.AIWrapper.parse_output(response)
                    
            else:
                messages.chat_message("assistant").write(response)
        else:
            messages.chat_message("assistant").write(response)
        st.rerun()

def render_tabs(tabs_desc, tab_renderers, tab_type):
    col1, col2 = st.columns([8, 1], gap="small")
    with col1:
        selected_tab = sac.tabs(
            [sac.TabsItem(label=desc, disabled=(i == 2)) for i, desc in enumerate(tabs_desc)],
            align='left', size='md', return_index=True, index=st.session_state.get("selected_tab_index")
        )
        st.session_state["current_page"] = tabs_desc[selected_tab]
    with col2:
        with st.popover("🤖  Chat", use_container_width=True):
            st.write("### Chat with AI")
            messages = st.container(height=500)
            initialize_chat(messages)
            handle_chat(messages, st.session_state.get("work_item_selector", "default_session"), tab_type)
            st.checkbox(
                "Use context",
                value=st.session_state.get("use_context", True),
                key="use_context"
            )
    tab_renderers[selected_tab](type=tab_type)

def planningverse_work_flow():
    st.subheader(f"Current Project: {st.session_state.get('current_project', 'Planningverse Project')}")
    work_item = st.session_state.get("work_item")
    project_name = st.session_state.get("current_project", "Planningverse Project")
    project_config = st.session_state.get("project_config", {}).get(project_name, {})
    work_item_url = ""
    if project_config.get("alm_tool", "").__class__.__name__ == "JiraConnector":
        work_item_url = f"{project_config.get('url', '')}/browse/{getattr(work_item, 'id', '')}" if work_item else "#"

    elif project_config.get("alm_tool", "").__class__.__name__ == "AdoConnector":
        work_item_url = f"{project_config.get('url', '')}/_workitems/edit/{getattr(work_item, 'id', '')}" if work_item else "#"
    st.markdown(
        f'<a href="{work_item_url}" style="color: blue;" target="_blank">'
        f'{project_config.get("url", "").replace("https://dev.azure.com/", "").replace("https://apexsystems.atlassian.net", "Jira")} / {project_name} / {getattr(work_item, "id", "")}'
        '</a>',
        unsafe_allow_html=True
    )
    work_item_id = st.session_state.get("story_item_selector") or st.query_params.get("id", [None])[0]
    st.session_state["selected_tab_index"] = 0
    if not isinstance(work_item_id, list):
        render_tabs(
            ["Interactions Analysis", "Code Analysis"],
            [history_analysis.render, code_analysis.render],
            tab_type="requirement"
        )
    else:
        home()


def main():
    set_default_session_state()
    st_elems.common_sidebar()
    show_home = st.session_state.get("show_home")
    if show_home == "Home":
        home()
    elif show_home == "Transcription_Import":
        transcript_tool.render()
    elif show_home == "Repo_Analysis":
        repo_analysis.render()
    elif show_home == "Settings":
        project_panel.render()
    elif show_home == "Info":
        planningverse_work_flow()
    elif show_home == "Global_Settings":
        global_settings.render()

if __name__ == "__main__":
    main()
