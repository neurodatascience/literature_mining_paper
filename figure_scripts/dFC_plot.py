from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from labelrepo import database, read_json, repo

## citations and year of publication
info_dict = {
    "Co-Activation Patterns": {
        "year": 2013,
        "citations": 505,
    },
    "Clustering": {
        "year": 2014,
        "citations": 2047,
    },
    "Hidden Markov Model": {
        "year": 2017,
        "citations": 398,
    },
    "Sliding Window": {
        "year": 2010,
        "citations": 494,
    },
    "Time-Frequency": {
        "year": 2010,
        "citations": 1557,
    },
    "Window-less": {
        "year": 2018,
        "citations": 27,
    },
}
## extract labels
labels_file = (
    repo.repo_root()
    / "projects"
    / "dynamic_functional_connectivity"
    / "labels"
    / "labels.json"
)
labels = read_json(labels_file)
application_labels = []
method_labels = []
for label in labels:
    name = label['name']
    if 'application' in name:
        application_labels.append(name)
    else:
        method_labels.append(name)

## extract annotations
connection = database.get_database_connection()
df = pd.read_sql(
    """
    SELECT label_name
    FROM detailed_annotation
    WHERE project_name = "dynamic_functional_connectivity"
    """,
    connection,
)

for i, row in df.iterrows():
    label = row["label_name"]
    if label in method_labels:
        df.loc[i, "method"] = label
    if label in application_labels:
        df.loc[i, "application"] = label  

## count 
method_counts = df["method"].value_counts().reindex(method_labels, fill_value=0).sort_values(ascending=True).to_frame()
method_counts.reset_index(inplace=True)
YLABEL = "Count of annotated articles\nusing this method"
XLABEL = "Count of citations for this method"
method_counts.columns = ['dFC method', YLABEL]
# add year and citations
for method in info_dict:
    method_counts.loc[method_counts['dFC method']==method, 'year'] = info_dict[method]['year']
    method_counts.loc[method_counts['dFC method']==method, XLABEL] = info_dict[method]['citations']
# remove rows with NaN
method_counts.dropna(inplace=True)
# convert to int
method_counts = method_counts.astype({XLABEL:"int","year":"int"})

## visualize
fig, axs = plt.subplots(1, 1, figsize=(6, 4),)

# organize the scatter plot
method_counts.plot.scatter(x=XLABEL, y=YLABEL, s = 40, c='purple', ax=axs)
# add annotations
for i, row in method_counts.iterrows():
    axs.annotate(row['dFC method'] + ' (' + str(row['year']) + ')', (row[XLABEL]+15, row[YLABEL] + 0.5), fontsize=10, rotation=45)

# remove top and right spines
axs.spines['top'].set_visible(False)
axs.spines['right'].set_visible(False)

# add more ticks
axs.yaxis.set_ticks(np.arange(0, 44, 5))
axs.xaxis.set_ticks(np.arange(0, 3000, 500))

fig.tight_layout()
fig_path = (
    Path(__file__).resolve().parents[1]
    / "figures"
    / "dfc_plot_simplified.pdf"
    )
fig.savefig(fig_path, bbox_inches="tight")
