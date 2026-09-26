# Validation Summary

## Overview

The MARSS–fMRIPrep integration was evaluated primarily as a workflow-engineering task: whether an optional MARSS preprocessing stage could be inserted into the fMRIPrep 20.2.3 BOLD pipeline upstream of head-motion correction and connected successfully to downstream processing.

The preserved development evidence supports successful **workflow integration**, while the preserved end-to-end run does **not** demonstrate execution of the MARSS regression algorithm itself.

## Evidence Matrix

| Validation Question | Preserved Evidence | Observation | Conclusion |
|---|---|---|---|
| Was MARSS configuration integrated? | fMRIPrep configuration and CLI modifications | `use_marss`, `marss_mb`, `--use-marss`, and `--marss-mb` are present | Configuration interface implemented |
| Was a MARSS workflow stage created? | Nipype workflow definition and runtime node hierarchy | `bold_marss_wf.marss_node` was instantiated | Custom workflow stage integrated |
| Was the BOLD input initially connected correctly? | Earlier crash report | `in_file = <undefined>` with `MB = 6` | Initial workflow wiring was incomplete |
| Was the wiring subsequently corrected? | Later Nipype execution evidence | `marss_node` received and executed on the BOLD workflow path | BOLD-to-MARSS connection corrected |
| Did the historical batch environment import MARSS? | May 19 runtime output | `No module named 'MARSS'` | MARSS import failed in that run |
| What happened after the import failure? | Development-wrapper runtime output | Passthrough copy created `marss_bold.nii.gz` | Workflow interface continued without MARSS regression |
| Did downstream processing consume the MARSS-stage output? | Downstream Nipype/FSL execution paths | Motion-correction processing consumed `marss_bold.nii.gz` | MARSS-stage output was propagated downstream |
| Did the surrounding fMRIPrep workflow complete? | May 19 batch stdout | `fMRIPrep finished successfully!` | End-to-end integration path completed |
| Was the preserved output altered by MARSS? | Checksum comparison | Examined `marss_bold.nii.gz` and original BOLD had matching MD5 checksums | Preserved output was consistent with passthrough behavior |
| Was MARSS regression demonstrated in that run? | Import failure plus checksum evidence | External MARSS algorithm did not execute | No |
| Was scientific artifact reduction evaluated? | Preserved validation scope | No algorithm-level image-quality comparison was performed | Not evaluated |

## Development Progression

### Initial Integration Test

An earlier validation attempt reached the custom MARSS node but failed because the BOLD input was undefined:

```text
MB = 6
in_file = <undefined>
```

The resulting error indicated an incomplete workflow connection rather than a MARSS algorithm failure.

### Corrected Integration

After revising the workflow connection, the later validation run successfully instantiated and executed:

```text
bold_marss_wf.marss_node
```

The node produced the expected workflow output interface:

```text
marss_bold.nii.gz
```

and downstream fMRIPrep processing consumed this output.

The overall run subsequently reached:

```text
fMRIPrep finished successfully!
```

## Passthrough Finding

The preserved runtime log also reported:

```text
No module named 'MARSS'
```

Because the development implementation included a passthrough fallback, the input BOLD image was copied to the expected MARSS output interface when the external package could not be imported.

Checksum comparison confirmed that the examined development outputs were byte-for-byte identical to the original BOLD input.

Therefore, the successful pipeline completion demonstrates integration of the MARSS workflow interface into fMRIPrep, but not successful MARSS regression.

## Environment Follow-Up

Later reproducibility investigation confirmed that the MARSS entry point accepts the integration wrapper's expected arguments. Source inspection also showed that MARSS creates a run-specific working directory and writes the corrected BOLD image using a `za` filename prefix.

The observed interface was:

```python
MARSS_main(timeseriesFile, MB, workingDir, *args)
```

The historical SLURM configuration included:

```bash
export PYTHONNOUSERSITE=1
```

while a later MARSS installation was identified in the user's Python site-packages directory. The batch script also did not explicitly expose the separate lab MARSS source directory through `PYTHONPATH`.

These findings provide a plausible environment-level explanation for the historical import failure.

## Interpretation

### Demonstrated

The preserved evidence demonstrates:

- optional MARSS configuration within fMRIPrep;
- command-line and multiband-factor support;
- creation of a modular MARSS Nipype workflow;
- correction of the initial BOLD-input wiring problem;
- execution of the custom MARSS node;
- downstream propagation of its output interface; and
- successful completion of the surrounding fMRIPrep workflow.

### Not Demonstrated

The preserved evidence does not demonstrate:

- successful MARSS regression during the May 19 run;
- artifact reduction attributable to MARSS;
- improved motion correction;
- improved image quality; or
- improved downstream statistical performance.

## Conclusion

The project established and validated the software architecture required to place an optional MARSS preprocessing stage upstream of head-motion correction in the fMRIPrep BOLD workflow.

The preserved validation run confirms end-to-end workflow integration but used passthrough behavior because MARSS was unavailable to the historical batch environment. Algorithm-level and scientific validation therefore remain separate future validation steps.