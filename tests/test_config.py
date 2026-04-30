import json
import tempfile
import unittest
from pathlib import Path

from orka.config import load_config
from orka.core.exceptions import ConfigError


class ConfigLoaderTests(unittest.TestCase):
    def test_load_config_supports_legacy_llm_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(
                json.dumps(
                    {
                        "llm": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
                        "tools": ["create_customer_tool"],
                    }
                ),
                encoding="utf-8",
            )

            config = load_config(str(config_path))

            self.assertEqual(config.tools, ["create_customer_tool"])
            self.assertIsNotNone(config.model)
            self.assertEqual(config.model.provider, "groq")

    def test_load_config_requires_tools(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            config_path.write_text(json.dumps({"tools": []}), encoding="utf-8")

            with self.assertRaises(ConfigError):
                load_config(str(config_path))


if __name__ == "__main__":
    unittest.main()
