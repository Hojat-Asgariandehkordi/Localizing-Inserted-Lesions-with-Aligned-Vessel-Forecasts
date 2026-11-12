#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
export PYTHONPATH="$PWD:$PWD/runs/revision_v3/code:$PWD/runs/revision_v4/code:$PWD/runs/revision_v5/code:$PWD/runs/revision_v6/code"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
export MPLBACKEND=Agg SOURCE_DATE_EPOCH=1794268800 FORCE_SOURCE_DATE=1
export CUDA_DEVICE_ORDER=PCI_BUS_ID CUBLAS_WORKSPACE_CONFIG=:4096:8
py="${PYTHON_BIN:-python3}"
run=runs/revision_v6
code="$run/code"
paper=paper/revision_v6
v5=
backgrounds=
authorized=
cache=
workers=40
device=cuda:2
numeric_only=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --v5-cache) v5="$(realpath "$2")"; shift 2 ;;
        --backgrounds) backgrounds="$(realpath "$2")"; shift 2 ;;
        --authorized-root) authorized="$(realpath "$2")"; shift 2 ;;
        --cache) cache="$(realpath -m "$2")"; shift 2 ;;
        --workers) workers="$2"; shift 2 ;;
        --device) device="$2"; shift 2 ;;
        --numeric-only) numeric_only=1; shift ;;
        *) printf 'Unknown argument %s\n' "$1" >&2; exit 2 ;;
    esac
done

if [[ -f V6_SHA256SUMS ]]; then sha256sum -c --quiet V6_SHA256SUMS; fi
if [[ -z "$cache" ]]; then cache="$(mktemp -d /tmp/btb-v6-replay.XXXXXX)"; fi
mkdir -p "$cache"
"$py" runs/revision_v5/code/verify_public.py

if [[ -n "$backgrounds" || -n "$v5" ]]; then
    test -n "$backgrounds" && test -n "$v5"
    broad="$v5/broad/backgrounds"
    if [[ ! -e "$cache/backgrounds" ]]; then ln -s "$backgrounds" "$cache/backgrounds"; fi
    transfer_manifest=runs/revision_v5/manifests/transfer.json
    if [[ ! -f "$transfer_manifest" ]]; then
        test -n "$authorized" && test -f "$authorized/$transfer_manifest"
        ln -s "$authorized/$transfer_manifest" "$transfer_manifest"
    fi
    for role in fit development test; do
        "$py" "$code/matched.py" "$role" --cache "$v5" --out "$cache" --workers "$workers"
    done
    "$py" "$code/heads_v6.py" --cache "$cache"
    "$py" "$code/learned.py" viewed --cache "$v5" --device "$device" --out "$cache/v5_learned.npz"
    for role in broad_fit broad_dev native_dev; do
        "$py" "$code/fresh.py" "$role" --cache "$cache" --broad "$broad" --workers "$workers"
    done
    "$py" "$code/verify_refit.py" --cache "$cache" --broad "$broad"
    "$py" "$code/fresh.py" calibration --cache "$cache" --broad "$broad" --workers "$workers"
    "$py" "$code/seal.py" calibrate --cache "$cache" --broad "$broad"
    for role in test transfer; do
        "$py" "$code/fresh.py" "$role" --cache "$cache" --broad "$broad" --workers "$workers"
        "$py" "$code/seal.py" score --role "$role" --cache "$cache" --broad "$broad"
    done
fi

"$py" "$code/evaluate_v6.py" viewed --cache "$cache"
"$py" "$code/evaluate_v6.py" test
"$py" "$code/evaluate_v6.py" transfer
"$py" "$code/secondary.py"
if [[ -f V6_NUMERIC_SHA256SUMS ]]; then sha256sum -c --quiet V6_NUMERIC_SHA256SUMS; fi
if [[ "$numeric_only" == 1 ]]; then exit 0; fi
"$py" "$code/paper_artifacts.py"
"$py" "$code/plot_v6.py"
(
    cd "$paper"
    mkdir -p build
    latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build main.tex supplement.tex
    cp build/main.pdf BeyondTheBlob_CVPR2027_V6.pdf
    cp build/supplement.pdf BeyondTheBlob_CVPR2027_V6_Supplement.pdf
)
if [[ -f V6_PAPER_SHA256SUMS ]]; then sha256sum -c --quiet V6_PAPER_SHA256SUMS; fi
