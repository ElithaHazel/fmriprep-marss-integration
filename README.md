# MARSS Integration into fMRIPrep

An engineering extension of the fMRIPrep functional BOLD preprocessing workflow that introduces an optional MARSS preprocessing stage upstream of head-motion correction.

This repository documents the architecture, implementation, HPC validation, debugging process, and reproducibility work performed while integrating MARSS into **fMRIPrep 20.2.3** using **Python, Nipype, BIDS, SLURM, and neuroimaging workflow tools**.

> **Validation status:** The preserved end-to-end run validates workflow integration and downstream propagation through fMRIPrep. In that historical batch run, the external MARSS package was unavailable to the runtime environment, so the development wrapper entered passthrough mode. The preserved run therefore does not constitute algorithm-level validation of MARSS regression.

---

## Project Overview

fMRIPrep provides standardized preprocessing workflows for functional MRI data using Nipype-based workflow composition.

This project extends the functional BOLD workflow with an optional MARSS preprocessing stage designed to execute before head-motion correction (HMC).

The integration adds:

- command-line controls for enabling MARSS;
- multiband-factor configuration and validation;
- a dedicated Nipype MARSS workflow;
- conditional routing of BOLD data through MARSS;
- propagation of the MARSS output into downstream fMRIPrep processing;
- SLURM-based HPC execution support; and
- validation and reproducibility documentation.

The implementation was developed and tested against **fMRIPrep 20.2.3**.

---

## Architecture

At a high level, the MARSS-enabled processing path is:

```text
BIDS BOLD Input
       |
       v
Initial fMRIPrep BOLD Processing
       |
       v
   BOLD Buffer
       |
       v
+-------------------------+
| MARSS Nipype Workflow   |
|                         |
| inputnode               |
|     |                   |
|     v                   |
| marss_node              |
|     |                   |
|     v                   |
| outputnode              |
+------------+------------+
             |
             | marss_bold_file
             v
    Head-Motion Correction
           (HMC)
             |
             v
     Remaining fMRIPrep
       BOLD Processing
```

The MARSS workflow is implemented as a modular Nipype workflow so that its output can be exposed through a standard BOLD-file interface to downstream nodes.

A more detailed architecture description is available in [`docs/architecture.md`](docs/architecture.md).

---

## Command-Line Interface

Two command-line options were introduced:

```text
--use-marss
--marss-mb <MB>
```

`--use-marss` enables the optional MARSS preprocessing pathway.

`--marss-mb` supplies the acquisition multiband factor required by the MARSS interface.

Example:

```bash
fmriprep <BIDS_DIR> <OUTPUT_DIR> participant \
    --participant-label 01 \
    --use-marss \
    --marss-mb 6
```

The CLI validates that a multiband factor is supplied when MARSS processing is requested.

---

## fMRIPrep Integration

The integration touches four parts of the fMRIPrep codebase.

### 1. Workflow Configuration

Two workflow-level configuration variables were introduced:

```python
use_marss = False
marss_mb = None
```

MARSS therefore remains optional rather than altering the default preprocessing path intentionally.

### 2. CLI Configuration

The parser was extended with:

```text
--use-marss
--marss-mb
```

along with validation requiring the multiband factor when MARSS is enabled.

### 3. MARSS Nipype Workflow

A dedicated workflow module introduces:

```text
inputnode
    |
    v
marss_node
    |
    v
outputnode
```

The external MARSS entry point follows the interface:

```python
MARSS_main(timeseriesFile, MB, workingDir, *args)
```

The wrapper maps the fMRIPrep BOLD input and configured multiband factor onto this interface.

### 4. BOLD Workflow Routing

When MARSS is enabled, a workflow named:

```text
bold_marss_wf
```

is instantiated and inserted into the BOLD preprocessing graph.

The MARSS output interface is then supplied to downstream processing, including the head-motion-correction workflow.

---

## Repository Structure

```text
fmriprep-marss-integration/
├── README.md
├── .gitignore
│
├── src/
│   └── marss.py
│
├── patches/
│   ├── config.patch
│   ├── cli-parser.patch
│   ├── bold-workflow.patch
│   └── marss-workflow.patch
│
├── scripts/
│   └── run_marss.slurm
│
├── docs/
│   ├── architecture.md
│   └── validation.md
│
└── results/
    └── validation-summary.md
```

Local baseline and patch-validation directories are excluded through `.gitignore`.

---

## Historical Patches

The `patches/` directory records the integration relative to the official **fMRIPrep 20.2.3** distribution.

The patches cover:

