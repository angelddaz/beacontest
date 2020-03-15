from github import Github
import pandas as pd
import boto3
from io import StringIO

class ExtractContributors(object):
    def __init__(self, token=None, repos=None, s3_bucket=None):
        self.token = token
        self.repos = repos
        self.s3_bucket = s3_bucket
    
    def __call__(self):
        """
        Extracts contributor data based on constant column definitions
        
        API Endpoint being used:
        https://developer.github.com/v3/repos/#list-contributors
        """
        g = Github(self.token)
        repos_obj = g.get_repo(self.repos)
        contributors = repos_obj.get_contributors()

        df = pd.DataFrame(
            columns=["company", "contributions", "email", "id", "login", "name",]
        )

        for i, user in enumerate(contributors, start=0):
            df.set_value(i, "company", user.company)
            df.set_value(i, "contributions", user.contributions)
            df.set_value(i, "email", user.email)
            df.set_value(i, "id", user.id)
            df.set_value(i, "login", user.login)
            df.set_value(i, "name", user.name)

            # added break because of rate limits
            if i == 10:
                break

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_resource = boto3.resource("s3")
        s3_resource.Object(self.s3_bucket, "contributors.csv").put(Body=csv_buffer.getvalue())
        return True

class ExtractOpenIssues(object):
    def __init__(self, token=None, repos=None, s3_bucket=None):
        self.token = token
        self.repos = repos
        self.s3_bucket = s3_bucket
    
    def __call__(self):
        """
        Extracts open issues titles and numbers for a given repository.

        API Endpoint being used:
        https://developer.github.com/v3/issues/
        """
        g = Github(self.token)
        repos_obj = g.get_repo(self.repos)
        issues = repos_obj.get_issues(state="open")

        df = pd.DataFrame(columns=["title", "number"])

        for i, issue in enumerate(issues, start=0):
            df.set_value(i, "title", issue.title)
            df.set_value(i, "number", issue.number)
            if i == 10:
                break

        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3_resource = boto3.resource("s3")
        s3_resource.Object(self.s3_bucket, "openissues.csv").put(Body=csv_buffer.getvalue())
        return True
        
