# Python Library Template

_WIP: Document python library._

## Requirements

* Python 3.6+

## Installation

Install via pip:

```bash
pip install --upgrade -e path/to/lib
```

## Usage

After installation, the package can be imported:

```python
import template_package
```

## Development

This library uses [black](https://github.com/psf/black) for auto-formatting, [isort](https://github.com/PyCQA/isort) for import sorting, [flake8](https://github.com/PyCQA/flake8) for linting, [mypy](https://github.com/python/mypy) for type checking, and [pydocstyle](https://github.com/PyCQA/pydocstyle) for docstring style checks. All code is written compatible with Python 3.6+, with type hints wherever possible.

## Testing

* DeploymentManager:
  * By default, just the DockerDeploymentManager is executed. To execute also the Kubernetes-related tests, a Kubernetes cluster has to be available from where the code is executed. On your local Mac, you can simply start one by executing `kind create cluster`. Then execute the tests by setting the environment variable `KUBE_AVAILABLE=true` (in VS Code, you can for example set the env variable in the `launch.json` or append it in front of the pytest command, e.g. `KUBE_AVAILABLE=true pytest...`)
