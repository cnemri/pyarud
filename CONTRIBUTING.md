# Contributing to Pyarud

Thank you for your interest in contributing to Pyarud! We welcome contributions from the community to help improve this library for Arabic prosody (Arud) analysis.

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally:
    ```bash
    git clone https://github.com/cnemri/pyarud.git
    cd pyarud
    ```
3.  **Set up a development environment**:
    We recommend using `uv` or `venv`:
    ```bash
    # Using uv
    uv sync
    
    # Or using standard venv
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -e .[dev]
    ```

## Development Workflow

1.  **Create a branch** for your feature or bugfix:
    ```bash
    git checkout -b feature/my-new-feature
    ```
2.  **Make your changes**. Ensure your code follows the project's style.
3.  **Run tests** to ensure you haven't broken anything:
    ```bash
    pytest
    ```
4.  **Run linting and type checking**:
    ```bash
    ruff check .
    mypy .
    ```

## Code Style

- We use **Ruff** for linting and formatting.
- We use **Mypy** for static type checking.
- Please add type hints to new functions and classes.
- Follow PEP 8 guidelines (Ruff will help you with this).

## Pull Requests

1.  Push your branch to your fork.
2.  Open a Pull Request (PR) against the `main` branch.
3.  Describe your changes clearly in the PR description.
4.  Ensure all tests and checks pass.

## Reporting Issues

If you find a bug or have a feature request, please open an issue on the GitHub repository with details about the problem or suggestion.

Thank you for contributing!
