# Validation and Development Record

## Purpose

This document records the development and validation evidence for integrating MARSS preprocessing into the fMRIPrep functional BOLD workflow.

The validation focused primarily on software integration:

- creation and execution of the MARSS Nipype node;
- propagation of BOLD data through the custom workflow;
- placement of the MARSS stage upstream of head-motion correction;
- downstream consumption of the MARSS workflow output; and
- successful continuation of the surrounding fMRIPrep workflow.

The preserved development run did not establish successful execution or scientific efficacy of the MARSS regression algorithm itself. Workflow integration and algorithm validation are therefore reported separately.

---

## Development Environment

The integration was developed against:

- **fMRIPrep:** 20.2.3
- **Python:** 3.9 in the fMRIPrep development environment
- **Workflow engine:** Nipype
- **Execution environment:** SLURM-based HPC cluster
- **Neuroimaging dependencies:** FSL, FreeSurfer, ANTs, AFNI, and related fMRIPrep dependencies

The integration introduced:

- `--use-marss` to enable MARSS preprocessing;
- `--marss-mb` to specify the acquisition multiband factor;
- workflow configuration variables for MARSS;
- a dedicated `bold_marss_wf` Nipype workflow; and
- conditional routing of the MARSS output into downstream BOLD processing.

---

## Development Progression

### Initial Workflow Integration

A dedicated MARSS workflow was implemented around a Nipype `Function` node.

The intended data flow was:

```text
BOLD input
    |
    v
MARSS inputnode
    |
    v
marss_node
    |
    v
MARSS outputnode
    |
    v
Downstream fMRIPrep processing
```

The MARSS node accepted two primary inputs:

```text
in_file
MB
```

where `in_file` represented the BOLD time series and `MB` represented the acquisition multiband factor.

---

## May 16: Workflow-Wiring Failure

An early integration run reached the custom MARSS workflow but failed before MARSS processing could execute.

The preserved crash report showed:

```text
Node:
fmriprep_wf.single_subject_01_wf.func_preproc_task_rest_run_1_wf.bold_marss_wf.marss_node

MB = 6
in_file = <undefined>
```

The resulting exception was:

```text
TypeError: marss_apply() missing 1 required positional argument: 'in_file'
```

### Interpretation

This failure indicated a workflow-connectivity problem rather than a failure of the MARSS algorithm.

The MARSS node existed and had received the multiband parameter, but the BOLD input had not been correctly connected to the node.

Because `in_file` was undefined, MARSS itself did not have an opportunity to process the BOLD time series.

The workflow connection was subsequently revised so that the BOLD data were routed into the MARSS workflow.

---

## May 19: End-to-End Workflow Integration Test

A later SLURM validation run enabled the integration using:

```text
--use-marss
--marss-mb 6
```

The runtime logs showed creation of the custom node:

```text
func_preproc_task_rest_run_1_wf.bold_marss_wf.marss_node
```

and execution through Nipype's `Function` interface.

This demonstrated that the earlier BOLD-to-MARSS connectivity problem had been resolved sufficiently for the custom node to execute.

---

## MARSS Runtime Availability

During the preserved May 19 validation run, the wrapper reported:

```text
[MARSS] Could not import MARSS_main: No module named 'MARSS'
```

When the Nipype node executed, the local import attempt similarly reported that `MARSS_main` could not be imported.

The development wrapper therefore entered its explicit passthrough behavior:

```text
[MARSS] MARSS package not available; passthrough copy.
```

Under this behavior, the input BOLD image was copied to the expected workflow output location as:

```text
marss_bold.nii.gz
```

### Interpretation

The May 19 run therefore validated the workflow interface and routing but did not execute MARSS regression.

The existence of `marss_bold.nii.gz` alone is not evidence that MARSS processing occurred because the development wrapper intentionally generated the same interface during passthrough testing.

---

## Downstream Propagation

The May 19 runtime evidence showed that downstream fMRIPrep processing consumed the output produced by the MARSS workflow.

In particular, the input supplied to downstream motion-correction processing referenced:

```text
bold_marss_wf/marss_node/marss_output/marss_bold.nii.gz
```

The MARSS workflow output was also propagated into subsequent BOLD-processing operations.

This is important because it demonstrates that the custom node was not merely instantiated independently. Its output became part of the active fMRIPrep processing graph.

---

## Full fMRIPrep Completion

The preserved standard output from the May 19 SLURM job ended with:

```text
fMRIPrep finished successfully!
```

Therefore, after the MARSS node executed in passthrough mode, the resulting output interface propagated through the downstream workflow and the complete fMRIPrep execution reached successful completion.

This result validates end-to-end compatibility of the custom workflow interface with the downstream fMRIPrep pipeline for the tested development configuration.

It does not establish successful MARSS regression.

---

## Output Checksum Verification

The BOLD input and MARSS-workflow output from the preserved development runs were compared using MD5 checksums.

The original BOLD image had the checksum:

```text
46ed4f213010f91a424c374215904dcf
```

The corresponding `marss_bold.nii.gz` outputs examined from the development work directories produced the same checksum.

### Interpretation

The matching checksums show that those outputs were byte-for-byte identical to the original BOLD input.

This is consistent with the passthrough behavior recorded in the runtime logs and provides independent confirmation that MARSS regression was not applied to those preserved outputs.

