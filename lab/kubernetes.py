import subprocess


class Kubernetes:
    def __init__(self, dependency="dependency"):
        self.dependency = dependency

    def delete_dependency_pod(self):
        self._run(
            "kubectl",
            "delete",
            "pod",
            "-l",
            f"app={self.dependency}",
        )

    def dependency_pod_name(self):
        result = self._run(
            "kubectl",
            "get",
            "pods",
            "-l",
            f"app={self.dependency}",
            "-o",
            "jsonpath={.items[0].metadata.name}",
            check=False,
        )
        if result.returncode != 0:
            return None

        return result.stdout.strip() or None

    def dependency_pod_ready(self):
        result = self._run(
            "kubectl",
            "get",
            "pods",
            "-l",
            f"app={self.dependency}",
            "-o",
            "jsonpath={.items[0].status.containerStatuses[0].ready}",
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    @staticmethod
    def _run(*command, check=True):
        return subprocess.run(
            command,
            check=check,
            capture_output=True,
            text=True,
        )
