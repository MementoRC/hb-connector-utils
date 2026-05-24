"""Shared utilities for connector implementations across Hummingbot sub-packages."""

from connector_utils.__about__ import __version__
from connector_utils.client_order_id import get_new_client_order_id, get_new_numeric_client_order_id
from connector_utils.trading_pair import (
    combine_to_hb_trading_pair,
    split_hb_trading_pair,
    validate_trading_pair,
)

__all__ = [
    "__version__",
    "split_hb_trading_pair",
    "combine_to_hb_trading_pair",
    "validate_trading_pair",
    "get_new_client_order_id",
    "get_new_numeric_client_order_id",
]
