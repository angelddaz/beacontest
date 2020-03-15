from airflow import DAG

# variables and config imports
from airflow.models import Variable
from datetime import datetime, timedelta

# operator imports
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

# local imports
# import ipdb;ipdb.set_trace()
from github_extract import ExtractContributors, ExtractOpenIssues

# setting variables
S3_CONN_ID = "s3conn"
REDSHIFT_CONN_ID = "redshiftconn"
AUTH_TOKEN = Variable.get("githubtoken")
S3_BUCKET = Variable.get("s3bucket")
AWS_ACCESS_KEY = Variable.get("s3login")
AWS_SECRET_ACCESS_KEY = Variable.get("s3pw")

# Hard coded variable
REPOSITORY = "apache/airflow"

# setting DAG config
default_args = {
    "depends_on_past": False,
    "start_date": datetime(2020, 3, 13),
    "email_on_retry": False,
    "retries": 1,
    "concurrency": 1,
    "retry_delay": timedelta(minutes=1),
}

# dag start
with DAG(
    "gh_to_redshift", default_args=default_args, schedule_interval=None
) as dag:

    d = DummyOperator(task_id="kick_off_dag")

    # Extract API data from github into s3
    # import ipdb; ipdb.set_trace()
    extract_contributors_to_s3 = PythonOperator(
        task_id="contributors_extract",
        python_callable=ExtractContributors(
            AUTH_TOKEN, REPOSITORY, S3_BUCKET
        )
    )

    # import ipdb; ipdb.set_trace()
    extract_issues_to_s3 = PythonOperator(
        task_id="issues_extract",
        python_callable=ExtractOpenIssues(
            AUTH_TOKEN, REPOSITORY, S3_BUCKET
        )
    )

    # list of sql commands to execute in s3->redshift load
    # 0. drop table for idempotency
    sql_cmds = []
    sql_cmds.append(
        """
        DROP TABLE IF EXISTS airflow_contributors;
        """
    )

    sql_cmds.append(
        """
        DROP TABLE IF EXISTS airflow_open_issues;
        """
    )

    # 1. create two tables
    sql_cmds.append(
        """
        CREATE TABLE airflow_contributors (
            company TEXT,
            contributions INT,
            email TEXT,
            id BIGINT,
            login TEXT,
            name TEXT
        );
        """
    )

    sql_cmds.append(
        """
        CREATE TABLE airflow_open_issues (
            title TEXT,
            number INT
        );
        """
    )

    # 2. load tables with small s3 csvs
    sql_cmds.append(
        """
        COPY airflow_contributors
        FROM 's3://{s3_bucket}/contributors.csv'
        CREDENTIALS 'aws_access_key_id={s3_login};aws_secret_access_key={s3_pw}'
        CSV
        IGNOREHEADER 1;
        """.format(
            s3_bucket=S3_BUCKET, s3_login=AWS_ACCESS_KEY, s3_pw=AWS_SECRET_ACCESS_KEY,
        )
    )

    sql_cmds.append(
        """
        COPY airflow_open_issues
        FROM 's3://{s3_bucket}/openissues.csv'
        CREDENTIALS 'aws_access_key_id={s3_login};aws_secret_access_key={s3_pw}'
        CSV
        IGNOREHEADER 1;
        """.format(
            s3_bucket=S3_BUCKET, s3_login=AWS_ACCESS_KEY, s3_pw=AWS_SECRET_ACCESS_KEY,
        )
    )

    # execute list of Redshift sql commands with PostgresOperator
    s3_load_to_redshift = PostgresOperator(
        task_id="load_to_redshift", sql=sql_cmds, postgres_conn_id=REDSHIFT_CONN_ID,
    )

    # DAG Task Ordering
    d >> extract_contributors_to_s3 >> extract_issues_to_s3 >> s3_load_to_redshift
