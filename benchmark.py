import os
import json
import matplotlib.pyplot as plt

results = [
    {
         "folder": "./benchmark/ICC_16_5_0_3000_300_1686255137",
         "label": "ICC n=16 f=5"
    },
    {
         "folder": "./benchmark/ICC_16_3_0_3000_300_1686256095",
         "label": "ICC n=16 f=3"
    },
    {
        "folder": "./benchmark/FICC_16_5_0_3000_300_1686253483",
        "label": "FICC n=16 f=5 p=0"
    },
    {
        "folder": "./benchmark/FICC_16_3_3_3000_300_1686254076",
        "label": "FICC n=16 f=3 p=3"
    },
]

# By locations

for res in results:
    box_plots = []
    labels = []
    for filename in os.listdir(res["folder"]):
        location_latencies = []
        if filename.endswith(".json"):
            with open(os.path.join(res["folder"], filename)) as f:
                data = json.load(f)
            # extract the latency values from the data
            location_latencies = [value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())[100:200]][:1000]
        box_plots.append(location_latencies)
        labels.append(filename[18:-5])

    # create the boxplot
    plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
    plt.ylabel(res['folder'])
    plt.show()


# OG
box_plots = []
labels = []

for res in results:
    subnet_latencies = []
    for filename in os.listdir(res["folder"]):
        if filename.endswith(".json"):
            with open(os.path.join(res["folder"], filename)) as f:
                data = json.load(f)
            # extract the latency values from the data
            subnet_latencies.extend([value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())[100:200]][:1000])
    box_plots.append(subnet_latencies)
    labels.append(res["label"])

# create the boxplot
plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
plt.ylabel('Latency (seconds)')
plt.show()



