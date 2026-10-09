# Distributed Systems Testing Lab

A hands-on lab for testing distributed systems, fault tolerance, and recovery using Python, pytest, Docker, and Kubernetes.

The goal is to validate system behavior under failure, not just verify that services work under normal conditions.

## What is tested?

### Docker resilience

Tests the API's behavior when its dependency:

* Is stopped and restarted.
* Is killed unexpectedly.
* Loses network connectivity.

The tests verify that the API detects the dependency failure and recovers when connectivity or service availability returns.

### Kubernetes resilience

Tests Kubernetes self-healing by deleting a dependency Pod managed by a Deployment.

The test verifies that Kubernetes creates a replacement Pod, that the replacement becomes ready, and that the API is healthy afterward.

## Architecture

The lab uses two services:

* **API:** exposes health and dependency endpoints on port `8080`.
* **Dependency:** exposes a health endpoint on port `9000`.

The API calls the dependency and reports an error when it is unavailable.

Two separate environments run these services:

* **Docker:** standalone containers connected through `lab-network`.
* **Kubernetes:** Deployments and Services running in a local Kind cluster.

The Kubernetes API is accessed by the tests through a temporary `kubectl port-forward`, managed automatically by pytest.

## Prerequisites

Install the following tools:

* Python and `venv`
* pytest
* Docker Engine
* `kubectl`
* Kind

The Docker tests require the standalone Docker containers to be running.

The Kubernetes tests require the Kind cluster and Kubernetes workloads to have been created and deployed beforehand.

## Run the tests

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Run the Docker resilience tests:

```bash
pytest -v tests/resilience/test_dependency_failure.py
```

Run the Kubernetes resilience tests:

```bash
pytest -v tests/resilience/test_kubernetes_resilience.py
```

Run the complete resilience suite:

```bash
pytest -v tests/resilience/
```

The Kubernetes test manages its own port-forward. You do not need to start one manually.

## Project structure

```text
applications/
  api/                 API service and Dockerfile
  dependency/           Dependency service and Dockerfile
lab/
  api.py                HTTP client used by tests
  docker.py             Docker fault-injection helpers
  kubernetes.py         Kubernetes operations
  wait.py               Condition-based polling
k8s/
  kind-config.yaml      Local Kind cluster configuration
  api.yaml              API Deployment
  api-service.yaml      API Service
  dependency.yaml       Dependency Deployment
  dependency-service.yaml
tests/
  resilience/
    test_dependency_failure.py
    test_kubernetes_resilience.py
```

## Design principles

* **Test behavior, not implementation details.**
* **Inject controlled failures** and verify observable outcomes.
* **Wait for conditions** instead of relying on arbitrary sleeps.
* **Keep test intent explicit.** Abstractions should simplify infrastructure interaction without hiding what a test is proving.
* **Separate environment setup from test execution** so tests can be run and debugged independently.

## Current limitations

* The Docker containers and Kind cluster must be provisioned before running the tests.
* The Kubernetes test assumes the API Service is named `api` and the dependency Deployment is named `dependency`.
* The port-forward uses local port `18080`, which must be available.
* The current suite verifies eventual health and Kubernetes Pod replacement; it does not yet measure recovery time or guarantee that every injected failure produces an observable outage.

