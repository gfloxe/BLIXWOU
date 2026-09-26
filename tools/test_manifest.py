import json
from pathlib import Path
import tempfile
import unittest
from build_manifest import build


class ManifestTests(unittest.TestCase):
    def test_publish_and_same_size_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            settings = json.loads((Path(__file__).resolve().parents[1] / 'pack.json').read_text())
            settings['ready'] = True
            (root / 'pack.json').write_text(json.dumps(settings))
            (root / 'mods').mkdir()
            (root / 'server-mods').mkdir()
            (root / 'server-mods/ignored.jar').write_bytes(b'server')
            (root / 'mods/serveurutils-neoforge-1.21.1-1.5.0.jar').write_bytes(b'client and server')
            mod = root / 'mods/a.jar'
            mod.write_bytes(b'first')
            first = build(root, 'example/BLIXWOU', 'a' * 40)
            mod.write_bytes(b'other')
            second = build(root, 'example/BLIXWOU', 'b' * 40)
            first_files = {entry['path']: entry for entry in first['files']}
            second_files = {entry['path']: entry for entry in second['files']}
            self.assertEqual(set(second_files), {
                'mods/a.jar', 'mods/serveurutils-neoforge-1.21.1-1.5.0.jar'
            })
            self.assertEqual(first_files['mods/a.jar']['size'], second_files['mods/a.jar']['size'])
            self.assertNotEqual(first_files['mods/a.jar']['sha256'], second_files['mods/a.jar']['sha256'])
            self.assertIn('/' + 'b' * 40 + '/', second_files['mods/a.jar']['url'])

    def test_unready_pack_is_not_published(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'pack.json').write_text('{"ready": false}')
            self.assertIsNone(build(root, 'example/BLIXWOU', 'a' * 40))
            self.assertFalse((root / 'manifest.json').exists())


if __name__ == '__main__':
    unittest.main()
