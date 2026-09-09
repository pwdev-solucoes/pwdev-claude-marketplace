import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1] / 'plugins/sdd-composy/scripts'))
import sdd_evidence


class EvidencePublicationSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / 'run.txt').write_text('ok')
        self.data = {'prd_slug': 'demo', 'task_id': 'TASK-001', 'entries': [{
            'requirement_id': 'RF-001', 'story_id': 'US-001', 'scenario_id': 'SC-001',
            'criterion_id': 'CA-001', 'test_id': 'TEST-001', 'result': 'passed',
            'evidence_type': 'log', 'path': 'run.txt'}]}

    def test_predictable_temporary_symlink_cannot_overwrite_another_file(self):
        victim = self.root / 'valuable.txt'
        victim.write_text('preserve')
        trap = self.root / 'manifest.json.tmp'
        trap.symlink_to(victim)
        sdd_evidence.build(self.data, self.root, self.root / 'manifest.json')
        self.assertEqual(victim.read_text(), 'preserve')
        self.assertTrue(trap.is_symlink())

    def test_failed_replace_preserves_existing_manifest_and_cleans_temp(self):
        target = self.root / 'manifest.json'
        target.write_text('original')
        before = set(self.root.iterdir())
        with patch.object(sdd_evidence.os, 'replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                sdd_evidence.build(self.data, self.root, target)
        self.assertEqual(target.read_text(), 'original')
        self.assertEqual(set(self.root.iterdir()), before)

    def test_parent_symlink_destination_is_rejected(self):
        real = self.root / 'real'; real.mkdir()
        (self.root / 'alias').symlink_to(real, target_is_directory=True)
        with self.assertRaises(ValueError):
            sdd_evidence.build(self.data, self.root, self.root / 'alias/manifest.json')

    def test_html_uses_persisted_workspace_language(self):
        config = self.root / '.planning/sdd-composy/config.json'
        config.parent.mkdir(parents=True)
        manifest = sdd_evidence.build(self.data, self.root)
        for language, title in [('pt-BR', 'Relatório de evidências'), ('en-US', 'Evidence report')]:
            config.write_text(json.dumps({'language': language}))
            target = self.root / 'report.html'
            sdd_evidence.export(manifest, target, self.root)
            self.assertIn(title, target.read_text())
        config.unlink()
        with self.assertRaises(ValueError):
            sdd_evidence.export(manifest, target, self.root)
