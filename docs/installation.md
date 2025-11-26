# Installation Guide

## Prerequisites

PyArud requires **Python 3.12** or newer.

## Standard Installation

You can install PyArud directly from PyPI using pip:

```bash
pip install pyarud
```

## Development Setup

If you want to contribute to PyArud or run the tests locally, follow these steps.

### Using standard venv

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/pyarud.git
    cd pyarud
    ```

2.  **Create a virtual environment:**
    ```bash
    python3.12 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install in editable mode with dev dependencies:**
    ```bash
    pip install -e ".[dev,docs]"
    ```

### Using uv (Recommended)

If you use [uv](https://github.com/astral-sh/uv), it handles Python versions and virtual environments automatically.

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev,docs]"
```

## Verifying Installation

To verify that PyArud is installed correctly, run this simple one-liner in your terminal:

```bash
python -c "from pyarud.processor import ArudhProcessor; print(ArudhProcessor().process_poem([('أَخِي جَاوَزَ الظَّالِمُونَ الْمَدَى', '')])['meter'])"
```

It should output:
```text
mutakareb
```
