class HistoryData:
    def __init__(self, fields):
        self.fields = fields  # Dictionary of all fields

    def to_dict(self):
        result = self.fields.copy()
        return result

    @staticmethod
    def from_azure_devops(entry):
        field_names = [
            'System.Id', 'System.AreaId', 'System.NodeName', 'System.AreaLevel1', 'System.Rev',
            'System.IterationLevel1',
            'System.WorkItemType', 'System.State', 'System.Reason', 'System.AssignedTo', 'System.CreatedDate',
            'System.CreatedBy', 'System.ChangedDate', 'System.ChangedBy', 'System.AuthorizedAs', 
            'System.IsDeleted', 'System.CommentCount', 'System.TeamProject', 'System.AreaPath',
            'System.IterationPath', 'Microsoft.VSTS.Common.StateChangeDate', 'System.Title', 'System.Description',
            'Microsoft.VSTS.Common.AcceptanceCriteria', 'System.Tags'
        ]
        fields = {}
        if entry.fields:
            for name in field_names:
                field_obj = entry.fields.get(name)
                fields[name] = field_obj.__dict__ if field_obj else None
            return HistoryData(fields=fields)
