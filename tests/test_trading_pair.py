"""Tests for trading pair utilities."""

import pytest

from connector_utils.trading_pair import (
    combine_to_hb_trading_pair,
    split_hb_trading_pair,
    validate_trading_pair,
)


class TestSplitHbTradingPair:
    """Tests for split_hb_trading_pair function."""

    def test_split_basic_trading_pair(self):
        """Test splitting a basic trading pair."""
        base, quote = split_hb_trading_pair("BTC-USDT")
        assert base == "BTC"
        assert quote == "USDT"

    def test_split_single_letter_base(self):
        """Test splitting with single letter base."""
        base, quote = split_hb_trading_pair("X-USD")
        assert base == "X"
        assert quote == "USD"

    def test_split_single_letter_quote(self):
        """Test splitting with single letter quote."""
        base, quote = split_hb_trading_pair("BTC-Y")
        assert base == "BTC"
        assert quote == "Y"

    def test_split_lowercase_pair(self):
        """Test splitting lowercase trading pair."""
        base, quote = split_hb_trading_pair("eth-usdc")
        assert base == "eth"
        assert quote == "usdc"

    @pytest.mark.parametrize(
        "trading_pair,expected_base,expected_quote",
        [
            ("BTC-USD", "BTC", "USD"),
            ("ETH-USDT", "ETH", "USDT"),
            ("HBOT-COINALPHA", "HBOT", "COINALPHA"),
            ("XRP-EUR", "XRP", "EUR"),
        ],
    )
    def test_split_various_pairs(self, trading_pair, expected_base, expected_quote):
        """Test splitting various trading pairs."""
        base, quote = split_hb_trading_pair(trading_pair)
        assert base == expected_base
        assert quote == expected_quote

    def test_split_with_multiple_dashes_raises_error(self):
        """Test that splitting pair with multiple dashes raises ValueError."""
        with pytest.raises(ValueError):
            split_hb_trading_pair("BTC-USD-EUR")

    def test_split_without_dash_raises_error(self):
        """Test that splitting pair without dash raises ValueError."""
        with pytest.raises(ValueError):
            split_hb_trading_pair("BTCUSDT")

    def test_split_empty_base_from_leading_dash(self):
        """Test splitting pair starting with dash."""
        base, quote = split_hb_trading_pair("-USDT")
        assert base == ""
        assert quote == "USDT"

    def test_split_empty_quote_from_trailing_dash(self):
        """Test splitting pair ending with dash."""
        base, quote = split_hb_trading_pair("BTC-")
        assert base == "BTC"
        assert quote == ""


class TestCombineToHbTradingPair:
    """Tests for combine_to_hb_trading_pair function."""

    def test_combine_basic_pair(self):
        """Test combining basic base and quote."""
        result = combine_to_hb_trading_pair("BTC", "USDT")
        assert result == "BTC-USDT"

    def test_combine_single_letter_base(self):
        """Test combining single letter base."""
        result = combine_to_hb_trading_pair("X", "USD")
        assert result == "X-USD"

    def test_combine_single_letter_quote(self):
        """Test combining single letter quote."""
        result = combine_to_hb_trading_pair("BTC", "Y")
        assert result == "BTC-Y"

    def test_combine_lowercase(self):
        """Test combining lowercase base and quote."""
        result = combine_to_hb_trading_pair("eth", "usdc")
        assert result == "eth-usdc"

    def test_combine_mixed_case(self):
        """Test combining mixed case base and quote."""
        result = combine_to_hb_trading_pair("HbOt", "CoInAlPhA")
        assert result == "HbOt-CoInAlPhA"

    @pytest.mark.parametrize(
        "base,quote,expected",
        [
            ("BTC", "USD", "BTC-USD"),
            ("ETH", "USDT", "ETH-USDT"),
            ("HBOT", "COINALPHA", "HBOT-COINALPHA"),
            ("XRP", "EUR", "XRP-EUR"),
        ],
    )
    def test_combine_various_pairs(self, base, quote, expected):
        """Test combining various base and quote combinations."""
        result = combine_to_hb_trading_pair(base, quote)
        assert result == expected

    def test_combine_empty_base(self):
        """Test combining with empty base."""
        result = combine_to_hb_trading_pair("", "USD")
        assert result == "-USD"

    def test_combine_empty_quote(self):
        """Test combining with empty quote."""
        result = combine_to_hb_trading_pair("BTC", "")
        assert result == "BTC-"

    def test_combine_both_empty(self):
        """Test combining with both empty."""
        result = combine_to_hb_trading_pair("", "")
        assert result == "-"

    def test_combine_with_spaces(self):
        """Test combining base and quote containing spaces."""
        result = combine_to_hb_trading_pair("B T C", "U S D")
        assert result == "B T C-U S D"


class TestValidateTradingPair:
    """Tests for validate_trading_pair function."""

    def test_validate_valid_pair(self):
        """Test validation of valid trading pair."""
        assert validate_trading_pair("BTC-USDT") is True

    def test_validate_valid_pair_single_letters(self):
        """Test validation with single letter base and quote."""
        assert validate_trading_pair("X-Y") is True

    def test_validate_valid_pair_hbot_coinalpha(self):
        """Test validation of HBOT-COINALPHA pair."""
        assert validate_trading_pair("HBOT-COINALPHA") is True

    def test_validate_valid_pair_lowercase(self):
        """Test validation of lowercase pair."""
        assert validate_trading_pair("btc-usdt") is True

    @pytest.mark.parametrize(
        "trading_pair",
        [
            "BTC-USD",
            "ETH-USDT",
            "HBOT-COINALPHA",
            "XRP-EUR",
            "A-B",
        ],
    )
    def test_validate_various_valid_pairs(self, trading_pair):
        """Test validation of various valid trading pairs."""
        assert validate_trading_pair(trading_pair) is True

    def test_validate_no_dash(self):
        """Test validation fails without dash."""
        assert validate_trading_pair("BTCUSDT") is False

    def test_validate_multiple_dashes(self):
        """Test validation fails with multiple dashes."""
        assert validate_trading_pair("BTC-USD-EUR") is False

    def test_validate_empty_string(self):
        """Test validation fails on empty string."""
        assert validate_trading_pair("") is False

    def test_validate_only_dash(self):
        """Test validation succeeds with only dash."""
        assert validate_trading_pair("-") is True

    def test_validate_leading_dash(self):
        """Test validation succeeds with leading dash."""
        assert validate_trading_pair("-USDT") is True

    def test_validate_trailing_dash(self):
        """Test validation succeeds with trailing dash."""
        assert validate_trading_pair("BTC-") is True

    def test_validate_no_split_result(self):
        """Test validation on string with no hyphen parts."""
        assert validate_trading_pair("BTCUSDTEUR") is False
