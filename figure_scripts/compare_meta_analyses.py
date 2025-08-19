from pathlib import Path

import matplotlib
from matplotlib import pyplot as plt
from matplotlib import gridspec
from matplotlib import colorbar
from matplotlib import cm
from matplotlib import colors
from nilearn import plotting, datasets, image

THRESHOLD = 3.1
bg = image.crop_img(datasets.load_mni152_template())
all_models = {
    "pubget_neurosynth": "pubget\n--fit_neurosynth",
    "neurosynth_website": "neurosynth.org",
    "pubget_neuroquery": "pubget\n--fit_neuroquery",
    "neuroquery_website": "neuroquery.org",
}

all_terms = {
    "face": (-18,),
    "prosopagnosia": (-18,),
    "reading": (-14, 12),
    "dyslexia": (-14, 12),
}


def add_colorbar(
    vmin,
    vmax,
    threshold,
    ax,
    cmap="magma",
    margin=None,
    with_label=True,
):
    if margin is not None:
        grid = gridspec.GridSpecFromSubplotSpec(
            3,
            2,
            ax,
            height_ratios=[margin, 1.0, margin],
            width_ratios=[1.0, 2.0],
        )
        ax = ax.figure.add_subplot(grid[1, 0])
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)
    # adapted from nilearn
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    our_cmap = matplotlib.colormaps[cmap]
    cmaplist = [our_cmap(i) for i in range(our_cmap.N)]
    transparent_start = int(norm(-threshold, clip=True) * (our_cmap.N - 1))
    transparent_stop = int(norm(threshold, clip=True) * (our_cmap.N - 1))
    for i in range(transparent_start, transparent_stop):
        cmaplist[i] = [0.5, 0.5, 0.5, 0.0]
    our_cmap = colors.LinearSegmentedColormap.from_list(
        "Custom cmap", cmaplist, our_cmap.N
    )
    cbar = colorbar.ColorbarBase(
        ax,
        ticks=[vmin, threshold, vmax],
        norm=norm,
        orientation="vertical",
        cmap=our_cmap,
        spacing="proportional",
        format="%.2g",
    )
    cbar.ax.set_facecolor("gray")
    if with_label:
        cbar.ax.set_xlabel("Z score")


def init_fig():
    widths = [1.05] + [len(coord) for coord in all_terms.values()] + [0.5]
    heights = [0.8] + [3.0] * len(all_models)
    figwidth, figheight = 12, 8
    fig, axes = plt.subplots(
        len(all_models) + 1,
        len(all_terms) + 2,
        figsize=(figwidth, figheight),
        gridspec_kw={
            "width_ratios": widths,
            "height_ratios": heights,
            "hspace": 0.02,
            "wspace": 0.12,
        },
    )
    add_titles(axes)
    return fig, axes



def add_titles(axes):
    for i, term in enumerate(all_terms):
        ax = axes[0, i + 1]
        term = {"prosopagnosia": "proso-\npagnosia"}.get(term, term)
        ax.text(
            0.5,
            0.0,
            term.capitalize(),
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            fontsize=14,
        )
    for i, model in enumerate(all_models.values()):
        ax = axes[i + 1, 0]
        ax.text(
            0.0,
            0.5,
            model,
            va="center",
            ha="left",
            transform=ax.transAxes,
            fontsize=12,
        )


def hide_text_bboxes(display):
    for display_ax in display.axes.values():
        for child in display_ax.ax.get_children():
            if isinstance(child, matplotlib.text.Text):
                child.set_bbox(None)
                t = child.get_text()
                if t == "L":
                    child.set_x(child.get_position()[0] - 0.07)
                elif t == "R":
                    child.set_x(child.get_position()[0] + 0.07)
                else:
                    child.set_x(child.get_position()[0] - 0.15)
                    child.set_fontsize(child.get_fontsize() * .8)


def plot_map(img_path, z_coord, ax, with_annotations):
    threshold = THRESHOLD
    if not img_path.is_file():
        ax.text(
            0.5,
            0.5,
            "(Not in\nmapped\nvocabulary)",
            va="center",
            ha="center",
            transform=ax.transAxes,
            fontsize=12,
        )
        return
    gs = gridspec.GridSpecFromSubplotSpec(
        1, len(z_coord), ax.get_subplotspec(), wspace=0, hspace=0
    )
    subaxes = gs.subplots()
    if not hasattr(subaxes, "__iter__"):
        subaxes = [subaxes]
    img = image.resample_to_img(
        image.math_img("np.maximum(img, 0)", img=img_path),
        bg,
        interpolation="linear",
    )
    for subax, z in zip(subaxes, z_coord):
        display = plotting.plot_img(
            img,
            bg_img=bg,
            axes=subax,
            display_mode="z",
            cut_coords=[z],
            threshold=threshold,
            vmax=10,
            vmin=0,
            annotate=with_annotations,
            colorbar=False,
            interpolation="nearest",
            black_bg=False,
            cmap="magma",
        )
        hide_text_bboxes(display)


def hide_axes(axes):
    for ax in axes.ravel():
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("none")
        for sp in ax.spines.values():
            sp.set_visible(False)


def make_fig():
    fig, axes = init_fig()
    for row, model in enumerate(all_models):
        if row == 0:
            add_colorbar(
                0, 20, THRESHOLD, axes[row + 1, -1], cmap="magma", margin=0.3
            )
        for col, (term, coord) in enumerate(all_terms.items()):
            print(f"{model}, {term}")
            with_annotations = row == 0
            img_path = (
                Path(__file__)
                .resolve()
                .parent.joinpath("data", "brain_maps", model, f"{term}.nii.gz")
            )
            plot_map(
                img_path,
                coord,
                axes[row + 1, col + 1],
                with_annotations,
            )
    hide_axes(axes)
    return fig


out_dir = (
    Path(__file__)
    .resolve()
    .parents[1]
    .joinpath("figures", "compare_meta_analyses")
)
out_dir.mkdir(exist_ok=True, parents=True)
fig = make_fig()
fig.savefig(out_dir / "all.pdf", bbox_inches="tight")
