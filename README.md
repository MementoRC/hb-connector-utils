# hb-connector-utils

[![CI](https://github.com/MementoRC/hb-connector-utils/actions/workflows/ci.yml/badge.svg)](https://github.com/MementoRC/hb-connector-utils/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/MementoRC/hb-connector-utils)](https://codecov.io/gh/MementoRC/hb-connector-utils)
[![PyPI version](https://badge.fury.io/py/hb-connector-utils.svg)](https://badge.fury.io/py/hb-connector-utils)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Shared utilities for connector implementations across Hummingbot sub-packages.

## Overview

This package provides shared helper utilities used by Hummingbot exchange connector
implementations. It operates as a standalone library that can be consumed independently
of the main Hummingbot application.

> **Scaffold notice**: This package is in initial scaffold state. The `connector_utils`
> module currently contains only the version stub. Connector utility implementations
> will be added in follow-up feature PRs.

> **Deferred sibling dependency**: A runtime dependency on `hb-data-type-primitives`
> (shared enums and data types for connectors) is planned but deferred to a follow-up
> feature PR. It is omitted here because `hb-data-type-primitives` is itself in
> scaffold-only state with no buildable package yet, which would block CI installation.

## Installation

```bash
pip install hb-connector-utils
```

Or with pixi:

```bash
pixi add hb-connector-utils
```

## Development

```bash
# Clone and install dev environment
git clone https://github.com/MementoRC/hb-connector-utils.git
cd hb-connector-utils
pixi install

# Run tests
pixi run test

# Run quality checks
pixi run quality

# Run full check suite
pixi run check
```

## Branch Strategy

- `development`: active development branch (default for PRs)
- `main`: release tagging only; PRs to `main` must come from `development`
