# Reproduce Beyond the Blob V6

The archive contains the anonymous LaTeX, compiled PDFs, generated vector figures and tables, code, score arrays, checksums, fit and test locks, and public source inventories. It carries the preceding reproducibility archive's public contents. Raw CT, the restricted LNDb manifest, and restricted LNDb row-level data stay with the authorized run.

## Saved-score replay

Extract the archive into an empty directory. Use Python 3.9.17 with the versions in `paper/revision_v6/requirements-v6.txt` and TeX Live 2026 with latexmk. Run from the extraction root.

    PYTHON_BIN=/path/to/python bash paper/revision_v6/reproduce.sh

The script verifies the distributed files, rechecks the original LUNA16 paired statistics with the V5 evaluator, recalculates the viewed and fresh V6 metrics, regenerates the paired location transitions, rebuilds all tables and vector figures, and compiles both PDFs. The archive records expected SHA-256s for each output. The seed- and block-level score arrays are the inputs to this replay. The wall-clock timing figure values use the recorded timing audit.

## Independent rerender from verified background caches

Use a second extraction and a new scratch directory.

    PYTHON_BIN=/path/to/python bash paper/revision_v6/reproduce.sh \
      --v5-cache /path/to/v5-cache \
      --backgrounds /path/to/v6/backgrounds \
      --authorized-root /path/to/authorized/project \
      --cache /path/to/empty/v6-cache --workers 66 --device cuda:2

The V5 cache contains `backgrounds/`, `scenes/`, `windows/`, and `broad/backgrounds/`. The V6 background directory contains `calibration.npz`, `test.npz`, `native_dev.npz`, and `transfer.npz`. Background hashes are checked against their role manifests. The authorized project supplies the locked V5 transfer manifest. The reference GPU for exact hybrid inference replay is the RTX A1000, CUDA device 2 with PCI enumeration and PyTorch 2.8.0+cu128. The candidate scorer for the fresh experiments is CPU-only. The execution host's staging locations are `/tmp/anatomy-revision-v5` and `/tmp/anatomy-revision-v6/backgrounds`.

The script rerenders the same-window V5 ablations, refits their heads, and re-evaluates the saved V6 hybrid checkpoints. It independently renders the broad fitting and development scenarios and verifies the complete fitted coefficients and selection grid against the seal. It rerenders the negative calibration, broader holdout, and native-background transfer, regenerates candidate scores and statistical summaries, and rebuilds both PDFs. Use `--numeric-only` to stop after the statistical and numerical checksum verification.

## Restage CT backgrounds

Run these commands in a clean extraction. Export the Python search path and single-thread environment as in `reproduce.sh`.

- LUNA16 staging verifies the original MHD and RAW members against the official inventory and uses the included and irrelevant reference findings. Supply the authorized V5 transfer manifest and V3 LNDb manifests under their recorded paths. Give `stage_v6.py luna --luna /path/to/luna0-5 --luna-reserve /path/to/luna6-9 --cache /path/to/v6/backgrounds` the released subset directories. The LUNA16 result roles are disjoint from all focused V5 outcome roles and the broad fitting folds. The simulator seeds have separate role namespaces.
- HiPaS staging uses release v2 with the published CT ZIP directory, annotation ZIP and voxel metadata. Supply the 24 verified development members with `stage_v6.py native_dev --hipas-dev /path/to/viewed/hipas --cache /path/to/v6/backgrounds`. The prior V4 `hipas_fetch.py` obtains those members and the ZIP central-directory tail. The V6 `fetch_hipas.py` reuses that local tail and metadata from `/tmp/anatomy-revision-v4/hipas` and obtains the predetermined reserve members with ZIP ranges. Run `fetch_hipas.py --cache /path/to/hipas-reserve` from a scratch extraction, then `stage_v6.py transfer --hipas /path/to/hipas-reserve --cache /path/to/v6/backgrounds`. Verify against the archived manifests.
- The parent V5 instructions give the initial focused and broad cache inputs. The broad fitting and development manifests required here are included. The V5 simulation, forecaster, and evaluator are reused.

The original hybrid training order was `learned.py local`, `learned.py easy`, then `learned.py compare`, each with `--cache /path/to/v5-cache --device cuda:2`. Train in a scratch extraction and keep the sealed published checkpoints for the quantitative replay. The optional `cost_audit.py` reruns the single-thread timing on the verified V5 development cases after the same-window development features are present. Wall-clock measurements vary with hardware and load.

## Primary data and format references

[LUNA16 release](https://luna16.grand-challenge.org/Data/), [HiPaS v2 release](https://doi.org/10.5281/zenodo.14879605), [LNDb release](https://doi.org/10.5281/zenodo.7153205), [CVPR 2027 author guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines).
