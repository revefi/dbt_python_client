import sys

from revefi_dbt_client.parser import parse_args
from revefi_dbt_client.upload import upload


def main(argv):
    args = parse_args(argv)
    upload(args.token, args.project_folder, args.target_folder, args.logs_folder, args.endpoint)


if __name__ == "__main__":
    main(sys.argv[1:])
