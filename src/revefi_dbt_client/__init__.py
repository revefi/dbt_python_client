__version__ = '0.1.1'

from revefi_dbt_client.config import Config
from revefi_dbt_client.logging import configure_logging

configure_logging(Config.get_log_level())
