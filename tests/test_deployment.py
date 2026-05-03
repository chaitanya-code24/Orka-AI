import unittest
from pathlib import Path


class DeploymentTests(unittest.TestCase):
    def test_dockerfile_runs_fastapi_app(self):
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")

        self.assertIn("FROM python:3.11-slim", dockerfile)
        self.assertIn("uvicorn", dockerfile)
        self.assertIn("orka.main:app", dockerfile)

    def test_compose_exposes_api_and_persists_data(self):
        compose = Path("docker-compose.yml").read_text(encoding="utf-8")

        self.assertIn("8000:8000", compose)
        self.assertIn("orka-data", compose)
        self.assertIn("ORKA_CONNECTOR_MODE", compose)

    def test_dockerignore_excludes_local_secrets_and_database(self):
        dockerignore = Path(".dockerignore").read_text(encoding="utf-8")

        self.assertIn(".env", dockerignore)
        self.assertIn("*.db", dockerignore)


if __name__ == "__main__":
    unittest.main()
