test: mypy unittest

mypy:
  mypy --config-file=mypy.ini codehighlighter/ test

unittest:
  python -m unittest discover -s test/ -t .
