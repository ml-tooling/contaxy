import glob
import os
import pathlib
import shutil

import urllib3
from universal_build import build_utils
from universal_build.helpers import build_docker, build_python

HERE = os.path.abspath(os.path.dirname(__file__))

WEBAPP_COMPONENT = "webapp"
DOCS_COMPONENT = "docs"
PYTHON_LIB_COMPONENT = "backend"
DOCKER_IMAGE_PREFIX = "mltooling"
COMPONENT_NAME = "contaxy"


def check_and_download_swagger_cli(file_path: str) -> bool:
    if not pathlib.Path(file_path).is_file():
        # build_utils.run('wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.23/swagger-codegen-cli-3.0.23.jar -O ./swagger-codegen-cli.jar')
        swagger_codegen_cli_download_url = "https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.23/swagger-codegen-cli-3.0.23.jar"
        response = urllib3.PoolManager().request(
            "GET", swagger_codegen_cli_download_url
        )
        if response.status == 200:
            with open(file_path, "wb") as f:
                f.write(response.data)
        else:
            return False
    return True


def generate_and_copy_js_client(swagger_path) -> bool:
    temp_dir = "./temp"
    pathlib.Path(temp_dir).mkdir(exist_ok=True)
    swagger_codegen_cli = f"{temp_dir}/swagger-codegen-cli.jar"
    is_successful = check_and_download_swagger_cli(swagger_codegen_cli)
    if not is_successful:
        return False
    output_path = f"{temp_dir}/client"
    if not pathlib.Path(swagger_path).is_file():
        build_utils.log(f"The OpenAPI spec file {swagger_path} does not exist")
        return False

    build_utils.run(
        f"java -jar {swagger_codegen_cli} generate -i {swagger_path} -l javascript -o {output_path} --additional-properties useES6=true"
    )
    # shutil.move(f"{output_path}/src/", "./webapp/src/services/mllab-client")
    try:
        for file in pathlib.Path(f"{output_path}/src/").iterdir():
            file_name = str(file.parts[-1])
            target_file_path = f"./webapp/src/services/contaxy-client/{file_name}"
            print(target_file_path)
            # Delete existing client files to be replaced with the new ones
            path = pathlib.Path(target_file_path)
            if path.exists():
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(target_file_path)
            else:
                path.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), target_file_path)
    except FileNotFoundError as e:
        build_utils.log(str(e))
        return False
    return True


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

        is_successful = generate_and_copy_js_client(
            f"./{PYTHON_LIB_COMPONENT}/openapi.json"
        )
        if not is_successful:
            build_utils.log("Error in generating the JavaScript client library")
            build_utils.exit_process(1)

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
