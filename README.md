# bubblewrap 

a wrapper around pytest for assessing flakiness and runtime regressions

_a cs implementations practice project_

## How to Run: 

First, install depedencies
```bash
# from the bubblewrap root
# first, install depdencies:
$ pip3 install -r requirements.txt`
```
```bash
# then, invoke with:
$ ./bubblewrap path/to/code

```

e.g.

```bash

$ ./bubblewrap .

```

or, if you're using add `bubblewrap` to your `$PATH` and call with just `bubblewrap path/to/code`, e.g.:

```bash
$ PATH="$HOME/path/to/bubblewrap:$PATH"

```

### Demos

This package also has a couple quick demos for testing against: 

```bash
# from the bubblewrap root
$ ./bubblewrap examples/stable

```

```bash
# from the bubblewrap root
$ ./bubblewrap examples/flake

```

### Usage Notes

As of right now, imports in test modules need to import the _full_ path of the module, e.g.:

```python
# this is alright: 
from example.one.A import apple
# but this is currently supported:
from A import apple
```

This'll be changed in the future. 

Also, `bubblewrap` doesn't yet support regression analysis


## Local Setup

This project uses Python3.9, `pip` to manage dependencies, and runs in a virtual environment. Install with the following:

```bash
# create + activate venv + install dependencies
# see docs:  https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
$ python3 -m pip install --user virtualenv
$ python3 -m venv env
$ source env/bin/activate
$ pip install -r requirements.txt
```

```bash
# note: to deactivate venv, use
$ deactivate
```

## Code Formatting

This project uses Black for code formatting:
```bash
$ python3 -m black .

```
The `pyproject.toml` file includes configuration for Black.


And, the project is linted with flake8

```bash 
$ python3 -m flake8 path/to/code

```


### Tests

Actual unit tests for this project are also run with with [pytest](https://docs.pytest.org/en/stable/). Having installed the `pip` dependencies (see prior section), run with the following:

```bash
# unit tests, ignoring ones in the demo dirs that are designed to flake
$ python3 -m pytest -vv -k 'not flake' .
```

```bash
# test coverage report
$ python3 -m coverage run -m pytest -k 'not flake' .
$ coverage report -m
```
