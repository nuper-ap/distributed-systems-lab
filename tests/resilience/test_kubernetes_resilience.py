import socket
import subprocess

import pytest

from lab.api import Api
from lab.kubernetes import Kubernetes
from lab.wait import wait_for


@pytest.fixture
def kubernetes():
    return Kubernetes()


@pytest.fixture
def api():
    port_forward = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            "service/api",
            "18080:8080",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    def port_is_open():
        if port_forward.poll() is not None:
            return False

        try:
            with socket.create_connection(
                ("127.0.0.1", 18080),
                timeout=0.2,
            ):
                return True
        except OSError:
            return False

    try:
        wait_for(port_is_open, timeout=10)
        yield Api(base_url="http://localhost:18080")
    finally:
        port_forward.terminate()

        try:
            port_forward.wait(timeout=5)
        except subprocess.TimeoutExpired:
            port_forward.kill()
            port_forward.wait()


# Keep your existing test function below this line.


@pytest.fixture
def kubernetes():
    return Kubernetes()


def test_api_recovers_when_dependency_pod_is_deleted(kubernetes, api):
    assert api.dependency_is_healthy()

    original_pod = kubernetes.dependency_pod_name()
    assert original_pod is not None

    kubernetes.delete_dependency_pod()

    wait_for(
        lambda: (
            (new_pod := kubernetes.dependency_pod_name()) is not None
            and new_pod != original_pod
        )
    )

    wait_for(kubernetes.dependency_pod_ready)
    wait_for(api.dependency_is_healthy)

    assert kubernetes.dependency_pod_name() != original_pod
    assert api.dependency_is_healthy()


