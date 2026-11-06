"""Parity tests against the in-tree hummingbot client order id functions.

Addresses MementoRC/hb-connector-utils#20.

The ``_ref_*`` functions below are verbatim copies of the functions in
``hummingbot/connector/utils.py``, with the nonce source replaced by an
argument (the package must not import hummingbot or async-utils). Output of
``connector_utils.client_order_id`` must be byte-identical to them for the same
nonce.
"""

import inspect
import os
import platform
import time
from hashlib import md5

import pytest

from connector_utils import client_order_id as coid
from connector_utils.client_order_id import (
    get_new_client_order_id,
    get_new_numeric_client_order_id,
)

_NONCES = [1, 1640001112223334, 1640001112223334567]
_FIXED_HOST = "0123456789abcdef0123456789abcdef"


def _ref_bot_instance_id() -> str:
    return md5(
        f"{platform.uname()}_pid:{os.getpid()}_ppid:{os.getppid()}".encode(),
        usedforsecurity=False,
    ).hexdigest()


def _ref_get_new_client_order_id(
    nonce, is_buy, trading_pair, hbot_order_id_prefix="", max_id_len=None
):
    side = "B" if is_buy else "S"
    symbols = trading_pair.split("-")
    base = symbols[0].upper()
    quote = symbols[1].upper()
    base_str = f"{base[0]}{base[-1]}"
    quote_str = f"{quote[0]}{quote[-1]}"
    client_instance_id = _ref_bot_instance_id()
    ts_hex = hex(nonce)[2:]
    client_order_id = (
        f"{hbot_order_id_prefix}{side}{base_str}{quote_str}{ts_hex}{client_instance_id}"
    ).replace("$", "")
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


def _ref_get_new_numeric_client_order_id(nonce, max_id_bit_count=None):
    hexa_hash = _ref_bot_instance_id()
    host_part = int(hexa_hash, 16)
    client_order_id = int(f"{host_part}{nonce}")
    if max_id_bit_count:
        max_int = 2**max_id_bit_count - 1
        client_order_id &= max_int
    return client_order_id


