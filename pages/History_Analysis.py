import streamlit as st
import json

from src.functions.helpers import (
    invoke_with_history
)
from src.classes.prompt_templates import history_analysis_template 


def render(type=None):
    work_item_id = st.session_state["work_item"].id
    
    if st.button("🚀 **Run History IA Analysis**", type="primary"):
        entry = st.session_state.history_json[work_item_id]
        json_data = json.loads(entry)
        prompt_text = history_analysis_template.format(
            history_json=json_data
        )
        st.session_state.history_response[work_item_id] = invoke_with_history(prompt_text, "global")
        st.header(f"Analysis for Work Item {work_item_id}")
        st.markdown(st.session_state.history_response[work_item_id].content)
        st.success("End of Analysis.")