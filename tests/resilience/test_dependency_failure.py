import pytest

from lab.api import Api
from lab.docker import Docker
from lab.wait import wait_for


@pytest.fixture
def docker():
    docker = Docker()

    if not docker.dependency_running():
        docker.start_dependency()

    yield docker

    if not docker.dependency_running():
        docker.start_dependency()


@pytest.fixture
def api():
    return Api()


def test_api_recovers_when_dependency_restarts(docker, api):
    assert api.dependency_is_healthy()

    docker.stop_dependency()

    wait_for(api.dependency_is_unavailable)

    assert api.dependency_is_unavailable()

    docker.start_dependency()

    wait_for(api.dependency_is_healthy)

    assert api.dependency_is_healthy()


def test_api_recovers_from_hard_dependency_failure(docker, api):
    assert api.dependency_is_healthy()

    docker.kill_dependency()

    wait_for(api.dependency_is_unavailable)

    assert api.dependency_is_unavailable()

    docker.start_dependency()

    wait_for(api.dependency_is_healthy)

    assert api.dependency_is_healthy()


def test_api_recovers_from_network_failure(docker, api):
    assert api.dependency_is_healthy()

    docker.disconnect_dependency()

    assert docker.dependency_running()

    wait_for(api.dependency_is_unavailable)

    assert api.dependency_is_unavailable()

    docker.connect_dependency()

    wait_for(api.dependency_is_healthy)

    assert api.dependency_is_healthy()
