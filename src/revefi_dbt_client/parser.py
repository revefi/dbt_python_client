import argparse


def _add_parser_args(parser: argparse.ArgumentParser):
    parser.add_argument("--token", required=True, type=str, help="validation token")
    parser.add_argument("--project_folder", required=True, type=str, help="dbt project folder")
    parser.add_argument("--target_folder", required=False, type=str, help="target folder for the dbt run")
    parser.add_argument("--logs_folder", required=False, type=str, help="log folder from the dbt run")


def parse_args_legacy(argv):
    parser = argparse.ArgumentParser(description="revefi dbt cli")
    subparsers = parser.add_subparsers(dest='command')
    dbt_parser = subparsers.add_parser('dbt')
    _add_parser_args(dbt_parser)
    args = parser.parse_args(argv)
    return args


def parse_args_v2(argv):
    parser = argparse.ArgumentParser(description="revefi dbt cli")
    _add_parser_args(parser)
    args = parser.parse_args(argv)
    return args
