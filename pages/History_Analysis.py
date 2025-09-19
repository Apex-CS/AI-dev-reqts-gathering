import streamlit as st
import re

from src.functions.helpers import (
    invoke_with_history
)
from src.classes.prompt_templates import history_analysis_template 

def clean_html(text):
    if not text:
        return ""
    text = re.sub('<[^<]+?>', '', text)
    return text.replace("</br>", "\n").replace("</li>", "\n")

def render(type=None):
    work_item_id = st.session_state["work_item"].id
    
    history = st.session_state.history_json.get(work_item_id, None)
    comments = st.session_state.comments_json.get(work_item_id, None)
    st.write("### Current Data")
    
    st.write(f"**Work Item ID:** {work_item_id}")
    st.write(f"**Title:** {st.session_state['work_item'].title}")
    st.write(f"**Description:** {clean_html(st.session_state['work_item'].description)}")
    st.write(f"**Acceptance Criteria:** {clean_html(st.session_state['work_item'].acceptance_criteria)}")
    st.write(f"**Status:** {st.session_state['work_item'].status}")
    
    if history:
        st.write(f"{len(history)} interactions on history")
    else:
        st.info("No history data available for the selected work item.")
        return
    
    if comments:
        st.write(f"{len(comments) } interactions on comments")
    else:
        st.info("No comments data available for the selected work item.")
        return
    
    if st.button("🚀 **Run Work Item IA Analysis**", type="primary"):
        json_data = history
        prompt_text = history_analysis_template.format(
            work_item_info={
                "title": st.session_state['work_item'].title,
                "description": st.session_state['work_item'].description,
                "acceptance_criteria": st.session_state['work_item'].acceptance_criteria,
                "status": st.session_state['work_item'].status
            },
            history_json=json_data,
            comments_json=comments
        )
        st.session_state.history_response[work_item_id] = invoke_with_history(prompt_text, work_item_id)
        st.header(f"Analysis for Work Item {work_item_id}")
        st.markdown(st.session_state.history_response[work_item_id].content)
        st.success("End of Analysis.")