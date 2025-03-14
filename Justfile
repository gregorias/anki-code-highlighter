test: mypy unittest

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
  vulture codehighlighter/
