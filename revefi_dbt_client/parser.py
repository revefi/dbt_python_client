import argparse


def parse_args(argv):
    parser = argparse.ArgumentParser(description="revefi dbt cli")
    subparsers = parser.add_subparsers(dest='command')
    dbt_parser = subparsers.add_parser('dbt')
    dbt_parser.add_argument("--token", required=True, type=str, help="validation token")
    dbt_parser.add_argument("--project_folder", required=True, type=str, help="dbt project folder")
    dbt_parser.add_argument("--target_folder", required=False, type=str, help="target folder for the dbt run")
    dbt_parser.add_argument("--logs_folder", required=False, type=str, help="log folder from the dbt run")
    dbt_parser.add_argument("--endpoint", required=False, type=str, help="endpoint for API")
    args = parser.parse_args(argv)
    return args
