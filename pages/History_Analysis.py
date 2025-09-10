import os
import streamlit as st
import re
import difflib
import json

import src.components.streamlit_elements as st_elems
import src.functions.helpers as helpers
from langchain.prompts import PromptTemplate
from src.functions.work_items import NewWorkItem
from src.functions.analysis_response import AnalysisResponse


def render(type=None):
    work_item_id = st.session_state["work_item"].id
    connector = st.session_state["current_connector"]
    work_item_history = connector.get_work_item_history(work_item_id)
    if not work_item_history:
        st.warning("No history available for this work item.")
        return
    st.header(f"History for Work Item {work_item_id}")
    for entry in work_item_history:
        if entry and entry.fields:
            try:
                st.subheader(f"Revision ID: {entry.fields.get('System.Rev', {}).get('new_value', 'N/A')}")
                st.write(f"**Changed Date:** {entry.fields.get('System.ChangedDate', {}).get('new_value', 'N/A')}")
                st.write("**Fields:**")
                for field_name, field_value in entry.fields.items():
                    if field_value:
                        st.write(f"**{field_name}:** {field_value}")
                st.markdown("----")
            except Exception as e:
                st.write(f"**Error displaying field:** {e}")

        
    st.success("End of history.")