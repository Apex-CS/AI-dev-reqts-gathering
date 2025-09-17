class Commits:
    def __init__(self, comment: str, remote_url: str, id: str = "", repository_id: str = ""):
        self.comment = comment
        self.remote_url = remote_url
        self.id = id
        self.repository_id = repository_id

    def to_dict(self):
        return {
            "comment": self.comment,
            "remote_url": self.remote_url,
            "id": self.id,
            "repository_id": self.repository_id
        }
    
    def __str__(self):
        return f"Commits(comment={self.comment}, remote_url={self.remote_url}, id={self.id}, repository_id={self.repository_id})"

    @classmethod
    def from_azure_devops(cls, item, repository_id):
        return cls(
            comment=item.comment,
            remote_url=item.remote_url,
            id=item.commit_id,
            repository_id=repository_id
        )