| Patch | Purpose |
|---|---|
| `config.patch` | Adds MARSS workflow configuration |
| `cli-parser.patch` | Adds CLI controls and MB validation |
| `bold-workflow.patch` | Inserts MARSS into the BOLD workflow |
| `marss-workflow.patch` | Adds the new MARSS Nipype workflow module |

The patches were generated by comparing the development environment against a clean fMRIPrep 20.2.3 distribution.

They were subsequently tested using `patch --dry-run` against an untouched 20.2.3 baseline. All four patches applied successfully during the dry-run validation.

These patches preserve the historical development implementation and should therefore be interpreted separately from the hardened reference implementation under `src/`.

---

## Development and Debugging

### Initial Workflow-Wiring Failure

During an early integration test, the custom MARSS node was created and received the multiband parameter, but the BOLD input was undefined:

```text
MB = 6
in_file = <undefined>
```

The resulting exception indicated that `in_file` had not been connected correctly.

This identified a workflow-wiring problem rather than a failure of the MARSS algorithm itself.

The BOLD-to-MARSS connection was subsequently revised.

### End-to-End Integration Run

A later SLURM validation run successfully instantiated and executed:

```text
bold_marss_wf.marss_node
```

The custom workflow produced the expected output interface:

```text
marss_bold.nii.gz
```

and downstream fMRIPrep processing consumed this path.

The complete pipeline subsequently reached:

```text
fMRIPrep finished successfully!
```

This established that the MARSS workflow interface could be inserted into the active BOLD processing graph and propagate through downstream fMRIPrep processing in the tested MARSS-enabled configuration.

---

## Important Validation Boundary

Successful workflow execution does not by itself demonstrate successful MARSS regression.

During the preserved end-to-end run, the batch runtime reported:

```text
No module named 'MARSS'
```

The historical development wrapper contained a passthrough fallback for integration testing. When MARSS could not be imported, the input BOLD image was copied to the expected output interface.

Checksum comparison subsequently showed that the examined development outputs were byte-for-byte identical to the original BOLD input.

Therefore:

### Demonstrated

- MARSS configuration integration
- MARSS CLI integration
- multiband-factor handling
- dedicated Nipype workflow construction
- correction of the initial BOLD-input wiring problem
- execution of the custom MARSS node
- propagation of its output interface downstream
- downstream motion-correction consumption of the MARSS workflow output
- successful completion of the surrounding fMRIPrep workflow

### Not Demonstrated by the Preserved Run

- successful MARSS regression
- MARSS-based artifact reduction
- improved image quality
- improved motion correction
- improved downstream statistical performance

Detailed evidence and interpretation are documented in [`docs/validation.md`](docs/validation.md).

A concise result summary is available in [`results/validation-summary.md`](results/validation-summary.md).

---

## Reproducibility Follow-Up

The Python environment and MARSS interface were revisited during later reproducibility work.

The MARSS entry point was successfully inspected with the interface:

```python
MARSS_main(timeseriesFile, MB, workingDir, *args)
```

which is compatible with the wrapper call used by the integration.

The historical batch script also contained:

```bash
export PYTHONNOUSERSITE=1
```

while a later importable MARSS installation was located in a user-level Python site-packages directory. The historical batch script did not explicitly expose the separate MARSS source tree through `PYTHONPATH`.

Together, these observations provide a plausible environment-level explanation for the historical batch import failure.

They do not retroactively establish MARSS execution in the preserved run.

---

## Hardened Reference Implementation

The historical development wrapper intentionally supported passthrough behavior so that workflow connectivity could be tested even when MARSS was unavailable.

That behavior is useful during integration development, but it can make successful MARSS processing ambiguous because an unprocessed BOLD image can appear at the same output interface.

The cleaned implementation under:

```text
src/marss.py
```

therefore follows stricter behavior.

It:

- validates the multiband factor;
- requires the MARSS Python module to be importable;
- invokes the MARSS entry point explicitly;
- standardizes the resulting NIfTI output; and
- raises an error when MARSS cannot execute or does not produce an expected output.

This prevents silent passthrough from being interpreted as successful MARSS processing.

---

## HPC Execution

The integration was developed and evaluated in a SLURM-based HPC environment.

The repository contains a sanitized example submission script:

```text
scripts/run_marss.slurm
```

The example intentionally replaces institution-specific paths with placeholders such as:

```text
<FMRIPREP_ENV>
<PATH_TO_BIDS_DATASET>
<PATH_TO_OUTPUT_DIRECTORY>
<PATH_TO_WORK_DIRECTORY>
<PATH_TO_FREESURFER_LICENSE>
```

This keeps the repository portable and avoids publishing environment-specific filesystem information.

---

## Reproducing the Integration

