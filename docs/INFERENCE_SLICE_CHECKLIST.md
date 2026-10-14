# Inference Slice Checklist

Pre-push checklist for each additive slice on AGI_SDK (companion to INFERENCE_SLICE.md, which stays unchanged).

1. `git pull` on `main`; confirm a clean tree.
2. Pick a brand-new path; confirm it does not already exist.
3. Add exactly one file. Do not edit or delete existing files.
4. No `.github/workflows` changes.
5. No model weights or downloads (`GIT_LFS_SKIP_SMUDGE=1`).
6. One commit, one push to `main`; record the SHA.
