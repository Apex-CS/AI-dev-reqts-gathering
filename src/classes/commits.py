class Commits:
    def __init__(self, comment: str, remote_url: str, id: str = ""):
        self.comment = comment
        self.remote_url = remote_url
        self.id = id

    def to_dict(self):
        return {
            "comment": self.comment,
            "remote_url": self.remote_url,
            "id": self.id
        }
    
    def __str__(self):
        return f"Commits(comment={self.comment}, remote_url={self.remote_url}, id={self.id})"

    @classmethod
    def from_azure_devops(cls, item):
        return cls(
            comment=item.comment,
            remote_url=item.remote_url,
            id=item.commit_id
        )