This repository is intended to reproduce the MARSS–fMRIPrep **workflow
integration** developed against fMRIPrep 20.2.3. Reproducing the historical
integration does not by itself reproduce or validate the scientific behavior
of MARSS.

### Prerequisites

A reproduction environment should provide:

- fMRIPrep 20.2.3;
- a Python environment compatible with that fMRIPrep release;
- Nipype and the neuroimaging dependencies required by fMRIPrep;
- an accessible MARSS Python installation exposing
  `MARSS.MARSS.MARSS_main`;
- a valid BIDS dataset;
- a valid FreeSurfer license; and
- a Linux execution environment, with SLURM if using the provided HPC example.

### Applying the Historical Patches

The files under `patches/` were generated relative to a clean fMRIPrep 20.2.3
distribution. From the root of an unpacked fMRIPrep 20.2.3 source tree, the
integration patches can be checked before application using:

```bash
patch --dry-run -p1 < /path/to/config.patch
patch --dry-run -p1 < /path/to/cli-parser.patch
patch --dry-run -p1 < /path/to/marss-workflow.patch
patch --dry-run -p1 < /path/to/bold-workflow.patch

```

If the dry runs succeed, remove `--dry-run` to apply the patches.

The preserved patches reproduce the historical development implementation,
including its documented limitations. They should not be interpreted as a
production-ready extension of current fMRIPrep releases.

### Verifying MARSS Availability

Before starting fMRIPrep, verify MARSS using the same Python interpreter that
will execute the workflow:

```bash
python -c "from MARSS.MARSS import MARSS_main; print('MARSS import OK')"
```

The example SLURM script under `scripts/` performs this check automatically
and aborts before fMRIPrep execution if MARSS is unavailable.

### Running

After replacing the environment, dataset, output, work-directory, and
FreeSurfer-license placeholders in:

```text
scripts/run_marss.slurm
```

the example can be submitted with:

```bash
sbatch scripts/run_marss.slurm
```

For non-SLURM environments, the equivalent fMRIPrep invocation requires:

```text
--use-marss --marss-mb <MB>
```

where `<MB>` is the multiband acceleration factor for the acquisition.

### Validation Boundary

A successful reproduction should distinguish between:

1. successful construction and execution of the MARSS workflow interface;
2. successful execution of the external MARSS algorithm; and
3. scientific evaluation of the resulting neuroimaging data.

These are separate validation levels. Successful fMRIPrep completion alone
does not establish MARSS algorithm execution or scientific efficacy.

---

## Future Validation

Algorithm-level validation should be performed using a controlled batch environment in which MARSS is explicitly available to the same Python interpreter used by fMRIPrep.

A complete validation should verify:

1. MARSS importability inside the SLURM job;
2. successful execution of `MARSS_main`;
3. generation of a genuinely processed BOLD output;
4. propagation of that output into HMC and downstream processing;
5. differences between processed output and the original BOLD input; and
6. appropriate quantitative neuroimaging quality-control measures.

Scientific claims regarding artifact reduction or downstream improvements should be made only after those analyses.

---

## Technologies

- Python
- Nipype
- fMRIPrep
- BIDS
- FSL
- FreeSurfer
- ANTs
- AFNI
- Linux
- SLURM
- HPC workflow execution
- Functional MRI preprocessing
- Reproducible workflow engineering

---

## Project Scope

This repository focuses on **workflow and software integration**.

It documents how an optional MARSS stage can be incorporated into the fMRIPrep BOLD processing architecture, how the integration was debugged and validated at the workflow level, and how the historical implementation can be reproduced relative to fMRIPrep 20.2.3.

The repository does not claim that the preserved validation run establishes MARSS scientific efficacy.

---

## Acknowledgments

This work was conducted as part of graduate research involving the integration and evaluation of MARSS within an fMRI preprocessing workflow.

fMRIPrep and Nipype are open-source neuroimaging projects maintained by their respective developer communities. MARSS is treated as an external dependency and its algorithmic implementation is not reproduced in this repository.

---

## Attribution and Licensing

This integration was developed against **fMRIPrep 20.2.3**. The files under `patches/` represent modifications relative to that upstream version and may include contextual portions of fMRIPrep source code. Those portions remain subject to the applicable upstream fMRIPrep copyright and license terms.

MARSS is used as an external dependency and is not redistributed by this repository.

For additional provenance and third-party attribution information, see [`NOTICE.md`](NOTICE.md).

This repository is an independent graduate research project and is not an official fMRIPrep, NiPreps, or MARSS distribution.

---

## References

- fMRIPrep documentation and source code
- Nipype workflow framework
- BIDS specification
- MARSS methodology and implementation, where applicable