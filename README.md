Revefi integrates with dbt Core to help connect the dots between your data issues and your dbt models [e.g. model code changes]. 

Follow the steps below to set up the integration:

- Make sure you have python (version 3.8 or above) installed on your machine

- Run pip install git+https://github.com/revefi/dbt_python_client.git to install the revefi-dbt-client package

- Separately, you will have received a Revefi Auth token; keep that in a secure place (like your password manager)

- In a terminal, run the command `python3 -m revefi-dbt-client.upload dbt --token <auth-token> --target_folder <target-folder>`, where `<auth-token>` is the token you received in Step b) above and `<target-folder>` is 
the Target folder you used for your dbt run
