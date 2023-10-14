import logging
import sys
import textwrap

from revefi_dbt_client.parser import parse_args_legacy, parse_args_v2
from revefi_dbt_client.upload import upload

LOG = logging.getLogger(__name__)


def main(legacy_parser=False):
    argv = sys.argv[1:]

    if legacy_parser:
        LOG.warning(textwrap.dedent("""
                                       Using legacy parser,
                                       please update how CLI is invoked as per the documentation: https://github.com/revefi/dbt_python_client"""))
        args = parse_args_legacy(argv)
    else:
        args = parse_args_v2(argv)

    upload(args.token, args.project_folder, args.target_folder, args.logs_folder)


if __name__ == "__main__":
    main()
