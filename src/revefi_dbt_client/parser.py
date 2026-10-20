import argparse

from revefi_dbt_client.config import Config


def _add_parser_args(parser: argparse.ArgumentParser):
    parser.add_argument("--token", required=True, type=str, help="validation token")
    parser.add_argument("--project_folder", required=True, type=str, help="dbt project folder")
    parser.add_argument("--target_folder", required=False, type=str, help="target folder for the dbt run")
    parser.add_argument("--logs_folder", required=False, type=str, help="log folder from the dbt run")
    parser.add_argument("--ignore-errors", required=False, action=argparse.BooleanOptionalAction,
                        default=Config.get_ignore_errors(),
                        help="when set, the client will exit with exitCode 0 even if an error occurs")
    parser.add_argument("--max-retries", required=False, type=int, default=Config.get_max_retries(),
                        help="maximum number of times to retry the upload after a failure")
    parser.add_argument("--max-retry-wait-seconds", required=False, type=int, default=Config.get_max_retry_wait_seconds(),
                        help="maximum total time in seconds to keep retrying the upload")


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
