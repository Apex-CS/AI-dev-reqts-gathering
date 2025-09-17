class CommentData:
    def __init__(self, fields):
        self.created_by = None
        self.created_date = None
        self.modified_date = None
        self.text = None
        self.mentions = None
            

    def to_dict(self):
        result = {
            "created_by": self.created_by,
            "created_date": self.created_date,
            "modified_date": self.modified_date,
            "text": self.text,
            "mentions": self.mentions
        }
        return result
        
    @staticmethod
    def from_azure_devops(entry):
        comment = CommentData(fields={})
        comment.created_by = getattr(getattr(entry, 'created_by', {}), 'displayName', '')
        comment.created_date = getattr(entry, 'created_date', '') if entry else ''
        comment.modified_date = getattr(entry, 'modified_date', '') if entry else ''
        comment.text = getattr(entry, 'text', '') if entry else ''
        mentions = getattr(entry, 'mentions', []) if entry else []
        comment.mentions = [getattr(mention, 'displayName', '') for mention in mentions] if mentions else []
        return comment