"""Trading pair utilities for Hummingbot connectors.

Functions for splitting, combining, and validating trading pair strings
in the canonical HB ``BASE-QUOTE`` format.
"""


def split_hb_trading_pair(trading_pair: str) -> tuple[str, str]:
    base, quote = trading_pair.split("-")
    return base, quote


def combine_to_hb_trading_pair(base: str, quote: str) -> str:
    trading_pair = f"{base}-{quote}"
    return trading_pair


def validate_trading_pair(trading_pair: str) -> bool:
    valid = False
    if "-" in trading_pair and len(trading_pair.split("-")) == 2:
        valid = True
    return valid
