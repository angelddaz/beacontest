# beacontest
Extracting Github Data into Redshift

## Data Pipeline with Airfow

This project's purpose is to extract contributor and open issue data from a given repositoy, into cloud storage. From cloud storage, the data is then loaded into a Redshift database.
The tables generated are; `airflow_contributors` and `airflow_open_issues`.

### Endpoints used
#### Contributors data
PyGithub:
* https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.get_contents

Github REST API:
* https://developer.github.com/v3/repos/#list-contributors


#### Issues data
PyGithub: 
* https://pygithub.readthedocs.io/en/latest/github_objects/Repository.html#github.Repository.Repository.get_issues_comments

Github REST API: 
* https://developer.github.com/v3/issues/

### Redshift Tables and Data Model Generated
### Tables
* `airflow_contributors`
* `airflow_open_issues`

### Rough Data Model
`airflow_contributors` columns:
* colname, data type
* company, text
* contributions, int
* email, text
* id, bigint
* login, text
* name, text

`airflow_open_issues` columns:
* colname, data type
* title, text
* number, int

### Dependencies

You will need to install Airflow and run the scheduler
* `pip install -r requirements.txt`
* `airflow scheduler`
* I am using python version 3.6.9
* aws credentials stored in `~/.aws/credentials`

### Sensitive Variables and Connections
Airflow Variables and Connections can store encrypted credentials.
There is a `create_conns_and_vars.sh` executable bash script not in this repository, but in the parent directory `~/airflow/` from the ec2 instance from which this code is being pushed from.
This bash script will load sensitive Variables and connections.

### Local Postgres database for webserver to run on
I set up a local postgres database for which the airflow webserver to run on.
An issue I ran into was that my bash session was not being loaded with the most up to date configurations in `~/airflow/airflow.cfg`.
I had to manually add the logging database in a `~/.bashrc` file in order for logging to go to a local database with user `airflow` and password included in `~/.bashrc` file.

### S3 Logging
S3 Logging is configured in `airflow.cfg` seemingly correctly, but I ran into a similar issue as the postgres database not being loaded by `airflow.cfg`.
I did not find a manual override for this logging to execute on the given s3 connection so this aspect of the test did not execute correctly.

### Coding Style test
I follow PEP8 standards which can be automatically implemented using the black command:
`black filename.py`

## Permissions
You will need to be a part of users on the ec2 instance to run these DAGs.
