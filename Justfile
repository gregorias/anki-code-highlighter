test: mypy unittest

# Bumps version numbers, commits, tags, and pushes.
bump:
  ./dev/bin/bump

# Builds .ankiaddon package.
package:
  ./dev/bin/package

# Creates a package and releases to GitHub.
release: package
  ./dev/bin/release

mypy:
  mypy --config-file=mypy.ini codehighlighter/ test

ruff:
  ruff check codehighlighter test

ruff-fix:
  ruff check --fix codehighlighter test

unittest:
  python -m unittest discover -s test/ -t .

coverage:
  coverage run --source='codehighlighter/' --branch -m unittest discover -s test/ -t . && \
  coverage html

vulture:
  vulture codehighlighter/ vulture_whitelist.py
