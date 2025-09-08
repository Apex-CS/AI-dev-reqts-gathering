class WorkItem:
    def __init__(self, title: str, description: str, acceptance_criteria: str, id: int = None, relations=None):
        self.id = id
        self.title = title
        self.description = description
        self.acceptance_criteria = acceptance_criteria
        self.relations = relations if relations is not None else []

    def __repr__(self):
        return (f"WorkItem(id={self.id!r}, "
                f"title={self.title!r}, "
                f"description={self.description!r}, "
                f"acceptance_criteria={self.acceptance_criteria!r}, "
                f"relations={self.relations!r})")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "relations": self.relations
        }
    
    @staticmethod
    def from_dict(data: dict):
        return WorkItem(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            acceptance_criteria=data.get("acceptance_criteria", ""),
            relations=data.get("relations", [])
        )

    def update(self, title=None, description=None, acceptance_criteria=None, id=None, relations=None):
        if id is not None:
            self.id = id
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if acceptance_criteria is not None:
            self.acceptance_criteria = acceptance_criteria
        if relations is not None:
            self.relations = relations

    @staticmethod
    def from_azure_devops(item):
        fields = item.fields
        relations = getattr(item, "relations", [])
        return WorkItem(
            id=item.id,
            title=fields.get("System.Title", ""),
            description=fields.get("System.Description", ""),
            acceptance_criteria=fields.get("Microsoft.VSTS.Common.AcceptanceCriteria", ""),
            relations=item.relations
        )

    def from_jira_issue(item):
        return WorkItem(
            id=item.key,
            title=item.fields.summary,
            description=item.fields.description,
            acceptance_criteria=item.fields.customfield_10047,
            relations=item.fields.issuelinks
        )

    def summarize(self):
        return (f"Work Item ID: {self.id}\n"
                f"Title: {self.title}\n"
                f"Description: {self.description}\n"
                f"Acceptance Criteria: {self.acceptance_criteria}\n"
                f"Relations: {self.relations}")