class _MonotonicMicroNonce:
    """Mimics hummingbot's NonceCreator (microsecond, strictly increasing)."""

    def __init__(self):
        self._last = 0

    def get_tracking_nonce(self) -> int:
        nonce = max(time.time_ns() // 1000, self._last + 1)
        self._last = nonce
        return nonce


class TestClientOrderIdParity:
    """get_new_client_order_id must be byte-identical to the in-tree version."""

    @pytest.mark.parametrize("nonce", _NONCES)
    @pytest.mark.parametrize("is_buy", [True, False])
    @pytest.mark.parametrize("trading_pair", ["HBOT-COINALPHA", "BTC-USDT", "a-b"])
    @pytest.mark.parametrize("prefix", ["", "hbot", "x$y"])
    @pytest.mark.parametrize(
        "max_id_len",
        [
            None,  # no limit
            1000,  # large value, no truncation
            30,  # plain truncation (suffix_max_length >= len(ts_hex))
            12,  # md5 suffix path (suffix_max_length < len(ts_hex))
        ],
    )
    def test_matches_in_tree(self, nonce, is_buy, trading_pair, prefix, max_id_len):
        """Output equals the verbatim in-tree reference for the same nonce."""
        expected = _ref_get_new_client_order_id(nonce, is_buy, trading_pair, prefix, max_id_len)
        actual = get_new_client_order_id(is_buy, trading_pair, prefix, max_id_len, nonce=nonce)
        assert actual == expected


class TestNumericClientOrderIdParity:
    """get_new_numeric_client_order_id must be identical to the in-tree version."""

    @pytest.mark.parametrize("nonce", _NONCES)
    @pytest.mark.parametrize("max_id_bit_count", [None, 0, 8, 32, 64, 128])
    def test_matches_in_tree(self, nonce, max_id_bit_count):
        """Output equals the verbatim in-tree reference for the same nonce."""
        expected = _ref_get_new_numeric_client_order_id(nonce, max_id_bit_count)
        actual = get_new_numeric_client_order_id(max_id_bit_count, nonce=nonce)
        assert actual == expected


class TestGoldenValues:
    """Literal pinned outputs, independent of the reference copy above."""

    @pytest.fixture(autouse=True)
    def fixed_host(self, monkeypatch):
        """Pin the host fingerprint."""
        monkeypatch.setattr(coid, "_bot_instance_id", lambda: _FIXED_HOST)

    def test_full_string_id(self):
        """Untruncated string id."""
        assert (
            get_new_client_order_id(True, "HBOT-COINALPHA", "hbot", nonce=1640001112223334)
            == "hbotBHTCA5d39283b9ae660123456789abcdef0123456789abcdef"
        )

    def test_plain_truncated_id(self):
        """Truncation path where the nonce hex still fits."""
        assert (
            get_new_client_order_id(True, "HBOT-COINALPHA", "hbot", 30, nonce=1640001112223334)
            == "hbotBHTCA5d39283b9ae6601234567"
        )

    def test_md5_suffix_id(self):
        """Hashed-suffix path where the nonce hex does not fit."""
        assert (
            get_new_client_order_id(False, "BTC-USDT", "hbot", 14, nonce=1640001112223334)
            == "hbotSBCUTa4375"
        )

    def test_numeric_unmasked(self):
        """Unmasked numeric id."""
        assert (
            get_new_numeric_client_order_id(nonce=1640001112223334)
            == 15123660752041709290495823544065592151640001112223334
        )

    def test_numeric_masked_64(self):
        """Numeric id masked to 64 bits."""
        assert get_new_numeric_client_order_id(64, nonce=1640001112223334) == 8189481811649801830


class TestMonotonicity:
    """Monotonicity is a property of the injected nonce, not of the package."""

    _CALLS = 10_000

    # Note: strict monotonicity of the numeric id holds only without masking and
    # while nonce lengths are equal (decimal concatenation); it is a property of
    # the injected nonce, not of the id functions.

    def test_injected_nonce_sequence_strictly_increasing(self):
        """Duplicate time_ns()//1000 readings are collapsed by the helper."""
        source = _MonotonicMicroNonce()
        nonces = [source.get_tracking_nonce() for _ in range(self._CALLS)]
        assert all(b > a for a, b in zip(nonces, nonces[1:], strict=False))

    def test_numeric_ids_strictly_increasing(self):
        """Without masking (and with equal digit counts) numeric ids increase."""
        source = _MonotonicMicroNonce()
        ids = [
            get_new_numeric_client_order_id(nonce=source.get_tracking_nonce())
            for _ in range(self._CALLS)
        ]
        assert all(b > a for a, b in zip(ids, ids[1:], strict=False))

    def test_string_ids_unique(self):
        """String ids are all unique with a monotonic nonce."""
        source = _MonotonicMicroNonce()
        ids = [
            get_new_client_order_id(True, "BTC-USDT", nonce=source.get_tracking_nonce())
            for _ in range(self._CALLS)
        ]
        assert len(set(ids)) == self._CALLS


class TestSignatures:
    """Pin the keyword-only nonce injection contract (issue #20)."""

    def test_client_order_id_signature(self):
        """nonce is keyword-only and defaults to None."""
        params = inspect.signature(get_new_client_order_id).parameters
        assert list(params) == [
            "is_buy",
            "trading_pair",
            "hbot_order_id_prefix",
            "max_id_len",
            "nonce",
        ]
        assert params["hbot_order_id_prefix"].default == ""
        assert params["max_id_len"].default is None
        assert params["nonce"].kind is inspect.Parameter.KEYWORD_ONLY
        assert params["nonce"].default is None

    def test_numeric_client_order_id_signature(self):
        """nonce is keyword-only and defaults to None."""
        params = inspect.signature(get_new_numeric_client_order_id).parameters
        assert list(params) == ["max_id_bit_count", "nonce"]
        assert params["max_id_bit_count"].default is None
        assert params["nonce"].kind is inspect.Parameter.KEYWORD_ONLY
        assert params["nonce"].default is None
