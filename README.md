# bubblewrap 

a wrapper around pytest for assessing flakiness and runtime regressions

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

### Code Formatting
This project uses Black for code formatting:
```bash
$ python3 -m black .

```
The `pyproject.toml` file includes configuration.


### Tests

Actual unit tests for this project are also run with with [pytest](https://docs.pytest.org/en/stable/). Having installed the `pip` dependencies (see prior section), run with the following:

```bash
# unit tests
$ python3 -m pytest
```

```bash
# test coverage report
$ python3 -m coverage run -m pytest
```
