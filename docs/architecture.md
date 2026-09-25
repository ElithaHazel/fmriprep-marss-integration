# MARSS–fMRIPrep Integration Architecture

## Overview

This project extends the fMRIPrep functional BOLD preprocessing workflow with an optional MARSS preprocessing stage. The integration was developed against fMRIPrep 20.2.3 and implemented as a modular Nipype workflow.

The MARSS stage is designed to operate upstream of fMRIPrep's head-motion correction (HMC) workflow. When MARSS processing is enabled, the BOLD time series is routed through the MARSS workflow before being supplied to downstream BOLD processing.

## Workflow Architecture

```text
BIDS BOLD Input
       |
       v
Initial fMRIPrep BOLD Handling
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

## Configuration

Two workflow configuration parameters support the integration:

- `use_marss` — enables or disables MARSS preprocessing.
- `marss_mb` — specifies the multiband acceleration factor required by MARSS.

MARSS processing is disabled by default.

## Command-Line Interface

The integration adds two command-line options to fMRIPrep:

```text
--use-marss
--marss-mb <MB>
```

When `--use-marss` is enabled, a multiband factor must also be supplied.

Example:

```bash
fmriprep <BIDS_DIR> <OUTPUT_DIR> participant \
    --participant-label 01 \
    --use-marss \
    --marss-mb 6
```

This allows MARSS preprocessing to remain optional while exposing acquisition-specific multiband information through the fMRIPrep command-line interface.

## MARSS Nipype Workflow

The MARSS integration is encapsulated in a dedicated Nipype workflow.

The workflow contains three primary components:

1. `inputnode` — receives the input BOLD time series.
2. `marss_node` — wraps the MARSS Python entry point using Nipype's `Function` interface.
3. `outputnode` — exposes the resulting BOLD image as `marss_bold_file`.

The MARSS entry point used by the wrapper follows the interface:

```python
MARSS_main(timeseriesFile, MB, workingDir, *args)
```

The multiband factor supplied through the fMRIPrep configuration is assigned to the MARSS processing node.

## Integration into the BOLD Pipeline

When MARSS is enabled, the workflow is instantiated as:

```text
bold_marss_wf
```

The BOLD data are routed from the fMRIPrep BOLD buffer into the MARSS workflow. The MARSS workflow output is subsequently supplied to downstream BOLD processing, including the input to the head-motion-correction workflow.

Conceptually:

```text
boldbuffer
    |
    v
bold_marss_wf
    |
    +--> marss_bold_file
              |
              v
          bold_hmc_wf
```

When MARSS is disabled, the standard fMRIPrep processing path is retained.

## Development Architecture

The integration required modifications across four layers of fMRIPrep:

### 1. Workflow Configuration

Configuration variables were introduced to represent whether MARSS should run and to store the acquisition multiband factor.

### 2. Command-Line Interface

Command-line arguments were added so MARSS could be enabled explicitly and supplied with the required multiband factor.

Validation was added to prevent MARSS execution without an MB value.

### 3. Dedicated MARSS Workflow

A modular Nipype workflow was implemented to isolate MARSS execution from the surrounding fMRIPrep workflow.

This design allows the MARSS stage to expose a standard BOLD-file interface to downstream nodes.

### 4. BOLD Workflow Routing

The fMRIPrep BOLD workflow was extended so that, when MARSS is enabled, the BOLD time series is routed through `bold_marss_wf` before downstream processing and head-motion correction.

## HPC Execution

Development and validation were performed in an HPC environment using fMRIPrep 20.2.3.

The workflow was executed through SLURM with the MARSS integration enabled using:

```text
--use-marss
--marss-mb 6
```

The repository provides a sanitized example SLURM script under:

```text
scripts/run_marss.slurm
```

Environment-specific paths and research-system configuration are intentionally excluded from the public execution example.

## Validation Boundary

The project distinguishes between two forms of validation:

### Workflow Integration Validation

This asks whether the custom MARSS workflow was correctly inserted into fMRIPrep and whether its output could propagate through downstream processing.

The preserved development run demonstrated that:

- the custom `bold_marss_wf.marss_node` was instantiated;
- the MARSS node executed;
- the expected `marss_bold.nii.gz` interface was produced;
- downstream fMRIPrep nodes consumed that output;
- the complete fMRIPrep workflow reached successful completion.

### MARSS Algorithm Validation

This asks whether the external MARSS algorithm itself performed artifact regression on the BOLD data.

In the preserved validation run, the external MARSS package was unavailable to the batch-job Python environment. The development wrapper therefore entered its passthrough behavior and copied the input BOLD image to the expected output interface.

Consequently, the preserved run validates the workflow integration and downstream routing, but it does **not** establish successful MARSS regression or scientific efficacy.

These two validation questions are intentionally kept separate throughout this repository.

## Hardened Reference Implementation

The implementation under `src/` is a cleaned reference version derived from the development work.

The historical development wrapper included passthrough behavior to facilitate pipeline integration testing when MARSS was unavailable. The cleaned implementation instead fails explicitly when MARSS cannot be imported or does not produce an output image.

This prevents an unprocessed BOLD image from being interpreted as MARSS-processed data and provides safer behavior for future reproducibility testing.

## Scope

This repository focuses on the engineering required to integrate MARSS into the fMRIPrep BOLD workflow.

It does not claim that the preserved validation run demonstrates improved image quality, reduced artifacts, improved motion correction, or downstream statistical improvements. Those questions require successful MARSS execution followed by dedicated quantitative and scientific validation.