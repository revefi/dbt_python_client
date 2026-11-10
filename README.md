# Revefi DBT Python Client

[![Install and Test](https://github.com/revefi/dbt_python_client/actions/workflows/install_and_test.yaml/badge.svg)](https://codecov.io/gh/revefi/dbt_python_client)
[![CodeQL](https://github.com/revefi/dbt_python_client/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/revefi/dbt_python_client/actions/workflows/github-code-scanning/codeql)
[![codecov](https://codecov.io/gh/revefi/dbt_python_client/graph/badge.svg?token=A6YWWOWA6L)](https://codecov.io/gh/revefi/dbt_python_client)

Revefi integrates with dbt Core to help connect the dots between your data issues and your dbt
models [e.g. model code changes].

### Pre-requisites

- Python 3.9

> [!NOTE]
> Python 3.9 is supported only on the `main-python-3-9` branch. For Python 3.10 and newer, install from the
> [`main`](https://github.com/revefi/dbt_python_client/tree/main) branch instead.

### Set up the integration:

- Run the following command with your Python 3.9 interpreter to install the `revefi-dbt-client` package from the
  `main-python-3-9` branch:

  ```shell
  python3.9 -m pip install "git+https://github.com/revefi/dbt_python_client.git@main-python-3-9"
  ```

  The `@main-python-3-9` suffix is required: without it, pip installs from `main`, which does not support Python 3.9.

- Separately, you will have received a Revefi Auth token; keep that in a secure place (like your password manager)

- Once installed, run the following command in the terminal
  ```shell
  revefi-dbt-client --token <auth-token> --project_folder <project-folder>
  ```
  where 
  - `<auth-token>` is the token you received in Step b) above
  - `<project-folder>` is the Project folder you have created for the dbt.

#### Unit test

Contributors need [uv](https://docs.astral.sh/uv/getting-started/installation/). Check out the `main-python-3-9`
branch, then run the unit tests:

```shell
git clone --branch main-python-3-9 https://github.com/revefi/dbt_python_client.git
cd dbt_python_client
uv sync --locked
uv run pytest
```

#### Note

- The uploader assumes that the dbt target path is set to `target` within the project folder. If you are using some other
target path, you may override the default behavior with `--target_folder <target-folder>`
