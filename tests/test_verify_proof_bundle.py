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

        self.assertIn("GH_REPO: " + "$" + "{{ github.repository }}", comment_job)
        self.assertNotIn("actions/checkout", comment_job)
        self.assertIn("pull-requests: write", comment_job)
        verify_job = workflow.split("  verify:", 1)[1].split("  comment-hashes:", 1)[0]
        self.assertNotIn("pull-requests: write", verify_job)

        # Execute the workflow's actual shell in a directory with no .git.
        # A fake gh checks explicit repository context and captures the body.
        marker = self.proof_dir / "shell-was-executed"
        payload = f"$(touch {marker})\n`touch {marker}`"
        fake_bin = self.proof_dir / "bin"
        fake_bin.mkdir()
        gh = fake_bin / "gh"
        gh.write_text(
            '#!/bin/bash\n'
            'test "$GH_REPO" = "example/repository" || exit 41\n'
            'test "$1" = pr && test "$2" = comment && test "$3" = 123 || exit 42\n'
            'test "$4" = --body-file || exit 43\n'
            'cat "$5" > "$CAPTURE"\n',
            encoding="utf-8",
        )
        gh.chmod(0o755)
        env = os.environ.copy()
        env.update({
            "HASHES_B64": base64.b64encode(payload.encode()).decode("ascii"),
            "GH_REPO": "example/repository",
            "PR_NUMBER": "123",
            "CAPTURE": str(self.proof_dir / "captured"),
            "PATH": str(fake_bin) + os.pathsep + env["PATH"],
        })
        import textwrap
        command = textwrap.dedent(comment_run)
        result = subprocess.run(
            ["bash", "-e", "-c", command], cwd=self.proof_dir,
            capture_output=True, text=True, env=env,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(payload, (self.proof_dir / "captured").read_text())
        self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main()
