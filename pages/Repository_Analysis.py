import os
import streamlit as st
import git
import src.classes.prompt_templates as pt
from src.functions.utility_functions import extract_json_blocks
from src.functions.helpers import invoke_with_history

# --- Constants ---
SUPPORTED_CODE_EXTENSIONS = (
    ".py", ".js", ".java", ".cpp", ".c", ".cs", ".rb", ".go", ".ts", ".php", ".swift", ".kt",
    ".md", ".html", ".css", ".json", ".xml", ".yml", ".yaml", ".sh", ".rs"
)
SKIP_EXTENSIONS = (
    ".analysis.txt", ".docx", ".pdf", ".md", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".bmp", ".gitignore",
    ".exe", ".dll", ".bin", ".class", ".jar", ".war", ".ear", ".zip", ".tar", ".gz", ".7z",
    ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".git", ".db", ".pptx", ".ppt", ".xlsx", ".xls",
    ".tmp", ".log", ".iso", ".img", ".flake8", ".pyc", ".pyo", ".whl", ".egg", ".example", ".ipynb"
)

def get_repo_path(repo_url):
    return "repo/" + repo_url.split("/")[-1].replace(".git", "")

def clone_repository(repo_url, username, token, path):
    if os.path.exists(path):
        st.info("Repository already cloned. Using existing content.")
        return True
    os.makedirs(path, exist_ok=True)
    with st.spinner("Retrieving repository content..."):
        try:
            if repo_url.startswith("https://"):
                protocol_removed = repo_url[len("https://"):]
                auth_repo_url = f"https://{username}:{token}@{protocol_removed}"
            else:
                auth_repo_url = repo_url
            git.Repo.clone_from(auth_repo_url, to_path=path)
            st.success("Repository content retrieved successfully!")
            return True
        except Exception as e:
            st.error(f"Error retrieving repository content: {e}")
            return False

def collect_files(path, extensions, skip_exts=None):
    files = []
    for root, dirs, file_list in os.walk(path):
        if ".git" in dirs:
            dirs.remove(".git")
        for file in file_list:
            if skip_exts and file.endswith(skip_exts):
                continue
            if file.endswith(extensions):
                files.append(os.path.join(root, file))
    return files

def read_files(files):
    contents = []
    for file in files:
        with open(file, 'r', errors='ignore') as f:
            contents.append(f.read().replace('\n', ' '))
    return contents

def analyze_overall(path):
    files = collect_files(path, SUPPORTED_CODE_EXTENSIONS)
    st.write("Files to analyze:")
    for file in files:
        st.write(file)
    files_content = read_files(files)
    st.success("Repository sources analysis completed.")
    prompt = pt.code_analysis_template.format(source_files=files_content)
    st.json(files_content)
    return invoke_with_history(prompt, st.session_state.get("work_item_selector", "default_session"))

def analyze_migration(path):
    files = collect_files(path, tuple(), skip_exts=SKIP_EXTENSIONS)
    files_to_analyze = []
    for file_path in files:
        st.write(file_path)
        analysis_file_path = f"{file_path}.analysis.txt"
        if os.path.exists(analysis_file_path):
            with open(analysis_file_path, "r") as analysis_file:
                analysis_content = analysis_file.read()
                extracted_json = extract_json_blocks(analysis_content)
                files_to_analyze.append(extracted_json)
        else:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read().replace('\n', ' ')
                prompt = pt.source_file_key_mapping.format(source_code=content)
                response = invoke_with_history(prompt, session_id=st.session_state.get("work_item_selector", "default_session"))
                with open(analysis_file_path, "w") as analysis_file:
                    analysis_file.write(response)
                extracted_json = extract_json_blocks(response)
                files_to_analyze.append(extracted_json)
    st.success("Repository sources analysis completed.")
    prompt = pt.project_repository_analysis_template.format(pre_analysed_content=files_to_analyze)
    st.json(files_to_analyze)
    return invoke_with_history(prompt, st.session_state.get("work_item_selector", "default_session"))

def render():
    st.title("Apex AI Repository Analysis Tool")
    repo_url = st.text_input("Repository URL", "")
    username = st.text_input("Username", "")
    token = st.text_input("Token", type="password")
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Code Quality", "Security Vulnerabilities", "Dependency Analysis", "Overall Analysis", "Migration Planning"]
    )
    path = get_repo_path(repo_url)
    response = ""

    if st.button("Retrieve Repository Content", type="primary"):
        if not repo_url or not username or not token:
            st.warning("Please provide the repository URL, username, and token.")
            return

        if not clone_repository(repo_url, username, token, path):
            return

        if analysis_type == "Overall Analysis":
            response = analyze_overall(path)
        elif analysis_type == "Migration Planning":
            response = analyze_migration(path)
        # Add more analysis types as needed

        st.markdown("### Overall Repository Analysis:")
        if hasattr(response, "content"):
            st.write(response.content)
        elif isinstance(response, dict) and "message" in response:
            st.write(response["message"])
        else:
            st.write(str(response))