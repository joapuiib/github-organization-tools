class User:
    def __init__(self, id="", username="", repo="", description=""):
        self.id = id
        self.username = username
        self.repo = repo
        self.description = description

    def is_valid(self):
        return self.id

    def __eq__(self, other):
        return (
            self.id == other.id and
            self.username == other.username and
            self.repo == other.repo and
            self.description == other.description
        )

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, repo={self.repo}, description={self.description})"
