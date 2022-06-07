#  -*- coding: utf-8 -*-

import os
from pathlib import Path

import pytest


def file_contains_text(file: Path, text: str) -> bool:
    return open(file, "r").read().find(text) != -1


@pytest.fixture(scope="module")
def script_loc(request):
    """Return the directory of the currently running test script

    :param request:
    :return:
    """

    return Path(request.fspath).parent.parent


def test_cicd_contains_pypi_secrets(script_loc):
    """

    :return:
    """

    assert file_contains_text(
        script_loc.joinpath(".github/workflows/on-release-main.yml"), "PYPI_API_TOKEN"
    ), "The PYPI_API_TOKEN is missing from the GitHub workflow"
    assert file_contains_text(
        script_loc.joinpath("Makefile"), "build-and-publish"
    ), "From the Makefile is missing the build-and-publish command"


# def test_dont_publish(script_loc):
#     """
#
#     :param script_loc:
#     :return:
#     """
#     assert not file_contains_text(
#         script_loc.joinpath(".github/workflows/on-release-main.yml"), "make build-and-publish"
#     )


def test_mkdocs(script_loc):
    """

    :param script_loc:
    :return:
    """
    assert file_contains_text(
        script_loc.joinpath(".github/workflows/on-release-main.yml"), "mkdocs gh-deploy"
    )
    assert file_contains_text(script_loc.joinpath("Makefile"), "docs:")
    assert os.path.isdir(script_loc.joinpath("docs"))


#
# def test_not_mkdocs(cookies, tmp_path):
#     with run_within_dir(tmp_path):
#         result = cookies.bake(extra_context={"mkdocs": "n"})
#         assert not file_contains_text(
#             f"{result.project_path}/.github/workflows/on-release-main.yml", "mkdocs gh-deploy"
#         )
#         assert not file_contains_text(f"{result.project_path}/Makefile", "docs:")
#         assert not os.path.isdir(f"{result.project_path}/docs")
#
#


def test_tox(script_loc):
    """

    :param script_loc:
    :return:
    """
    assert file_contains_text(
        script_loc.joinpath(".github/workflows/on-release-main.yml"),
        "poetry add tox-gh-actions",
    )
    assert file_contains_text(
        script_loc.joinpath(".github/workflows/on-merge-to-main.yml"),
        "poetry add tox-gh-actions",
    )
    assert file_contains_text(
        script_loc.joinpath(".github/workflows/on-pull-request.yml"),
        "poetry add tox-gh-actions",
    )
    assert os.path.isfile(script_loc.joinpath("tox.ini"))


#
# def test_not_tox(cookies, tmp_path):
#     with run_within_dir(tmp_path):
#         result = cookies.bake(extra_context={"tox": "n"})
#         assert not file_contains_text(
#             f"{result.project_path}/.github/workflows/on-release-main.yml", "poetry add tox-gh-actions"
#         )
#         assert not os.path.isfile(f"{result.project_path}/tox.ini")
