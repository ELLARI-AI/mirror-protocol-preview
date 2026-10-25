import base64
import hashlib
import os
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "verify-proof-bundle.sh"


class VerifyProofBundleTests(unittest.TestCase):
    def setUp(self):
        if shutil.which("jq") is None:
            self.skipTest("jq is required by the production verifier")
        self.temp = tempfile.TemporaryDirectory()
        self.proof_dir = Path(self.temp.name) / "proof"
        self.proof_dir.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def run_verifier(self, mode):
        return subprocess.run(
            ["bash", str(SCRIPT), mode, str(self.proof_dir)],
            check=False,
            capture_output=True,
            text=True,
        )

    def write_manifest(self, files):
        manifest = {
            "title": "Synthetic proof bundle",
            "version": "test-v1",
            "files": files,
            "issuer": "Synthetic test issuer",
            "license": "Synthetic test license",
        }
        (self.proof_dir / "bundle_manifest.json").write_text(
            json.dumps(manifest), encoding="utf-8"
        )

    def test_missing_manifest_fails_closed(self):
        result = self.run_verifier("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing manifest", result.stderr)

    def test_invalid_schema_fails_closed(self):
        (self.proof_dir / "bundle_manifest.json").write_text(
            json.dumps({
                "title": "Synthetic proof bundle",
                "version": "test-v1",
                "files": "not-an-array",
                "issuer": "Synthetic test issuer",
                "license": "Synthetic test license",
            }),
            encoding="utf-8",
        )
        result = self.run_verifier("validate")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Invalid proof manifest schema", result.stderr)

    def test_absent_referenced_file_fails_closed(self):
        self.write_manifest(["not-present.txt"])
        result = self.run_verifier("files")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing referenced proof file", result.stderr)

    def test_valid_bundle_passes_and_computes_hashes(self):
        payload = b"synthetic artifact\\n"
        (self.proof_dir / "artifact.txt").write_bytes(payload)
        self.write_manifest(["artifact.txt"])

        self.assertEqual(self.run_verifier("validate").returncode, 0)
        self.assertEqual(self.run_verifier("files").returncode, 0)
        result = self.run_verifier("hashes")
        self.assertEqual(result.returncode, 0)
        self.assertIn(hashlib.sha256(payload).hexdigest(), result.stdout)
        self.assertIn("artifact.txt", result.stdout)

    def test_hash_comment_treats_hashes_as_data(self):
        workflow = (
            SCRIPT.parents[1] / ".github" / "workflows" / "proof-verify-pr.yml"
        ).read_text(encoding="utf-8")
        output_expression = "$" + "{{ needs.verify.outputs.hashes_b64 }}"
        self.assertEqual(workflow.count(output_expression), 1)
        self.assertIn(f"HASHES_B64: {output_expression}", workflow)
        comment_job = workflow.split("  comment-hashes:", 1)[1]
        comment_run = comment_job.split("        run: |", 1)[1]
        self.assertNotIn("$" + "{{", comment_run)

        marker = self.proof_dir / "shell-was-executed"
        payload = f"$(touch {marker})"
        encoded = base64.b64encode(payload.encode("utf-8")).decode("ascii")
        env = os.environ.copy()
        env["HASHES_B64"] = encoded
        command = 'hashes="$(printf "%s" "$HASHES_B64" | base64 --decode)"; printf "%s\\n" "$hashes"'
        result = subprocess.run(
            ["bash", "-c", command],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, payload + "\\n")
        self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main()
