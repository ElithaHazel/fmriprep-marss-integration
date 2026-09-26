#!/bin/bash
#SBATCH --job-name=fmriprep_marss
#SBATCH --partition=<PARTITION>
#SBATCH --time=2-00:00:00
#SBATCH --cpus-per-task=40
#SBATCH --output=marss_%j.out
#SBATCH --error=marss_%j.err

# -------------------------------------------------------------------------
# Environment configuration
# -------------------------------------------------------------------------

# Activate or expose the Python environment containing fMRIPrep.
export PATH="<FMRIPREP_ENV>/bin:$PATH"

# Path to a valid FreeSurfer license.
export FS_LICENSE="<PATH_TO_FREESURFER_LICENSE>"

# Load neuroimaging dependencies as required by the HPC environment.
# Module names and versions may differ between systems.
module load freesurfer
module load ants
module load afni
module load c3d

# -------------------------------------------------------------------------
# Environment preflight validation
# -------------------------------------------------------------------------

echo "Running MARSS environment preflight check..."

python - <<'PY'
import sys

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version.split()[0]}")

try:
    from MARSS.MARSS import MARSS_main
except ImportError as exc:
    raise SystemExit(
        "ERROR: MARSS is not importable in the batch-job Python environment. "
        f"Aborting before fMRIPrep execution. Details: {exc}"
    )

print("MARSS import: OK")
print(f"MARSS entry point: {MARSS_main.__module__}.{MARSS_main.__name__}")
PY

if [ $? -ne 0 ]; then
    echo "MARSS preflight validation failed."
    exit 1
fi

echo "MARSS environment preflight validation passed."

# -------------------------------------------------------------------------
# Dataset configuration
# -------------------------------------------------------------------------

BIDS_DIR="<PATH_TO_BIDS_DATASET>"
OUTPUT_DIR="<PATH_TO_OUTPUT_DIRECTORY>"
WORK_DIR="<PATH_TO_WORK_DIRECTORY>"

PARTICIPANT_LABEL="01"
MARSS_MB=6

# -------------------------------------------------------------------------
# Run fMRIPrep with MARSS enabled
# -------------------------------------------------------------------------

fmriprep \
    "$BIDS_DIR" \
    "$OUTPUT_DIR" \
    participant \
    --participant-label "$PARTICIPANT_LABEL" \
    -w "$WORK_DIR" \
    --fs-no-reconall \
    --use-marss \
    --marss-mb "$MARSS_MB" \
    --fs-license-file "$FS_LICENSE"
