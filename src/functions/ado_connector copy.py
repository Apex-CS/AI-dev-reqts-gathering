from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import streamlit as st
import json
from src.classes import work_item, common_data

import src.interfaces.connector

class AdoConnector(src.interfaces.connector.ConnectorInterface):
    def __init__(self):
        self.session_state = st.session_state

    def change_connection(self, base_url, project_name, personal_access_token, user_email=None):
        try:
            print("Changing ADO connection...")
            self.session_state["connection_ado"] = {
                "base_url": base_url,
                "project_name": project_name,
                "personal_access_token": personal_access_token
            }
        except Exception as e:
            st.error(f"Error changing connection: {e}")

    def get_connection(self):
        try:
            conn_info = self.session_state.get("connection_ado", {})
            credentials = BasicAuthentication('', conn_info.get("personal_access_token"))
            return Connection(base_url=conn_info.get("base_url"), creds=credentials)
        except Exception as e:
            st.error(f"Error getting connection: {e}")
            return None

    def get_wit_client(self):
        try:
            connection = self.get_connection()
            if connection:
                return connection.clients.get_work_item_tracking_client()
        except Exception as e:
            st.error(f"Error getting WIT client: {e}")
        return None

    def get_git_client(self):
        try:
            connection = self.get_connection()
            if connection:
                return connection.clients.get_git_client()
        except Exception as e:
            st.error(f"Error getting Git client: {e}")
        return None

    def fetch_data(self):
        try:
            wit_client = self.get_wit_client()
            if not wit_client:
                return []
            project_name = self.session_state["connection_ado"].get('project_name')
            wiql = {
                'query': (
                    f"SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo] "
                    f"FROM WorkItems WHERE [System.TeamProject] = '{project_name}' "
                    "ORDER BY [System.Id] DESC"
                )
            }
            result = wit_client.query_by_wiql(wiql)
            ids = [wi.id for wi in result.work_items][:200] if result.work_items else []
            if not ids:
                return []
            work_items = wit_client.get_work_items(ids)
            return [
                common_data.CommonData.from_azure_devops(item)
                for item in work_items
            ]
        except Exception as e:
            st.error(f"Failed to fetch work items. Please check your connection settings. {e}")
            return []

    def fetch_data_by_ids(self, ids):
        try:
            if not ids:
                return []
            wit_client = self.get_wit_client()
            if not wit_client:
                return []
            work_items = wit_client.get_work_items(ids, expand='relations')
            result = []
            for item in work_items:
                wi_type = item.fields.get('System.WorkItemType', 'Unknown')
                if wi_type == 'User Story':
                    result.append(work_item.WorkItem.from_azure_devops(item))
            return result
        except Exception as e:
            st.error(f"Failed to get Azure DevOps client: {e}")
            return []

    def add_work_item(self, title, description, acceptance_criteria, project_name):
        try:
            wit_client = self.get_wit_client()
            if not wit_client:
                return None
            patch_document = [
                {"op": "add", "path": "/fields/System.Title", "value": title},
                {"op": "add", "path": "/fields/System.Description", "value": description},
                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria", "value": acceptance_criteria or ''},
                {"op": "add", "path": "/fields/System.Tags", "value": "AI Requirements Gathering"}
            ]
            return wit_client.create_work_item(patch_document, project_name, 'Task')
        except Exception as e:
            st.error(f"Error adding work item: {e}")
            return None

    def fetch_work_item_by_id(self, work_item_id):
        try:
            wi = self.get_wit_client().get_work_item(work_item_id)
            wi_type = wi.fields.get("System.WorkItemType", "")
            if wi_type == "User Story":
                return work_item.WorkItem.from_azure_devops(wi)
            return None
        except Exception as e:
            st.error(f"Error fetching work item by id: {e}")
            return None

    def update_work_item(self, work_item_id, title=None, description=None, acceptance_criteria=None):
        try:
            wit_client = self.get_wit_client()
            if not wit_client:
                return
            patch = []
            if title:
                patch.append({"op": "add", "path": "/fields/System.Title", "value": title})
            if description:
                patch.append({"op": "add", "path": "/fields/System.Description", "value": description})
            if acceptance_criteria:
                patch.append({
                    "op": "add",
                    "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                    "value": acceptance_criteria
                })
            patch.append({
                "op": "add",
                "path": "/fields/System.Tags",
                "value": "Planningverse AI Improved"
            })
            if patch:
                wit_client.update_work_item(patch, work_item_id)
        except Exception as e:
            st.error(f"Error updating work item: {e}")

    def update_work_item_tc(self, work_item_id, title=None, description=None, steps=None, parameters=None):
        try:
            wit_client = self.get_wit_client()
            if not wit_client:
                return
            patch = []
            if title:
                patch.append({"op": "add", "path": "/fields/System.Title", "value": title})
            if description:
                patch.append({"op": "add", "path": "/fields/System.Description", "value": description})
            if steps:
                steps_xml = self._build_steps_xml(steps)
                patch.append({"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Steps", "value": steps_xml})
            if parameters:
                patch.append({"op": "add", "path": "/fields/Microsoft.VSTS.TCM.Parameters", "value": parameters})
            patch.append({"op": "add", "path": "/fields/System.Tags", "value": "Planningverse AI Improved"})
            if patch:
                wit_client.update_work_item(patch, work_item_id)
        except Exception as e:
            st.error(f"Error updating test case work item: {e}")

    def _build_steps_xml(self, steps):
        steps_xml = ""
        for j, case in enumerate(steps.splitlines(), start=2):
            cleaned_case = case.lstrip().split(' ', 1)
            case_text = cleaned_case[1] if len(cleaned_case) > 1 and cleaned_case[0].replace('.', '').isdigit() else case
            steps_xml += (
                f"<step id=\"{j}\" type=\"ActionStep\">"
                f"<parameterizedString isformatted=\"true\">{case_text}</parameterizedString>"
                f"<parameterizedString isformatted=\"true\">&lt;DIV&gt;&lt;P&gt;&lt;BR/&gt;&lt;/P&gt;&lt;/DIV&gt;</parameterizedString>"
                f"<description/>"
                f"</step>"
            )
        return f"<steps id=\"0\" last=\"{len(steps.splitlines())}\">{steps_xml}</steps>"

    def update_work_item_with_test_results(self, work_item_id, test_results):
        try:
            wit_client = self.get_wit_client()
            if not wit_client:
                return
            patch = [
                {
                    "op": "add",
                    "path": f"/fields/Microsoft.VSTS.Common.TestResults[{i}]",
                    "value": tr
                }
                for i, tr in enumerate(test_results)
            ]
            if patch:
                wit_client.update_work_item(patch, work_item_id)
        except Exception as e:
            st.error(f"Error updating work item with test results: {e}")
            
    def fetch_work_item_commits_by_id():
        pass
    def get_commit_details():
        pass
    def get_git_commit_content():
        pass
    def update_work_item_with_test_cases():
        pass