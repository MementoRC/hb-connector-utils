"""Client order ID generation utilities for Hummingbot connectors.

Functions for generating unique client order IDs (string and numeric)
used to track orders submitted to exchanges.
"""

import os
import platform
from hashlib import md5

from async_utils import NonceCreator, get_tracking_nonce

from connector_utils.trading_pair import split_hb_trading_pair


def _bot_instance_id() -> str:
    return md5(f"{platform.uname()}_pid:{os.getpid()}_ppid:{os.getppid()}".encode("utf-8")).hexdigest()


def get_new_client_order_id(
    is_buy: bool, trading_pair: str, hbot_order_id_prefix: str = "", max_id_len: int | None = None
) -> str:
    """
    Creates a client order id for a new order

    Note: If the need for much shorter IDs arises, an option is to concatenate the host name, the PID,
    and the nonce, and hash the result.

    :param is_buy: True if the order is a buy order, False otherwise
    :param trading_pair: the trading pair the order will be operating with
    :param hbot_order_id_prefix: The hummingbot-specific identifier for the given exchange
    :param max_id_len: The maximum length of the ID string.
    :return: an identifier for the new order to be used in the client
    """
    side = "B" if is_buy else "S"
    symbols = split_hb_trading_pair(trading_pair)
    base = symbols[0].upper()
    quote = symbols[1].upper()
    base_str = f"{base[0]}{base[-1]}"
    quote_str = f"{quote[0]}{quote[-1]}"
    client_instance_id = _bot_instance_id()
    ts_hex = hex(get_tracking_nonce())[2:]
    client_order_id = f"{hbot_order_id_prefix}{side}{base_str}{quote_str}{ts_hex}{client_instance_id}".replace("$", "")

    if max_id_len is not None:
        id_prefix = f"{hbot_order_id_prefix}{side}{base_str}{quote_str}"
        suffix_max_length = max_id_len - len(id_prefix)
        if suffix_max_length < len(ts_hex):
            id_suffix = md5(f"{ts_hex}{client_instance_id}".encode()).hexdigest()
            client_order_id = f"{id_prefix}{id_suffix[:suffix_max_length]}"
        else:
            client_order_id = client_order_id[:max_id_len]
    return client_order_id


def get_new_numeric_client_order_id(nonce_creator: NonceCreator, max_id_bit_count: int | None = None) -> int:
    hexa_hash = _bot_instance_id()
    host_part = int(hexa_hash, 16)
    client_order_id = int(f"{host_part}{nonce_creator.get_tracking_nonce()}")
    if max_id_bit_count:
        max_int = 2**max_id_bit_count - 1
        client_order_id &= max_int
    return client_order_id
