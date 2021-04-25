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

Contaxy is an extensible collaborative platform for teams to share files and deploy services and jobs easily using Docker or Kubernetes.The platform is secured so only members of a project can access its resources (files, services, jobs). Its strong extension system allows to add further functionality to the backend and web app and also to override the behavior of Contaxy's core endpoints. By adding project members or generating fine-granular access tokens, resources can easily be shared with others. Deploying a service and securely sharing it with a stakeholder? No problem.

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

#### Deploy Behind a Proxy

If you deploy Contaxy behind a proxy, you can define a base url. It must not end with a slash. For example, if the web app should be accessible behind /test/app instead of /app, the CONTAXY_BASE_URL would be defined as /test.

#### Use external OAuth2/OIDC Identity Provider

The application needs to be registered at the desired identity provider as a prerequisite. The IDP requires a redirect URI which is `https://{CONTAXY_HOST}/api/auth/oauth/callback`. For further details on how to registering the application at your IDP you should refer to it's documentation (e.g. [Google](https://developers.google.com/identity/protocols/oauth2/web-server)). Moreover, the following env variables need to be added to contaxy:

- CONTAXY_HOST - The domain where contaxy gets deployed without scheme and path, e.g. if the app will be accessible under `https://home.contaxy.com/app` then you need to set `home.contaxy.com`.
- OIDC_AUTH_ENABLED - Set to 1
- OIDC_AUTH_URL - The OAuth2 authentication endpoint of the IDP
- OIDC_TOKEN_URL - The OAuth2 endpint of the IDP to exchange an authorization code for an access token / identity token
- OIDC_CLIENT_ID - The client ID of the application obtained from the IDP during app registration
- OIDC_CLIENT_SECRET - The client secret of the application obtained from the IDP during app registration

If you want to prevent user registration via the default username / password flow, then you can set USER_REGISTRATION_ENABLED=0. You still need to initially create an admin user.

#### Initialize and register admin user

In order to initialze the system and create the admin user, call the endpoint `/api/system/admin-form` on the started instance and submit the form. This can only be done once.

### Usage

After initializing, visit `/app/`.

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

By default, unit tests are executed (marked via `pytest.mark.unit`). If you want to execute the integration tests, pass `--test-marker integration` to _options 1_ or _2_ or `-m "integration"` to _option 3_. This can be a valid pytest markexpression, hence it would also be possible to execute unit _and_ integration tests by passing `"unit and integration"` to one of the flags. If neither unit nor integration tests should be executed, pass an unknown marker such as `notests`.
By default, the deployment tests are executed for the DockerDeploymentManager. If you want to execute them for the `KubernetesDeploymentManager`, set the environment variables `KUBERNETES_INTEGRATION_TESTS=True` and `DEPLOYMENT_MANAGER=kubernetes` (for example in an `.env` file in the [backend directory](./backend)).
Using option 1 (`act`) will create a Kubernetes cluster. If you don't use `act`, make sure that a Kubernetes cluster is accessible.

> ❗ To point to a running instance for Contaxy and execute the RemoteEndpoint tests, set the `REMOTE_BACKEND_TESTS=True` and `REMOTE_BACKEND_ENDPOINT=$endpoint` variables. For executing LocalEndpoint tests, make sure that the Postgres database and S3 storage are reachable from the locally spawned instance via the environment variables `POSTGRES_CONNECTION_URI`, `S3_ENDPOINT`, `S3_ACCESS_KEY`, `S3_SECRET_KEY`.

To run the stress tests, you have the following options:

1. `cd` into the `backend/` folder and execute, for example, `locust -f tests/endpoint_tests/locustfile.py --host=http://localhost:8000 --headless -t1m --csv=./tests/results/locust`

> ❗ For the stress tests, the `--host` flag **must** be set and pointing to a running Contaxy instance.
