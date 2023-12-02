import os
import json
import matplotlib.pyplot as plt
import statistics 
import numpy as np

proposer_only = False

outlier = [
    {
         "folder": "./paper/experiments/7us+6eu+3as/16_5",
         "label": "ICC n=16 \n f=5",
         "N": 16,
    },
    {
         "folder": "./paper/experiments/7us+6eu+3as/16_5_0",
         "label": "FICC n=16 \n f=5 p=0",
         "N": 16,
    },
    {
         "folder": "./paper/experiments/7us+6eu+3as/16_3_3",
         "label": "FICC n=16 \n f=3 p=3",
         "N": 16,
    },
]
wan = [
    {
         "folder": "./paper/experiments/6us+6asia+4/16_5",
         "label": "ICC n=16 \n f=5",
         "N": 16,
    },
    {
         "folder": "./paper/experiments/6us+6asia+4/16_5_0",
         "label": "FICC n=16 \n f=5 p=0",
         "N": 16,
    },
    {
         "folder": "./paper/experiments/6us+6asia+4/16_3_3",
         "label": "FICC n=16 \n f=3 p=3",
         "N": 16,
    },
]

horsemen = [
    {
         "folder": "./paper/experiments/horsemen/4_1",
         "label": "ICC n=4 f=1",
         "N": 4,
    },
    {
         "folder": "./paper/experiments/horsemen/4_1_0",
         "label": "FICC n=4 f=1 p=0",
         "N": 4,
    },
]

results = outlier
figsize = (5,4)


# By locations
for res in results:
    box_plots = []
    labels = []
    for filename in np.sort(os.listdir(res["folder"])):
        location_latencies = []
        if filename.endswith(".json"):
            with open(os.path.join(res["folder"], filename)) as f:
                data = json.load(f)
            # extract the latency values from the data
            n_replica = int(filename[18:-5])

            location_latencies = [value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())][1:]
            
            if proposer_only:
                location_latencies = location_latencies[((1-n_replica) % res["N"])::res["N"]]
            else:
                location_latencies = [loc for loc in location_latencies if loc != 0]
            
            print(filename, statistics.mean(location_latencies), statistics.stdev(location_latencies))

            box_plots.append(location_latencies)
            labels.append(filename[18:-5])
    
    min = len(box_plots[0])
    for node in box_plots:
        if len(node) < min:
            min = len(node)
    
    box_plots = [node[:min] for node in box_plots]
        
    # create the boxplot
    plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
    plt.ylabel('Latency (seconds)')
    plt.xlabel('Replica Number')
    plt.ylim(0,1.8)
    plt.savefig(f"{res['label']}_individual.png")
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

            location_latencies = [value["latency"]["secs"] + value["latency"]["nanos"] / 1000000000 for value in list(data['finalization_times'].values())][20:]
            if proposer_only:
                location_latencies = location_latencies[((1-n_replica) % res["N"])::res["N"]]
            else:
                location_latencies = [loc for loc in location_latencies if loc != 0]
            subnet_latencies.extend(location_latencies)
    
    box_plots.append(subnet_latencies)
    labels.append(res["label"])
    print("stats ",filename, statistics.mean(subnet_latencies), statistics.stdev(subnet_latencies))

min = len(box_plots[0])
for node in box_plots:
    if len(node) < min:
        min = len(node)
    
box_plots = [node[:min] for node in box_plots]
    
# create the boxplot
plt.figure(figsize=figsize, dpi=300)
plt.boxplot(box_plots, labels=labels, showfliers=True, flierprops=dict(marker='o', markerfacecolor='gray', markersize=4, linestyle='none', markeredgecolor='gray'))
plt.ylabel('Latency (seconds)')
plt.savefig("boxplot.png")
plt.show()



