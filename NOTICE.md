# Attribution and Third-Party Notice

This repository documents an independent research integration of MARSS
(Motion & Artifact Regression in Simultaneous Slices) into the fMRIPrep
functional BOLD preprocessing workflow.

## fMRIPrep

The integration and patch files in this repository were developed against
fMRIPrep 20.2.3.

fMRIPrep is an open-source neuroimaging preprocessing pipeline developed by
the NiPreps community. Version 20.2.3 is distributed under the BSD 3-Clause
License.

The files under `patches/` represent modifications relative to upstream
fMRIPrep 20.2.3 and therefore may contain contextual portions of upstream
fMRIPrep source code. Those portions remain subject to the applicable
fMRIPrep license and copyright.

Upstream project:
https://github.com/nipreps/fmriprep

This repository is an independent research project and is not an official
fMRIPrep or NiPreps distribution.

## MARSS

MARSS is treated as an external dependency by this integration. This
repository does not redistribute the MARSS package itself.

The reference implementation under `src/` provides the workflow integration
interface used to invoke an available MARSS installation.

## Research Scope

The preserved validation evidence demonstrates integration of the MARSS
workflow stage into the fMRIPrep processing graph and propagation of its
output through downstream preprocessing.

In the documented end-to-end validation run, the external MARSS package was
not available in the runtime environment and the historical development
wrapper used its passthrough behavior. Therefore, that run should not be
interpreted as validation of MARSS regression itself or as evidence of
improved neuroimaging outcomes.