# 🪞 MirrorProof — Proof of Care & Verification Layer

This directory holds audit and verification artifacts for the **ELARRI / MirrorOS** ecosystem.

## 📜 Purpose
`docs/proof/` is the registry of proof artifacts and supporting records.

## 📂 Folder Contents
| File | Description |
|------|--------------|
| `MirrorSigil_ProofChain_Summary_v1.md` | Full audit summary (Markdown) |
| `MirrorSigil_ProofChain_Summary_v1.docx` | Editable summary recovered byte-for-byte from the preserved bundle archive |
| `MirrorSigil_ProofChain_Summary_v1.pdf` | Print-safe formatted one-pager |
| `MirrorSigil_ProofChain_Summary_v1_bundle.zip` | Preserved original archive containing the source bundle files and its original manifest |
| `bundle_manifest.json` | Preview-specific machine-readable manifest |
| `README.md` | This file |

The standalone Markdown, DOCX, and PDF are the files named by the original manifest inside the preserved ZIP. The DOCX was restored from that archive; the original ZIP remains unchanged. The preview manifest's issuer and license fields are transcribed from the summary and this README.

## 🧭 Verification
Each proof entry links to a verification endpoint:

- **Master Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_v1_CAC>
- **Plate Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_v1_plate>
- **COA Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_COA_v1>

The weekly and PR workflows validate the manifest schema, check that referenced files exist, and compute SHA-256 hashes for reporting. They do not compare those hashes with an independently authenticated digest or signature. These checks establish file presence and hash computation; by themselves, they do not establish provenance or independently authenticated integrity.

## 🧠 Integration
The **mirrorvault-receipts-viewer** automatically renders `.md` and `.json` files found here for public validation.

## 🕊 License
All proof artifacts are released under the **Proof-of-Care Invocation Standard v1**.

> *“Proof before power. Receipts before rhetoric.”*
