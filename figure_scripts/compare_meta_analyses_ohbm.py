from pathlib import Path

import matplotlib
from matplotlib import pyplot as plt
from nilearn import plotting, glm, maskers, datasets

masker = maskers.NiftiMasker(datasets.load_mni152_brain_mask()).fit()


def plot_term(term, z_coord, out_dir):
    all_models = {
        "pubget_neurosynth": "pubget neurosynth",
        "neurosynth_website": "neurosynth.org",
    }
    for model, display_name in all_models.items():
        fig, ax = plt.subplots(1, 1, figsize=(2 * len(z_coord) + .5, 2.2))
        # ax.set_title(display_name)
        img = (
            Path(__file__)
            .resolve()
            .parent.joinpath("data", "brain_maps", model, f"{term}.nii.gz")
        )
        if img.is_file():
            # threshold = glm.fdr_threshold(
            #     masker.transform(str(img)).ravel(), 0.01
            # )
            threshold = 3.1
            display = plotting.plot_stat_map(
                str(img),
                axes=ax,
                display_mode="z",
                cut_coords=z_coord,
                threshold=threshold,
                vmax=10,
                symmetric_cbar=True,
            )
            for display_ax in display.axes.values():
                for child in display_ax.ax.get_children():
                    if isinstance(child, matplotlib.text.Text):
                        child.set_bbox(None)
        else:
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)
            ax.text(0.5, 0.5, "?", transform=ax.transAxes, fontsize=20)
        for ext in ("pdf", "png"):
            out_file = out_dir.joinpath(f"{term}_{model}.{ext}")
            fig.savefig(str(out_file), bbox_inches="tight")


out_dir = (
    Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("figures", "compare_meta_analyses_ohbm")
)
out_dir.mkdir(exist_ok=True, parents=True)


for term, z_coord in (
    # ("language", 12),
    # ("aphasia", 12),
    # ("language", -4),
    # ("aphasia", -4),
    ("face", (-18,)),
    ("prosopagnosia", (-18,)),
    ("reading", (-14, 12)),
    ("dyslexia", (-14, 12)),
    # ("word", -14),
    # ("visual_word", -14),
):
    plot_term(term, z_coord, out_dir)