---

## Later Reproducibility Follow-Up

As part of continued reproducibility work, the MARSS installation and Python environment were revisited after the original development period.

Two MARSS source/install locations were identified:

```text
<LAB_LIBRARY>/MARSS/python/src/MARSS/MARSS.py
```

and a user-level Python installation under:

```text
~/.local/lib/python3.9/site-packages/MARSS/MARSS.py
```

Using the Python interpreter associated with the fMRIPrep 20.2.3 development environment, the MARSS entry point was subsequently importable and its interface was inspected.

The observed function signature was:

```python
(timeseriesFile, MB, workingDir, *args)
```

This is compatible with the wrapper call used by the integration:

```python
MARSS_main(in_file, MB, out_dir)
```

---

## Environment Finding

The preserved May SLURM execution script contained:

```bash
export PYTHONNOUSERSITE=1
```

This setting prevents Python from adding the user's site-packages directory to its normal module search path.

During the later reproducibility check, MARSS was importable from the user's Python 3.9 site-packages directory.

In addition, the preserved SLURM script did not explicitly add the lab MARSS source directory to `PYTHONPATH`.

### Interpretation

These observations provide a strong technical explanation for the historical batch-job import failure: the batch configuration excluded the user-site installation, while the separate MARSS source tree was not explicitly exposed through the script's Python module path.

This explanation was identified during later reproducibility investigation and should not be interpreted as evidence that the May batch environment successfully contained MARSS.

---

## Validation Summary

| Validation Question | Result |
|---|---|
| MARSS configuration added to fMRIPrep | Confirmed |
| MARSS CLI controls added | Confirmed |
| Multiband parameter validation added | Confirmed |
| Dedicated Nipype MARSS workflow created | Confirmed |
| BOLD input connected to MARSS node after debugging | Confirmed |
| MARSS node executed in the May 19 workflow | Confirmed |
| MARSS workflow output propagated downstream | Confirmed |
| Downstream motion-correction processing consumed the MARSS workflow output | Confirmed |
| Complete fMRIPrep workflow finished | Confirmed |
| External MARSS algorithm executed in the preserved May 19 run | **Not confirmed; logs show passthrough** |
| Preserved MARSS output differed from original BOLD input | **No; examined outputs were byte-identical** |
| MARSS scientifically reduced artifacts | **Not evaluated** |
| MARSS improved downstream statistical results | **Not evaluated** |

---

## Hardened Repository Implementation

The historical development implementation used passthrough behavior so that workflow integration could continue to be tested when the MARSS package was unavailable.

That behavior is useful during development but creates ambiguity because an unprocessed image can appear at the same output interface expected from successful MARSS processing.

The cleaned implementation under `src/marss.py` therefore changes this behavior.

If MARSS cannot be imported, the reference implementation raises an explicit error.

If MARSS executes without producing an expected NIfTI output, the reference implementation also raises an explicit error.

This change separates successful MARSS execution from integration-only testing and makes future validation results easier to interpret.

---

## Known Historical Implementation Limitation

The preserved patches represent the development implementation used during
the MARSS-enabled integration work and should not be interpreted as a
production-hardened extension of fMRIPrep.

In particular, the historical `bold-workflow.patch` instantiates `marss_wf`
only when MARSS is enabled, while the workflow connection list contains a
reference to `marss_wf`. The MARSS-enabled path was the path exercised during
the documented integration validation; the MARSS-disabled path was not
independently validated in the preserved implementation.

A production-ready implementation should guard MARSS-specific workflow
construction and connections so that disabling MARSS leaves the standard
fMRIPrep BOLD processing graph unchanged.

This limitation does not alter the documented result of the MARSS-enabled
validation run, but it defines an additional requirement for a fully hardened
optional integration.

## Remaining Validation Work

A complete algorithm-level validation would require a new controlled run in an environment where MARSS is explicitly available to the batch-job Python interpreter.

Such validation should verify:

1. successful import of `MARSS_main` within the batch environment;
2. successful execution of MARSS on the intended BOLD input;
3. generation of a MARSS-processed output distinct from passthrough behavior;
4. propagation of that output into head-motion correction and downstream fMRIPrep stages;
5. comparison of MARSS-enabled and standard fMRIPrep outputs using appropriate quantitative quality-control measures.

Only after those steps should claims regarding MARSS artifact reduction or scientific performance be made.

---

## Conclusion

The development work established an optional MARSS preprocessing pathway within the fMRIPrep 20.2.3 BOLD workflow, including configuration, command-line controls, a dedicated Nipype workflow, multiband-factor handling, and downstream routing.

The preserved end-to-end validation run demonstrated that the custom workflow could execute and integrate with downstream fMRIPrep processing through successful pipeline completion.

However, the external MARSS package was unavailable to that historical batch runtime, causing the development wrapper to use its passthrough behavior. Consequently, the preserved run demonstrates successful **workflow integration**, not successful **MARSS regression**.

Later reproducibility investigation identified a plausible environment-level explanation for the import failure and confirmed that the MARSS entry-point interface is compatible with the integration wrapper. Future algorithm-level validation should therefore focus on reproducible MARSS availability within the batch environment and quantitative evaluation of genuinely MARSS-processed outputs.