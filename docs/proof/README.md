# 🪞 MirrorProof — Proof of Care & Verification Layer

This directory holds canonical audit and verification artifacts for the **ELARRI / MirrorOS** ecosystem.

## 📜 Purpose
`docs/proof/` is the registry of ethical proofs, manifests, and certification records that establish provenance and accountability across all Mirror assets.

Every file here represents a **receipt of care** — a sealed record containing cryptographic hashes, timestamps, and verification links to public or internal manifests.

## 📂 Folder Contents
| File | Description |
|------|--------------|
| `MirrorSigil_ProofChain_Summary_v1.md` | Full audit summary (Markdown) |
| `MirrorSigil_ProofChain_Summary_v1.pdf` | Print-safe formatted one-pager |
| `bundle_manifest.json` | Machine-readable manifest index |
| `README.md` | This file |

## 🧭 Verification
Each proof entry links to a verification endpoint:

- **Master Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_v1_CAC>  
- **Plate Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_v1_plate>  
- **COA Manifest:** <https://verify.ellari.ai/proof/MirrorSigil_COA_v1>

To verify integrity, compute each file’s SHA-256 hash and compare it to the value in `bundle_manifest.json`.

## 🧠 Integration
The **mirrorvault-receipts-viewer** automatically renders `.md` and `.json` files found here for public validation.

## 🕊 License
All proof artifacts are released under the **Proof-of-Care Invocation Standard v1**.

> *“Proof before power. Receipts before rhetoric.”*
