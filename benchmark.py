import os
import json
import matplotlib.pyplot as plt



results = [
    {
         "folder": "./benchmark/ICC_16_5_0_10000_100_1686642144",
         "label": "ICC n=16 f=5",
         "N": 16,
    },
    {
         "folder": "./benchmark/FICC_16_5_0_10000_100_1686642571",
         "label": "FICC n=16 f=5 p=0",
         "N": 16,
    },
    {
         "folder": "./benchmark/FICC_16_3_3_10000_100_1686643003",
         "label": "FICC n=16 f=3 p=3",
         "N": 16,
    },
]

results7 = [
    {
         "folder": "./benchmark/ICC_7_2_0_5000_100_1686521311",
         "label": "ICC n=7 f=2 p=0",
         "N": 7,
    },
    {
         "folder": "./benchmark/FICC_7_2_0_5000_100_1686520957",
         "label": "FICC n=7 f=2 p=0",
         "N": 7,
    },
    {
         "folder": "./benchmark/FICC_7_1_1_3000_100_1686514196",
         "label": "FICC n=7 f=1 p=1",
         "N": 7,
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
            n_replica = int(filename[18:-5])

            location_latencies = [value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())]#[:100]
            location_latencies = location_latencies[((1-n_replica) % res["N"])::res["N"]]
            box_plots.append(location_latencies)
            labels.append(filename[18:-5])
    
    min = len(box_plots[0])
    for node in box_plots:
        if len(node) < min:
            min = len(node)
    
    box_plots = [node[:min] for node in box_plots]
        
    # create the boxplot
    plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
    plt.ylabel(res['folder'])
    plt.show()


# Overview Plot
box_plots = []
labels = []

for res in results:
    subnet_latencies = []
    for filename in os.listdir(res["folder"]):
        if filename.endswith(".json"):
            with open(os.path.join(res["folder"], filename)) as f:
                data = json.load(f)
            # extract the latency values from the data
            n_replica = int(filename[18:-5])

            location_latencies = [value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())]#[:100]
            location_latencies = location_latencies[((1-n_replica) % res["N"])::res["N"]]
            subnet_latencies.extend(location_latencies)
    
    box_plots.append(subnet_latencies)
    labels.append(res["label"])

min = len(box_plots[0])
for node in box_plots:
    if len(node) < min:
        min = len(node)
    
box_plots = [node[:min] for node in box_plots]
    
# create the boxplot
plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
plt.ylabel('Latency (seconds)')
plt.show()



