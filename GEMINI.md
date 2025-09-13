# Gemini Project Guide: anki-code-highlighter

This document provides instructions for the Gemini AI agent to interact with the
`anki-code-highlighter` repository.

## Project Overview

This repository contains an Anki add-on that provides syntax highlighting for
code snippets embedded in cards. It uses Pygments for highlighting and is
designed to work with Anki's day and night modes.

## Tech Stack

- **Language:** Python 3.13
- **Dependency Management:** `uv`
- **Task Runner:** `just`
- **Linting:** `ruff`
- **Type Checking:** `mypy`
- **Testing:** `unittest`

## Project Structure

- **`codehighlighter/`**: Main source code for the Anki add-on.
- **`test/`**: Unit tests.
- **`pydeps/`**: Vendored dependencies (contains Pygments).
- **`assets/`**: Static assets like CSS and JavaScript.
- **`tools/`**: Development scripts, e.g., for generating Pygments CSS.
- **`Justfile`**: Defines project tasks and commands.
- **`pyproject.toml`**: Python project metadata and dependencies.
- **`README.md`**: Project README.
- **`GEMINI.md`**: Instructions for the Gemini AI agent.

## Development Commands

The project uses a `Justfile` to define common development tasks.

| Command         | Description                                                                                             |
| :-------------- | :------------------------------------------------------------------------------------------------------ |
| `just ruff`     | Run the `ruff` linter to check for style issues.                                                        |
| `just ruff-fix` | Run `ruff` and automatically fix any detected issues.                                                   |
| `just mypy`     | Run `mypy` to perform static type checking.                                                             |
| `just unittest` | Execute the unit test suite.                                                                            |
| `just test`     | A convenience command that runs both `mypy` and `unittest`. This is the primary command for validation. |
| `just coverage` | Run tests and generate an HTML coverage report.                                                         |
| `just vulture`  | Scan for and report dead code.                                                                          |
| `just package`  | Build the distributable `.ankiaddon` package.                                                           |
| `just release`  | Create a package and release it to GitHub.                                                              |

### Workflow

- Before committing, always run `just test` to ensure that type checks and unit
  tests pass.
- To automatically fix linting issues, run `just ruff-fix`.
