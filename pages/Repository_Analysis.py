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
                
            st.success("Repository sources analysis completed.")
            
            if analysis_type == "Overall Analysis":
                work_item_json = {}
                files_to_analyze = []
                for project in st.session_state["selected_work_items"]:
                    for item in st.session_state["selected_work_items"][project][:100]:
                        try:
                            work_item_json[item.id] = st.session_state.work_items_json[item.id]
                        except Exception as e:
                            print(f"Error loading data for item {item.id}: {e}")
                        
                for root, dirs, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, "r", encoding="utf-8", errors="ignore") as analysis_file:
                                files_to_analyze.append(analysis_file.read())
                        except Exception as e:
                            print(f"Error reading file {file_path}: {e}")
                        
                prompt = pt.project_repository_analysis_template.format(files_to_analyze=files_to_analyze, requirements=work_item_json)
                st.write(prompt)
                
                
                
                
            elif analysis_type == "Code Quality":
                prompt = pt.code_quality_analysis_template.format(pre_analysed_content=files_to_analyze)
            elif analysis_type == "Security Vulnerabilities":
                prompt = pt.security_vulnerabilities_analysis_template.format(pre_analysed_content=files_to_analyze)
            elif analysis_type == "Dependency Analysis":
                prompt = pt.dependency_analysis_template.format(pre_analysed_content=files_to_analyze)
            elif analysis_type == "Migration Planning":
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
                            
                prompt = pt.migration_planning_analysis_template.format(pre_analysed_content=files_to_analyze)
            
            response = invoke_with_history(prompt, session_id="repo_analysis_session")
            print(response)
            st.markdown("### Repository Analysis:")
            # Display the response content or message
            if hasattr(response, "content"):
                st.write(response.content)
            elif isinstance(response, dict) and "message" in response:
                st.write(response["message"])
            else:
                st.write(str(response))