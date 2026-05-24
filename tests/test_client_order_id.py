"""Tests for client order ID generation utilities."""

import os
import platform
from hashlib import md5

import pytest

from connector_utils.client_order_id import (
    get_new_client_order_id,
    get_new_numeric_client_order_id,
)

_FIXED_NONCE = 1640001112223334


class TestGetNewClientOrderId:
    """Test suite for get_new_client_order_id function."""

    @pytest.fixture
    def trading_pair(self):
        """Standard trading pair for tests."""
        return "HBOT-COINALPHA"

    def test_client_order_id_without_prefix(self, trading_pair):
        """Test that client order ID is generated without prefix when not provided."""
        order_id = get_new_client_order_id(
            is_buy=True, trading_pair=trading_pair, nonce=_FIXED_NONCE
        )

        assert not order_id.startswith("hbot")
        assert "BHT" in order_id  # Side + base symbols

    def test_client_order_id_with_prefix(self, trading_pair):
        """Test that client order ID includes the provided prefix."""
        prefix = "hbot"

        order_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            hbot_order_id_prefix=prefix,
            nonce=_FIXED_NONCE,
        )

        assert order_id.startswith(prefix)

    def test_client_order_id_respects_max_length(self, trading_pair):
        """Test that client order ID respects max_id_len parameter."""
        full_id = get_new_client_order_id(
            is_buy=True, trading_pair=trading_pair, nonce=_FIXED_NONCE
        )
        reduced_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            max_id_len=len(full_id) - 2,
            nonce=_FIXED_NONCE,
        )

        assert len(reduced_id) == len(full_id) - 2

    def test_client_order_id_with_buy_side(self, trading_pair):
        """Test that buy orders have 'B' side indicator."""
        order_id = get_new_client_order_id(
            is_buy=True, trading_pair=trading_pair, nonce=_FIXED_NONCE
        )

        assert "B" in order_id
        # Should have format: side (B) + base symbols (HT) + quote symbols (CA)
        assert "BHT" in order_id

    def test_client_order_id_with_sell_side(self, trading_pair):
        """Test that sell orders have 'S' side indicator."""
        order_id = get_new_client_order_id(
            is_buy=False, trading_pair=trading_pair, nonce=_FIXED_NONCE
        )

        assert "S" in order_id
        # Should have format: side (S) + base symbols (HT) + quote symbols (CA)
        assert "SHT" in order_id

    def test_client_order_id_with_long_prefix_and_max_len_uses_full_suffix(self, trading_pair):
        """Test that when max_id_len is large enough, full suffix is included."""
        nonce_value = _FIXED_NONCE
        prefix = "long-hbot-prefix"
        full_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            hbot_order_id_prefix=prefix,
            nonce=nonce_value,
        )
        shortened_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            hbot_order_id_prefix=prefix,
            # prefix + side + symbols + time hex + instance id start
            max_id_len=len(prefix) + 5 + 13 + 5,
            nonce=nonce_value,
        )

        # Shortened ID should still have the time hex component
        expected_time_text = hex(nonce_value)[2:]
        assert expected_time_text in shortened_id
        assert len(shortened_id) <= len(full_id)

    def test_client_order_id_with_max_len_less_than_required_hashes_suffix(self, trading_pair):
        """Test that when max_id_len is very small, suffix is hashed."""
        nonce_value = _FIXED_NONCE
        prefix = "long-hbot-prefix"
        extra_reduced_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            hbot_order_id_prefix=prefix,
            max_id_len=len(prefix) + 5 + 12,
            nonce=nonce_value,
        )

        # When max_id_len is very small, the suffix should be hashed
        expected_id_prefix = f"{prefix}BHTCA"
        assert extra_reduced_id.startswith(expected_id_prefix)
        assert len(extra_reduced_id) == len(prefix) + 5 + 12

    def test_client_order_id_format_matches_expected(self, trading_pair):
        """Test that client order ID has expected format."""
        nonce_value = _FIXED_NONCE
        prefix = "long-hbot-prefix"
        order_id = get_new_client_order_id(
            is_buy=True,
            trading_pair=trading_pair,
            hbot_order_id_prefix=prefix,
            nonce=nonce_value,
        )

        # Calculate expected components
        expected_id_prefix = f"{prefix}BHTCA"
        expected_time_text = hex(nonce_value)[2:]
        expected_client_instance_id = md5(
            f"{platform.uname()}_pid:{os.getpid()}_ppid:{os.getppid()}".encode()
        ).hexdigest()
        expected_full_id = f"{expected_id_prefix}{expected_time_text}{expected_client_instance_id}"

        assert order_id == expected_full_id


class TestGetNewNumericClientOrderId:
    """Test suite for get_new_numeric_client_order_id function."""

    def test_numeric_client_order_id_is_integer(self):
        """Test that numeric client order ID returns an integer."""
        order_id = get_new_numeric_client_order_id(nonce=123456789)

        assert isinstance(order_id, int)

    def test_numeric_client_order_id_combines_host_and_nonce(self):
        """Test that numeric order ID combines host part and nonce via decimal string concat."""
        nonce_value = 123456789

        order_id = get_new_numeric_client_order_id(nonce=nonce_value)

        # Verify that the nonce is part of the order ID (decimal string concatenation)
        assert str(nonce_value) in str(order_id)

    def test_numeric_client_order_id_without_max_bit_count(self):
        """Test numeric order ID generation without bit count limitation."""
        order_id = get_new_numeric_client_order_id(max_id_bit_count=None, nonce=123456789)

        assert isinstance(order_id, int)
        assert order_id > 0

    def test_numeric_client_order_id_with_max_bit_count(self):
        """Test numeric order ID respects max_id_bit_count constraint."""
        max_bits = 32

        order_id = get_new_numeric_client_order_id(
            max_id_bit_count=max_bits,
            nonce=123456789,
        )

        # Verify order ID fits within the specified bit count
        max_allowed = 2**max_bits - 1
        assert order_id <= max_allowed

    def test_numeric_client_order_id_with_small_bit_count(self):
        """Test numeric order ID with very small bit count."""
        max_bits = 16

        order_id = get_new_numeric_client_order_id(
            max_id_bit_count=max_bits,
            nonce=999999999,
        )

        # Verify order ID fits within the specified bit count
        max_allowed = 2**max_bits - 1
        assert order_id <= max_allowed
        assert order_id >= 0

    def test_numeric_client_order_id_different_nonces_produce_different_ids(self):
        """Test that different nonces produce different order IDs."""
        order_id1 = get_new_numeric_client_order_id(nonce=111111111)
        order_id2 = get_new_numeric_client_order_id(nonce=222222222)

        # Different nonces should produce different IDs
        assert order_id1 != order_id2

    def test_numeric_client_order_id_host_part_included(self):
        """Test that the host part (MD5 fingerprint as int) is included in decimal concat."""
        nonce_value = 123456789
        expected_host_part = int(
            md5(
                f"{platform.uname()}_pid:{os.getpid()}_ppid:{os.getppid()}".encode(),
                usedforsecurity=False,
            ).hexdigest(),
            16,
        )
        expected_order_id = int(f"{expected_host_part}{nonce_value}")

        order_id = get_new_numeric_client_order_id(nonce=nonce_value)

        assert order_id == expected_order_id
