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
        return f"CSVUserLoader(pattern_id={self.pattern_id}, pattern_username={self.pattern_username}, pattern_repo={self.pattern_repo}, pattern_description={self.pattern_description})"


    def load(self, path):
        return [ self.map(row) for _, row in self.rows(path) ]


    def rows(self, path):
        """
        Yields (line number, row) for each data row, loading the schema from the header.
        """
        try:
            # utf-8-sig also strips the BOM added by Excel
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.reader(f, delimiter=',')
                header = next(reader)
                self.load_schema(header)
                for row in reader:
                    # Missing trailing columns are treated as empty
                    row += [''] * (len(header) - len(row))
                    yield reader.line_num, row
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
