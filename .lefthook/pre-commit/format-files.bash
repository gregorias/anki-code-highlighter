#!/usr/bin/env bash

function format-files {
  # Git pre-commit hook to check staged Python files for formatting issues with
  # yapf.

  # Find all staged Python files, and exit early if there aren't any.
  PYTHON_FILES=()
  while IFS=$'\n' read -r line; do PYTHON_FILES+=("$line"); done \
    < <(git diff --name-only --cached --diff-filter=AM | grep --color=never '.py$')
  if [ ${#PYTHON_FILES[@]} -eq 0 ]; then
    return 0
  fi

  if ! pipenv run yapf --version 2>/dev/null 2>&1; then
    echo 'yapf not on path; can not format. Please install yapf:'
    echo '    pipenv install yapf'
    exit 2
  fi

  # Check for unstaged changes to files in the index.
  CHANGED_FILES=()
  while IFS=$'\n' read -r line; do CHANGED_FILES+=("$line"); done \
    < <(git diff --name-only "${PYTHON_FILES[@]}")
  if [ ${#CHANGED_FILES[@]} -gt 0 ]; then
    echo 'You have unstaged changes to some files in your commit; skipping '
    echo 'auto-format. Please stage, stash, or revert these changes. You may '
    echo 'find `git stash -k` helpful here.'
    echo 'Files with unstaged changes:' "${CHANGED_FILES[@]}"
    exit 1
  fi

  # Format all staged files, then exit with an error code if any have uncommitted
  # changes.
  echo 'Formatting staged Python files . . .'

  pipenv run yapf -i -r "${PYTHON_FILES[@]}"

  CHANGED_FILES=()
  while IFS=$'\n' read -r line; do CHANGED_FILES+=("$line"); done \
    < <(git diff --name-only "${PYTHON_FILES[@]}")
  if [ ${#CHANGED_FILES[@]} -gt 0 ]; then
    echo 'Reformatted staged files. Please review and stage the changes.'
    echo 'Files updated: ' "${CHANGED_FILES[@]}"
    exit 1
  fi
}

format-files
