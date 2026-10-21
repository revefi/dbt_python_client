from importlib.metadata import version

from revefi_dbt_client.config import Config
from revefi_dbt_client.logging import configure_logging

__version__ = version("revefi-dbt-client")

configure_logging(Config.get_log_level())
