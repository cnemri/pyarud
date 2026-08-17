# Installation Guide

## Prerequisites

PyArud requires **Python 3.12** or newer and has **zero external runtime dependencies**.

## Standard Installation

You can install PyArud directly from PyPI using pip:

```bash
pip install pyarud
```

Or using `uv`:

```bash
uv add pyarud
```

## Development Setup

If you want to contribute to PyArud, run benchmarks, or build documentation locally:

### Using uv (Recommended)

```bash
git clone https://github.com/cnemri/pyarud.git
cd pyarud

# Install with development & documentation tools
uv sync --extra dev --extra docs
```

### Using standard venv

```bash
git clone https://github.com/cnemri/pyarud.git
cd pyarud

python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install -e ".[dev,docs]"
```

## Running Tests & Benchmarks

To execute the test suite (including the 80-poem unseen benchmark):

```bash
pytest -v
```

## Verifying Installation

To verify that PyArud is working correctly:

```bash
python -c "import pyarud; print(f'PyArud v{pyarud.__version__} installed successfully!')"
```
