<!-- markdownlint-disable MD033 MD041 -->
<h1 align="center">
    Contaxy
</h1>

<p align="center">
    <strong>Collaborative, extensible platform to create projects, share files, and deploy services & jobs.</strong>
</p>

<p>
    <a href="https://pypi.org/project/contaxy/" title="PyPi Version"><img src="https://img.shields.io/pypi/v/contaxy?color=green&style=flat"></a>
    <a href="https://pypi.org/project/contaxy/" title="Python Version"><img src="https://img.shields.io/badge/Python-3.6%2B-blue&style=flat"></a>
    <a href="https://github.com/ml-tooling/opyrator/blob/main/LICENSE" title="Project License"><img src="https://img.shields.io/badge/License-MIT-green.svg"></a>
    <a href="https://github.com/ml-tooling/contaxy/actions?query=workflow%3Abuild-pipeline" title="Build status"><img src="https://img.shields.io/github/workflow/status/ml-tooling/contaxy/build-pipeline?style=flat"></a>
    <a href="ttps://mltooling.substack.com/subscribe" title="Subscribe to newsletter"><img src="http://bit.ly/2Md9rxM"></a>
    <a href="https://twitter.com/mltooling" title="Follow on Twitter"><img src="https://img.shields.io/twitter/follow/mltooling.svg?style=social&label=Follow"></a>
</p>

<p align="center">
  <a href="#getting-started">Getting Started</a> •
  <a href="#features">Features</a> •
  <a href="#examples">Examples</a> •
  <a href="#support--feedback">Support</a> •
  <a href="https://github.com/ml-tooling/opyrator/issues/new?labels=bug&template=01_bug-report.md">Report a Bug</a> •
  <a href="#contribution">Contribution</a> •
  <a href="https://github.com/ml-tooling/opyrator/releases">Changelog</a>
</p>

Contaxy is an extensible collaborative platform for teams to share files and deploy services and jobs easily using Docker or Kubernetes.The platform is secured so only members of a project can access its resources (files, services, jobs). Its strong extension system allows to add further functionality to the backend and web app and also to override the behavior of Contaxy's core endpoints. By adding project members or generating fine-granular access tokens, resources can easily be shared with others. Deploying a service and securely sharing it with a stakeholder? No problem. It is based on the [Machine Learning Lab project](https://github.com/SAP/machine-learning-lab) with a completely rewritten backend and web app using the newer React functions.

## Highlights

- 🔐 Secure multi-user development plaform for collaboration.
- 🗃️ Upload, manage, version, and share files.
- 🎛 Deploy and share services.
- 🐳 Deployable on a single-server via Docker or a server-cluster via Kubernetes.

## Getting Started

### Installation

> _**Note**: Currently, not all Docker images are pushed to DockerHub. So, the project has to be built locally, see the [build section](#build)_.

For the Docker deployment, have a look at the [docker-compose.yaml file](./test_deployment/docker-compose.yml); you can start it via `docker compose up`. For Kubernetes, have a look at the [deploy script](./test_deployment/kubernetes/deploy.sh).
> _**Important**: The configurations are not meant to be used for production as the JWT secret is the default one and the ports of all services instead of only the core service are published; change the configuration accordingly._

For a list of all configurable environment variables, have a look at [the config file](./backend/src/contaxy/config.py#L31). All fields of the `Settings` class represent an environment variable that can be set.

### Usage

After deploying, visit `http://localhost:30010/app/`. If you deployed it via the `docker-compose.yaml` file, you can login with the credentials `Foo:Foobar`. If you deployed the Kubernetes version, you have to call the endpoint `/api/seed/default` in the browser once first.

## Development

### Start the backend locally

In the `backend` directory, run `uvicorn --app-dir=src contaxy.main:app --reload`. Set the environment variables `POSTGRES_CONNECTION_URI`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY` so that the locally-started Python instance can access them.

### Build

#### Using Act

> _**Note**: We recommend to use [Docker](https://docs.docker.com/get-docker/) and [Act](https://github.com/nektos/act#installation) to execute the containerized build process. If this is not an option, run `python build.py --make` and install the dependencies based on probable errors._

To simplify the process of building this project from scratch, we provide build-scripts - based on [universal-build](https://github.com/ml-tooling/universal-build) - that run all necessary steps (build, check, test, and release) within a containerized environment. To build and test your changes, execute the following command in the project root folder:

```bash
act -b -j build
```

Refer to our [contribution guides](https://github.com/ml-tooling/contaxy/blob/main/CONTRIBUTING.md#development-instructions) for more detailed information on our build scripts and development process.

### Testing

The project contains unit tests, integration tests, and stress tests. For the unit and integration tests `pytest` is used, for the stress tests `locust`.

To run the unit/integration tests, you have the following options:

1. in the root folder, execute `act -j build -s BUILD_ARGS="--test"`
2. in the root folder, execute `python build.py --test`
3. `cd` into the `backend/` folder and run `PYTHONPATH=$(pwd) pytest`

By default, unit tests are executed (marked via `pytest.mark.unit`). If you want to execute the integration tests, pass `--test-marker integration` to *options 1* or *2* or `-m "integration"` to *option 3*. This can be a valid pytest markexpression, hence it would also be possible to execute unit *and* integration tests by passing `"unit and integration"` to one of the flags. If neither unit nor integration tests should be executed, pass an unknown marker such as `notests`.
By default, the deployment tests are executed for the DockerDeploymentManager. If you want to execute them for the `KubernetesDeploymentManager`, set the environment variables `KUBERNETES_INTEGRATION_TESTS=True` and `DEPLOYMENT_MANAGER=kubernetes` (for example in an `.env` file in the [backend directory](./backend)).
Using option 1 (`act`) will create a Kubernetes cluster. If you don't use `act`, make sure that a Kubernetes cluster is accessible.

> ❗ To point to a running instance for Contaxy and execute the RemoteEndpoint tests, set the `REMOTE_BACKEND_TESTS=True` and `REMOTE_BACKEND_ENDPOINT=$endpoint` variables. For executing LocalEndpoint tests, make sure that the Postgres database and S3 storage are reachable from the locally spawned instance via the environment variables `POSTGRES_CONNECTION_URI`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`.

To run the stress tests, you have the following options:

1. `cd` into the `backend/` folder and execute, for example, `locust -f tests/endpoint_tests/locustfile.py --host=http://localhost:8000 --headless -t1m --csv=./tests/results/locust`

> ❗ For the stress tests, the `--host` flag **must** be set and pointing to a running Contaxy instance.
