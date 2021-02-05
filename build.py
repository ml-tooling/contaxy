"""Root build.py for the Contaxy project. Will also execute the build.py in sub-directories."""

import os

from universal_build import build_utils, openapi_utils
from universal_build.helpers import build_docker, build_python

HERE = os.path.abspath(os.path.dirname(__file__))

WEBAPP_COMPONENT = "webapp"
DOCS_COMPONENT = "docs"
PYTHON_LIB_COMPONENT = "backend"
DOCKER_IMAGE_PREFIX = "mltooling"
COMPONENT_NAME = "contaxy"


def main(args: dict) -> None:
    """Execute all component builds."""

    # set script path as working dir
    os.chdir(HERE)

    version = args.get(build_utils.FLAG_VERSION)

    # Build python lib
    build_utils.build(PYTHON_LIB_COMPONENT, args)

    # TODO: create FastAPI OpenAPI definition
    # TODO: copy OpenAPI definition to Web App
    if args.get(build_utils.FLAG_MAKE):
        # Duplicate api docs into the mkdocs documentation
        build_utils.duplicate_folder(
            f"./{PYTHON_LIB_COMPONENT}/docs/", f"./{DOCS_COMPONENT}/docs/api-docs/"
        )

        output_path = openapi_utils.generate_openapi_js_client(
            openapi_spec_file=f"./{PYTHON_LIB_COMPONENT}/openapi.json"
        )
        is_successful = False
        if output_path:
            is_successful = openapi_utils.copy_openapi_client(
                source_dir=f"{output_path}/src",
                target_dir="./webapp/src/services/contaxy-client/",
            )

        if not is_successful:
            build_utils.log("Error in generating the JavaScript client library")
            # build_utils.exit_process(1)

    build_utils.build(WEBAPP_COMPONENT, args)

    # Build mkdocs documentation
    # build_utils.build(DOCS_COMPONENT, args)

    # Build all docker component
    docker_image_prefix = args.get(build_docker.FLAG_DOCKER_IMAGE_PREFIX)

    if not docker_image_prefix:
        docker_image_prefix = DOCKER_IMAGE_PREFIX  # type: ignore

    if args.get(build_utils.FLAG_MAKE):
        build_docker.build_docker_image(COMPONENT_NAME, version, exit_on_error=True)

    if args.get(build_utils.FLAG_CHECK):
        build_docker.lint_dockerfile(exit_on_error=True)


if __name__ == "__main__":
    args = build_utils.parse_arguments()

    if args.get(build_utils.FLAG_RELEASE):
        # Run main without release to see whether everthing can be built and all tests run through
        # Run args without release to see whether everthing can be built and all tests run through
        args = dict(args)
        args[build_utils.FLAG_RELEASE] = False
        main(args)
        # Run main again without building and testing the components again
        args = {
            **args,
            build_utils.FLAG_MAKE: False,
            build_utils.FLAG_CHECK: False,
            build_utils.FLAG_TEST: False,
            build_utils.FLAG_RELEASE: True,
            build_utils.FLAG_FORCE: True,
        }
    main(args)
