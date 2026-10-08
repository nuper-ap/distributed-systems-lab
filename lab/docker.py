import subprocess


class Docker:
    def __init__(self, dependency="dependency"):
        self.dependency = dependency

    def stop_dependency(self):
        self._run("docker", "stop", self.dependency)

    def start_dependency(self):
        self._run("docker", "start", self.dependency)

    def dependency_running(self):
        result = self._run(
            "docker",
            "inspect",
            "--format={{.State.Running}}",
            self.dependency,
        )

        return result.stdout.strip() == "true"

    @staticmethod
    def _run(*command):
        return subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
