# Contaxy

## Start the Contaxy backend locally

In the `backend` directory, run `uvicorn --app-dir=src contaxy.main:app --reload`.

## Testing

The project contains unit tests, integration tests, and stress tests. For the unit and integration tests `pytest` is used, for the stress tests `locust`.

To run the unit/integration tests, you have the following options:

1. in the root folder, execute `act -j build -s BUILD_ARGS="--test"`
2. in the root folder, execute `python build.py --test`
3. `cd` into the `backend/` folder and run `PYTHONPATH=$(pwd) pytest`

By default, unit tests are executed (marked via `pytest.mark.unit`). If you want to execute the integration tests, pass `--test-marker integration` to *options 1* or *2* or `-m "integration"` to *option 3*. This can be a valid pytest markexpression, hence it would also be possible to execute unit *and* integration tests by passing `"unit and integration"` to one of the flags. If neither unit nor integration tests should be executed, pass an unknown marker such as `notests`.
Option 1 will create an internal, local Kubernetes cluster and will also execute the unit tests requiring the `KubeSpawner`. If you want to execute the unit tests for KubeSpawner manually, set `KUBE_AVAILABLE=true` and make sure that a Kubernetes cluster is accessible.

> ❗ To point to a running instance for Contaxy, set the `CONTAXY_ENDPOINT` variable. If this variable is not set, FastAPI's TestClient is used and so the app is manuall invoked. Please make sure that the invoked app can access the required databases or mock them accordingly (see `backend/tests/endpoint_tests/conftest.py::client`). Set the `CONTAXY_ROOT_PATH` according to the running instance (likely set to `/api`).

To run the stress tests, you have the following options:

1. in the root folder, execute `act -j build -s BUILD_ARGS="--test --test-marker stress"`
2. in the root folder, execute `python build.py --test --test-marker stress`
3. `cd` into the `backend/` folder and execute, for example, `locust -f tests/endpoint_tests/locustfile.py --host=http://localhost:8000 --headless -t1m --csv=./tests/results/locust`

For *options 1* and *2*, `locust` runs in headless mode and saves the csv result-files in the `backend/tests` directory. In *option 3* just change the args as wished.

> ❗ For the stress tests, the `CONTAXY_ENDPOINT` variable **must** be set and pointing to a running Contaxy instance. Set the `CONTAXY_ROOT_PATH` according to the running instance (likely set to `/api`). When using the `act` option, nothing has to be done as it will start it's own local instance.
