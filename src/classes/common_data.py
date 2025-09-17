class CommonData:
    def __init__(self, id=None, title=None, state=None, assigned_to=None, type=None, description=None, acceptance_criteria=None, status=None):
        self.id = id
        self.title = title
        self.state = state
        self.assigned_to = assigned_to
        self.type = type
        self.description = description
        self.acceptance_criteria = acceptance_criteria
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "state": self.state,
            "assigned_to": self.assigned_to,
            "type": self.type,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "status": self.status
        }
    
    def __str__(self):
        return (
            f"CommonData(id={self.id}, title={self.title}, state={self.state}, "
            f"assigned_to={self.assigned_to}, type={self.type}, description={self.description}, "
            f"acceptance_criteria={self.acceptance_criteria}, status={self.status})"
        )
    
    @staticmethod
    def from_azure_devops(item):
        common_data = CommonData()
        common_data.id = item.id
        common_data.title = item.fields.get("System.Title", "")
        common_data.state = item.fields.get("System.State", "")
        common_data.assigned_to = item.fields.get("System.AssignedTo", "")
        common_data.type = item.fields.get("System.WorkItemType", "")
        common_data.description = item.fields.get("System.Description", "")
        common_data.acceptance_criteria = item.fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", "")
        common_data.status = item.fields.get("System.Status", "")
        return common_data
    
    @staticmethod
    def from_jira_issue(item):
        common_data = CommonData()
        common_data.id = item.key
        common_data.title = item.fields.summary
        common_data.state = item.fields.status.name
        common_data.assigned_to = item.fields.assignee
        common_data.type = item.fields.issuetype.name
        common_data.description = item.fields.description
        common_data.acceptance_criteria = item.fields.customfield_10047
        common_data.status = getattr(item.fields, "status", None)
        return common_data