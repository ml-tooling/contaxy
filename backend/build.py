import os
from pathlib import Path

from universal_build import build_utils
from universal_build.helpers import build_python

# Project specific configuration
MAIN_PACKAGE = "contaxy"
GITHUB_URL = "https://github.com/ml-tooling/contaxy"

HERE = os.path.abspath(os.path.dirname(__file__))

STRESS_TEST_MARKER = "stress"


def main(args: dict) -> None:
    # set current path as working dir
    os.chdir(HERE)

    version = args.get(build_utils.FLAG_VERSION)

    if version:
        # Update version in _about.py
        build_python.update_version(
            os.path.join(HERE, f"src/{MAIN_PACKAGE}/_about.py"),
            build_utils._Version.get_pip_compatible_string(str(version)),
            exit_on_error=True,
        )

    if args.get(build_utils.FLAG_MAKE):
        # Install pipenv dev requirements
        build_python.install_build_env(exit_on_error=True)

        # Generate the OpenAPI spec so that clients can be generated
        swagger_path = f"src/{MAIN_PACKAGE}/generate-openapi-specs.py"
        build_utils.run(f"pipenv run python {swagger_path}")

        # Create API documentation via lazydocs
        build_python.generate_api_docs(
            github_url=GITHUB_URL, main_package=MAIN_PACKAGE, exit_on_error=True
        )
        # Build distribution via setuptools
        build_python.build_distribution(exit_on_error=True)

    if args.get(build_utils.FLAG_CHECK):
        build_python.code_checks(exit_on_error=True)

    if args.get(build_utils.FLAG_TEST):
        build_utils.run("pipenv run coverage erase", exit_on_error=False)

        test_markers = args.get(build_utils.FLAG_TEST_MARKER)
        print(test_markers)
        if isinstance(test_markers, list) and STRESS_TEST_MARKER in test_markers:
            locust_cmd_args = os.getenv("LOCUST_CMD_ARGS", None)
            if not locust_cmd_args:
                test_results_dir = "./tests/results"
                Path(test_results_dir).mkdir(parents=False, exist_ok=True)
                locust_cmd_args = f"-f tests/endpoint_tests/locustfile.py --host=http://localhost:8000 --headless -t1m --csv {test_results_dir}/locust"

            build_utils.run(f"locust {locust_cmd_args}")
        else:
            # Activated Python Environment (3.8)
            build_python.install_build_env()
            # Run pytest in pipenv environment
            build_utils.run("pipenv run pytest tests", exit_on_error=True)

            # Update pipfile.lock when all tests are successfull (lock environment)
            build_utils.run("pipenv lock", exit_on_error=True)

    if args.get(build_utils.FLAG_RELEASE):
        # Publish distribution on pypi
        build_python.publish_pypi_distribution(
            pypi_token=args.get(build_python.FLAG_PYPI_TOKEN),
            pypi_repository=args.get(build_python.FLAG_PYPI_REPOSITORY),
        )

        # TODO: Publish coverage report: if private repo set CODECOV_TOKEN="token" or use -t
        # build_utils.run("curl -s https://codecov.io/bash | bash -s", exit_on_error=False)


if __name__ == "__main__":
    args = build_python.parse_arguments()
    main(args)
