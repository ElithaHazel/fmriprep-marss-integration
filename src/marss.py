"""MARSS preprocessing workflow for integration with fMRIPrep BOLD processing.

This module wraps MARSS as a Nipype workflow so that MARSS preprocessing can
be inserted upstream of fMRIPrep head-motion correction.
"""


from nipype.interfaces.utility import Function, IdentityInterface
from nipype.pipeline.engine import Node, Workflow


def marss_apply(in_file, MB):
    """Run MARSS preprocessing on a 4D BOLD time series.

    Parameters
    ----------
    in_file : str
        Path to the input 4D BOLD NIfTI image.
    MB : int
        Multiband acceleration factor for the acquisition.

    Returns
    -------
    str
        Absolute path to the MARSS-processed BOLD image.

    Notes
    -----
    Unlike the development implementation, this version fails explicitly if
    MARSS cannot be imported or does not produce a NIfTI output. This prevents
    an unprocessed BOLD image from being mistaken for MARSS-processed data.
    """
    import os
    import shutil

    try:
        from MARSS.MARSS import MARSS_main
    except ImportError as exc:
        raise RuntimeError(
            "MARSS could not be imported. Ensure the MARSS Python package is "
            "available in the execution environment."
        ) from exc

    out_dir = os.path.abspath("marss_output")
    os.makedirs(out_dir, exist_ok=True)

    final_output = os.path.join(out_dir, "marss_bold.nii.gz")

    MARSS_main(in_file, MB, out_dir)

    produced = [
        filename
        for filename in os.listdir(out_dir)
        if filename.endswith((".nii", ".nii.gz"))
        and filename != "marss_bold.nii.gz"
    ]

    if not produced:
        # MARSS may already have produced the standardized filename.
        if os.path.exists(final_output):
            return final_output

        raise RuntimeError(
            "MARSS completed without producing a NIfTI output."
        )

    produced_path = os.path.join(out_dir, produced[0])

    if os.path.abspath(produced_path) != os.path.abspath(final_output):
        shutil.move(produced_path, final_output)

    return final_output


def init_marss_wf(MB, name="marss_wf"):
    """Create the Nipype workflow used to execute MARSS.

    The workflow exposes a BOLD input and returns the MARSS-processed BOLD
    image for connection to downstream fMRIPrep nodes.
    """
    if MB is None or int(MB) <= 0:
        raise ValueError("MB must be a positive integer.")

    workflow = Workflow(name=name)

    inputnode = Node(
        IdentityInterface(fields=["bold_file"]),
        name="inputnode",
    )

    marss_node = Node(
        Function(
            input_names=["in_file", "MB"],
            output_names=["out_file"],
            function=marss_apply,
        ),
        name="marss_node",
    )
    marss_node.inputs.MB = int(MB)

    outputnode = Node(
        IdentityInterface(fields=["marss_bold_file"]),
        name="outputnode",
    )

    workflow.connect(
        [
            (inputnode, marss_node, [("bold_file", "in_file")]),
            (marss_node, outputnode, [("out_file", "marss_bold_file")]),
        ]
    )

    return workflow
