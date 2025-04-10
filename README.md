# Revefi DBT Python Client

[![Install and Test](https://github.com/revefi/dbt_python_client/actions/workflows/install_and_test.yaml/badge.svg)](https://codecov.io/gh/revefi/dbt_python_client)
[![CodeQL](https://github.com/revefi/dbt_python_client/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/revefi/dbt_python_client/actions/workflows/github-code-scanning/codeql)
[![codecov](https://codecov.io/gh/revefi/dbt_python_client/graph/badge.svg?token=A6YWWOWA6L)](https://codecov.io/gh/revefi/dbt_python_client)

Revefi integrates with dbt Core to help connect the dots between your data issues and your dbt
models [e.g. model code changes].

### Pre-requisites
- Python 3.8 or higher

### Set up the integration:

- Run the following command to install the revefi-dbt-client package
  ```shell
  pip install git+https://github.com/revefi/dbt_python_client.git
  ```

- Separately, you will have received a Revefi Auth token; keep that in a secure place (like your password manager)

- Once installed, run the following command in the terminal
  ```shell
  revefi-dbt-client --token <auth-token> --project_folder <project-folder>
  ```
  where 
  - `<auth-token>` is the token you received in Step b) above
  - `<project-folder>` is the Project folder you have created for the dbt.

#### Unit test

For unit testing, run the following commands
```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

#### Note

- The uploader assumes that the dbt target path is set to `target` within the project folder. If you are using some other
target path, you may override the default behavior with `--target_folder <target-folder>`
