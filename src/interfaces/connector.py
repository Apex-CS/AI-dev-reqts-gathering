from abc import ABC, abstractmethod

class ConnectorInterface(ABC):
    @abstractmethod
    def change_connection(self, base_url, project_name, personal_access_token, user_email=None):
        pass

    @abstractmethod
    def get_connection(self):
        pass

    @abstractmethod
    def get_wit_client(self):
        pass

    @abstractmethod
    def get_git_client(self):
        pass

    @abstractmethod
    def fetch_data(self):
        pass

    @abstractmethod
    def fetch_data_by_ids(self, ids):
        pass

    @abstractmethod
    def add_work_item(self, title, description, acceptance_criteria, project_name):
        pass

    @abstractmethod
    def fetch_work_item_by_id(self, work_item_id):
        pass

    @abstractmethod
    def fetch_work_item_commits_by_id(self, work_item_id):
        pass

    @abstractmethod
    def update_work_item(self, work_item_id, title=None, description=None, acceptance_criteria=None):
        pass

    @abstractmethod
    def update_work_item_tc(self, work_item_id, title=None, description=None, steps=None, parameters=None):
        pass

    @abstractmethod
    def update_work_item_with_test_cases(self, work_item_id, test_cases):
        pass

    @abstractmethod
    def update_work_item_with_test_results(self, work_item_id, test_results):
        pass

    @abstractmethod
    def get_commit_details(self, commit_url, project_name):
        pass

    @abstractmethod
    def get_git_commit_content(self, repo_url, project_name):
        pass
    
    @abstractmethod
    def get_work_item_history(self, work_item_id):
        pass
