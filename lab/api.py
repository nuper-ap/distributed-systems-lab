import json
from urllib.error import HTTPError
from urllib.request import urlopen


class Api:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url

    def dependency(self):
        return self._get("/dependency")

    def health(self):
        return self._get("/health")

    def _get(self, path):
        try:
            response = urlopen(
                f"{self.base_url}{path}",
                timeout=5,
            )

            return response.status, json.loads(response.read())

        except HTTPError as exc:
            return exc.code, json.loads(exc.read())
