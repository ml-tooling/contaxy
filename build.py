import glob
import os
import shutil

from universal_build import build_utils

HERE = os.path.abspath(os.path.dirname(__file__))

REACT_WEBAPP_COMPONENT = "webapp"
DOCS_COMPONENT = "docs"
PYTHON_LIB_COMPONENT = "backend"


def main(args: dict) -> None:
    """Execute all component builds."""

    # set script path as working dir
    os.chdir(HERE)

    # Build react webapp
    # build_utils.build(REACT_WEBAPP_COMPONENT, args)
    # Build python lib
    build_utils.build(PYTHON_LIB_COMPONENT, args)

    if args.get(build_utils.FLAG_MAKE):
        # Duplicate api docs into the mkdocs documentation
        build_utils.duplicate_folder(
            f"./{PYTHON_LIB_COMPONENT}/docs/", f"./{DOCS_COMPONENT}/docs/api-docs/"
        )

    # Build mkdocs documentation
    # build_utils.build(DOCS_COMPONENT, args)


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
