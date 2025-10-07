import os
import streamlit as st
import git
import src.classes.prompt_templates as pt
import src.functions.utility_functions as uf
from src.functions.utility_functions import extract_json_blocks

from src.functions.helpers import (
    invoke_with_history
)

# --- Streamlit App Logic ---
def render():
    st.title("Apex AI Repository Analysis Tool")
    
    repo_url = st.text_input("Repository URL", "")
    username = st.text_input("Username", "")
    token = st.text_input("Token", type="password")
    
    path = "/workspaces/AI-dev-reqts-gathering/repo/" + repo_url.split("/")[-1].replace(".git", "")
    
    files_to_analyze = []
    
    analysis_type = st.selectbox("Select Analysis Type", ["Code Quality", "Security Vulnerabilities", "Dependency Analysis", "Overall Analysis", "Migration Planning"])
    
    
    if st.button("Retrieve Repository Content", type="primary"):
        if not repo_url or not username or not token:
            st.warning("Please provide the repository URL, username, and token.")
        else:
            
            if os.path.exists(path):
                st.info("Repository already cloned. Using existing content.")
            else:
                os.makedirs(path, exist_ok=True)
                with st.spinner("Retrieving repository content..."):
                    try:
                        # Embed credentials in the URL for HTTPS cloning
                        if repo_url.startswith("https://"):
                            protocol_removed = repo_url[len("https://"):]
                            auth_repo_url = f"https://{username}:{token}@{protocol_removed}"
                        else:
                            auth_repo_url = repo_url
                        git.Repo.clone_from(auth_repo_url, to_path=path)
                        st.success("Repository content retrieved successfully!")
                        # Here you can add code to analyze the repository content as needed
                    except Exception as e:
                        st.error(f"Error retrieving repository content: {e}")
            for root, dirs, files in os.walk(path):
                if ".git" in dirs:
                    dirs.remove(".git")
                for file in files:
                    if file.endswith((
                        ".analysis.txt", ".docx", ".pdf", ".md", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".bmp", ".gitignore",
                        ".exe", ".dll", ".bin", ".class", ".jar", ".war", ".ear", ".zip", ".tar", ".gz", ".7z",
                        ".mp3", ".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv", ".git", ".db", ".pptx", ".ppt", ".xlsx", ".xls",
                        ".tmp", ".log", ".iso", ".img", ".flake8", ".pyc", ".pyo", ".whl", ".egg", ".example", ".ipynb"
                    )):
                        continue  # Skip analysis files
                    file_path = os.path.join(root, file)
                    st.write(file_path)
                    analysis_file_path = f"{file_path}.analysis.txt"
                    if os.path.exists(analysis_file_path):
                        #st.markdown(f"**Analysis for {file}:**")
                        with open(analysis_file_path, "r") as analysis_file:
                            analysis_content = analysis_file.read()
                            extracted_json = extract_json_blocks(analysis_content)
                            #st.markdown(extracted_json)
                            files_to_analyze.append(extracted_json)
                    else:
                        with open(file_path, 'r', errors='ignore') as f:
                            content = f.read().replace('\n', ' ')
                            prompt = pt.source_file_key_mapping.format(source_code=content)
                            #st.markdown(f"**Analysis for {file}:**")
                            response = invoke_with_history(prompt, session_id="repo_analysis_session")
                            #st.markdown(response.content)
                            with open(analysis_file_path, "w") as analysis_file:
                                analysis_file.write(response)
                            extracted_json = extract_json_blocks(response)
                            files_to_analyze.append(extracted_json)
            st.success("Repository sources analysis completed.")
            
            prompt = pt.project_repository_analysis_template.format(pre_analysed_content=files_to_analyze)
            st.json(files_to_analyze)
            
            response = invoke_with_history(prompt, session_id="repo_analysis_session")
            st.markdown("### Overall Repository Analysis:")
            # Display the response content or message
            if hasattr(response, "content"):
                st.write(response.content)
            elif isinstance(response, dict) and "message" in response:
                st.write(response["message"])
            else:
                st.write(str(response))