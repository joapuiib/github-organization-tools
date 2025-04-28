import csv

from .user import User
from .pattern_formatter import PatternFormatter


class CSVUserLoader:
    def __init__(
            self,
            pattern_id="",
            pattern_username="",
            pattern_repo="",
            pattern_description="",
    ):
        self.pattern_id = pattern_id
        self.pattern_username = pattern_username
        self.pattern_repo = pattern_repo
        self.pattern_description = pattern_description

        self.schema = {}
        self.formatter = PatternFormatter()


    def __repr__(self):
        return f"CSVUserLoader(pattern_id={self.pattern_id}, pattern_username={self.pattern_username}, pattern_repo={self.pattern_repo}, pattern_description={self.pattern_description}, lower_id={self.lower_id}, remove_accents={self.remove_accents})"


    def load(self, path):
        try:
            with open(path, newline='') as f:
                reader = csv.reader(f, delimiter=',')
                header = next(reader)
                self.load_schema(header)
                return [ self.map(row) for row in reader ]
        except FileNotFoundError:
            print(f"Could not find file: {path}")
            exit(1)


    def load_schema(self, header):
        self.schema = {name: idx for idx, name in enumerate(header)}
        self.formatter.schema = self.schema


    def map(self, row):
        """
        Maps a CSV line to a User object.
        """
        return User(**{
            "id": self.formatter.format(self.pattern_id, row),
            "username": self.formatter.format(self.pattern_username, row),
            "repo": self.formatter.format(self.pattern_repo, row),
            "description": self.formatter.format(self.pattern_description, row),
        })
