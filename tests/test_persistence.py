from pathlib import Path
import tempfile
import unittest

from nightfall_gargoyle.persistence import load_save, new_save, write_save
from nightfall_gargoyle.settings import GameConfig, load_config, save_config


class PersistenceTests(unittest.TestCase):
    def test_save_roundtrip_preserves_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "savegame.json"
            state = new_save(checkpoint=(42, 99))
            state.current_level = 1
            state.collected_shards.append("level:shard")
            state.defeated_enemies.append("level:enemy")
            write_save(state, path)

            loaded = load_save(path)

        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.current_level, 1)
        self.assertEqual(loaded.checkpoint, (42.0, 99.0))
        self.assertEqual(loaded.total_shards, 1)
        self.assertEqual(loaded.defeated_enemies, ["level:enemy"])

    def test_config_roundtrip_preserves_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            config = GameConfig(width=1600, height=900, fullscreen=True, master_volume=0.4)
            save_config(config, path)
            loaded = load_config(path)

        self.assertEqual(loaded.window_size, (1600, 900))
        self.assertTrue(loaded.fullscreen)
        self.assertEqual(loaded.master_volume, 0.4)


if __name__ == "__main__":
    unittest.main()
