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

    # Always leave the environment healthy for the next test.
    if not docker.dependency_running():
        docker.start_dependency()


@pytest.fixture
def api():
    return Api()


def test_api_recovers_when_dependency_restarts(docker, api):
    # Establish the initial healthy state.
    status, body = api.dependency()

    assert status == 200
    assert body["status"] == "ok"

    # Inject the failure.
    docker.stop_dependency()

    # The system should eventually observe the dependency failure.
    wait_for(
        lambda: api.dependency()[0] == 503,
        timeout=10,
    )

    status, body = api.dependency()

    assert status == 503
    assert body["status"] == "error"

    # Restore the dependency.
    docker.start_dependency()

    # The API should eventually recover.
    wait_for(
        lambda: api.dependency()[0] == 200,
        timeout=10,
    )

    status, body = api.dependency()

    assert status == 200
    assert body["status"] == "ok"

def test_api_recovers_from_hard_dependency_failure(docker, api):
    # Establish healthy state.
    status, body = api.dependency()

    assert status == 200
    assert body["status"] == "ok"

    # Kill the dependency without giving it a chance to shut down gracefully.
    docker.kill_dependency()

    # The API should eventually detect the failure.
    wait_for(
        lambda: api.dependency()[0] == 503,
        timeout=10,
    )

    # Restore the dependency.
    docker.start_dependency()

    # The API should eventually recover.
    wait_for(
        lambda: api.dependency()[0] == 200,
        timeout=10,
    )
