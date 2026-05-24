"""Client order ID generation utilities for Hummingbot connectors.

Functions for generating unique client order IDs (string and numeric)
used to track orders submitted to exchanges.
"""

from __future__ import annotations

import os
import platform
import time
from hashlib import md5

from connector_utils.trading_pair import split_hb_trading_pair


def _bot_instance_id() -> str:
    fingerprint = f"{platform.uname()}_pid:{os.getpid()}_ppid:{os.getppid()}"
    return md5(fingerprint.encode(), usedforsecurity=False).hexdigest()


def get_new_client_order_id(
    is_buy: bool,
    trading_pair: str,
    hbot_order_id_prefix: str = "",
    max_id_len: int | None = None,
    *,
    nonce: int | None = None,
) -> str:
    """
    Creates a client order id for a new order

    Note: If the need for much shorter IDs arises, an option is to concatenate
    the host name, the PID, and the nonce, and hash the result.

    :param is_buy: True if the order is a buy order, False otherwise
    :param trading_pair: the trading pair the order will be operating with
    :param hbot_order_id_prefix: The hummingbot-specific identifier for the given exchange
    :param max_id_len: The maximum length of the ID string.
    :param nonce: Optional nonce override (defaults to time.time_ns()). Inject
        hummingbot's get_tracking_nonce() here to preserve exact upstream semantics.
    :return: an identifier for the new order to be used in the client
    """
    if nonce is None:
        nonce = time.time_ns()
    side = "B" if is_buy else "S"
    symbols = split_hb_trading_pair(trading_pair)
    base = symbols[0].upper()
    quote = symbols[1].upper()
    base_str = f"{base[0]}{base[-1]}"
    quote_str = f"{quote[0]}{quote[-1]}"
    client_instance_id = _bot_instance_id()
    ts_hex = hex(nonce)[2:]
    raw_id = f"{hbot_order_id_prefix}{side}{base_str}{quote_str}{ts_hex}{client_instance_id}"
    client_order_id = raw_id.replace("$", "")

    if max_id_len is not None:
        id_prefix = f"{hbot_order_id_prefix}{side}{base_str}{quote_str}"
        suffix_max_length = max_id_len - len(id_prefix)
        if suffix_max_length < len(ts_hex):
            id_suffix = md5(
                f"{ts_hex}{client_instance_id}".encode(), usedforsecurity=False
            ).hexdigest()
            client_order_id = f"{id_prefix}{id_suffix[:suffix_max_length]}"
        else:
            client_order_id = client_order_id[:max_id_len]
    return client_order_id


def get_new_numeric_client_order_id(
    max_id_bit_count: int | None = None,
    *,
    nonce: int | None = None,
) -> int:
    """
    Creates a numeric client order id for a new order.

    The ID is formed by decimal-string-concatenating the integer representation of
    the MD5 host fingerprint with the nonce, then masking to max_id_bit_count bits
    if requested. This preserves the exact upstream format from hummingbot.connector.utils.

    :param max_id_bit_count: Optional maximum bit width for the returned integer.
    :param nonce: Optional nonce override (defaults to time.time_ns()). Inject
        hummingbot's NonceCreator.get_tracking_nonce() here to preserve exact
        upstream semantics.
    :return: a numeric identifier for the new order
    """
    if nonce is None:
        nonce = time.time_ns()
    hexa_hash = _bot_instance_id()
    host_part = int(hexa_hash, 16)
    client_order_id = int(f"{host_part}{nonce}")
    if max_id_bit_count:
        max_int = 2**max_id_bit_count - 1
        client_order_id &= max_int
    return client_order_id
