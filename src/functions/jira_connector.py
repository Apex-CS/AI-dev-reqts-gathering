from jira import JIRA
import streamlit as st
import json
import requests
import src.interfaces.connector
from src.classes import work_item, common_data, commits

class JiraConnector(src.interfaces.connector.ConnectorInterface):

    # Initialize the JIRA client
    def __init__(self):
        self.session_state = st.session_state

    def change_connection(self, base_url, project_name, personal_access_token, user_email):
        print("Changing JIRA connection")
        self.session_state["connection_jira"] = {
            "base_url": base_url,
            "project_name": project_name,
            "personal_access_token": personal_access_token,
            "user_email": user_email
        }
        try:
            self.jira = self.get_connection()
        except Exception as e:
            st.error(f"Failed to connect to JIRA: {e}")

    def get_connection(self):
        try:
            return JIRA(
                server=self.session_state["connection_jira"].get("base_url"),
                basic_auth=(self.session_state["connection_jira"].get("user_email"), self.session_state["connection_jira"].get("personal_access_token"))
            )
        except Exception as e:
            st.error(f"Error establishing JIRA connection: {e}")
            return None

    def get_wit_client(self):
        try:
            # Not implemented
            st.info("get_wit_client not implemented.")
        except Exception as e:
            st.error(f"Error in get_wit_client: {e}")

    def get_git_client(self):
        try:
            # Not implemented
            st.info("get_git_client not implemented.")
        except Exception as e:
            st.error(f"Error in get_git_client: {e}")

    def fetch_data(self):
        try:
            tickets = []
            jira = self.jira

            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None

            jql_query = f"project = '{st.session_state['connection_jira'].get('project_name')}'"
            issues_found = jira.search_issues(jql_query)
            for item in issues_found:
                tickets.append(common_data.CommonData.from_jira_issue(item))
            return tickets
        except Exception as e:
            st.error(f"Error fetching data: {e}")
            return None

    def fetch_data_by_ids(self, ids):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None

            issues = []
            for issue_id in ids:
                issue = jira.issue(issue_id)
                if issue.fields.issuetype.name == "Story":
                    issues.append(work_item.WorkItem.from_jira_issue(issue))
                elif issue.fields.issuetype.name == "Test":
                    issues.append(test_case.TestCase.from_jira_issue(issue))
            return issues
        except Exception as e:
            st.error(f"Error fetching data by IDs: {e}")
            return None

    def add_work_item(self, title, description, acceptance_criteria, project_name):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None
            issue_dict = {
                'project': {'key': project_name},
                'summary': title,
                'description': description + "\n\nAcceptance Criteria:\n" + acceptance_criteria if acceptance_criteria else description,
                'issuetype': {'name': 'Story'}
            }
            new_issue = jira.create_issue(fields=issue_dict)
            st.success(f"Work item '{title}' created with ID: {new_issue.key}")
            return work_item.WorkItem.from_jira_issue(new_issue)
        except Exception as e:
            st.error(f"Failed to create work item: {e}")
            return None

    def fetch_work_item_by_id(self, work_item_id):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None

            issue = jira.issue(work_item_id)
            if issue.fields.issuetype.name == "Story":
                return work_item.WorkItem.from_jira_issue(issue)
            elif issue.fields.issuetype.name == "Test Case":
                return test_case.TestCase.from_jira_issue(issue)
            return None
        except Exception as e:
            st.error(f"Error fetching work item by ID: {e}")
            return None

    def fetch_work_item_commits_by_id(self, work_item_id):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None
            issue = jira.issue(work_item_id)
            work_item_obj = work_item.WorkItem.from_jira_issue(issue)
            remote_links = jira.remote_links(issue)
            commits_list = []
            for link in remote_links:
                if hasattr(link, 'object') and link.object.get('url', '').startswith('http'):
                    commit_data = commits.Commit.from_jira_remote_link(link)
                    if commit_data:
                        commits_list.append(commit_data)
            return {"work_item": work_item_obj, "commits": commits_list}
        except Exception as e:
            st.error(f"Failed to fetch commits for work item: {e}")
            print(f"Failed to fetch commits for work item: {e}")
            return None

    def update_work_item(self, work_item_id, title=None, description=None, acceptance_criteria=None):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None
            issue = jira.issue(work_item_id)
            fields_to_update = {}
            if title is not None:
                fields_to_update['summary'] = title
            if description is not None:
                fields_to_update['description'] = description
            if acceptance_criteria is not None:
                fields_to_update['customfield_10047'] = acceptance_criteria

            if fields_to_update:
                issue.update(fields=fields_to_update)
                st.success(f"Work item '{work_item_id}' updated successfully.")
                return work_item.WorkItem.from_jira_issue(issue)
            else:
                st.info("No fields to update.")
                return None
        except Exception as e:
            st.error(f"Failed to update work item: {e}")
            return None

    def update_work_item_tc(self, work_item_id, title=None, description=None, steps=None, parameters=None):
        try:
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None

            issue = jira.issue(work_item_id)
            fields_to_update = {}
            if title is not None:
                fields_to_update['summary'] = title
            if description is not None:
                fields_to_update['description'] = description
            if steps is not None:
                fields_to_update['customfield_10041'] = steps
            if parameters is not None:
                fields_to_update['customfield_10043'] = parameters

            if fields_to_update:
                issue.update(fields=fields_to_update)
                st.success(f"Test case '{work_item_id}' updated successfully.")
                return test_case.TestCase.from_jira_issue(issue)
            else:
                st.info("No fields to update.")
                return None
        except Exception as e:
            st.error(f"Failed to update test case: {e}")
            return None

    def update_work_item_with_test_cases(self, work_item_id, test_cases):
        try:
            test_cases = json.loads(test_cases) if isinstance(test_cases, str) else test_cases
            jira = self.jira
            if not jira:
                st.error("Jira connection settings or project name missing.")
                return None

            created_test_cases = []
            for tc in test_cases.get("test_cases", []):
                issue_dict = {
                    'project': {'key': self.session_state["connection_jira"].get("project_name")},
                    'summary': tc.get('title', ''),
                    'description': tc.get('description', ''),
                    'issuetype': {'name': 'Test Case'},
                    'customfield_10041': '\n'.join(tc.get('steps', '')),
                    'customfield_10043': '\n'.join(tc.get('parameters', ''))
                }
                try:
                    new_issue = jira.create_issue(fields=issue_dict)
                    jira.create_issue_link(
                        type='Relates',
                        inwardIssue=work_item_id,
                        outwardIssue=new_issue.key
                    )
                    st.success(f"Test case '{tc.get('title', '')}' created and linked to {work_item_id} with ID: {new_issue.key}")
                    created_test_cases.append(test_case.TestCase.from_jira_issue(new_issue))
                except Exception as e:
                    st.error(f"Failed to create test case '{tc.get('title', '')}': {e}")
            return created_test_cases
        except Exception as e:
            st.error(f"Error updating work item with test cases: {e}")
            return None

    def update_work_item_with_test_results(self, work_item_id, test_results):
        try:
            # Not implemented
            st.info("update_work_item_with_test_results not implemented.")
        except Exception as e:
            st.error(f"Error in update_work_item_with_test_results: {e}")

    def get_commit_details(self, commit_url, project_name):
        try:
            # Not implemented
            st.info("get_commit_details not implemented.")
        except Exception as e:
            st.error(f"Error in get_commit_details: {e}")

    def get_git_commit_content(self, repo_url, project_name):
        try:
            # Not implemented
            st.info("get_git_commit_content not implemented.")
        except Exception as e:
            st.error(f"Error in get_git_commit_content: {e}")

    jira = None