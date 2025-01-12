import requests
import subprocess
import time
import os
import json
import matplotlib.pyplot as plt
import matplotlib

folder = "paper/experiments/horsemen/" 
folder = "paper/experiments/6us+6asia+4/" 
folder = "paper/experiments/7us+6eu+3as/" 
name = "16_5_0"

N = 16
figsize = (5,4)
yaxis = [0,1.8]


def getBenchmarks(n_replica):
    with open(f'./{folder}{name}/benchmark_results_{n_replica:02d}.json', 'r') as f:
        return json.loads(f.read())

def fillMissingElements(iterations, metrics, default_element):
    filled_iterations = []
    filled_metrics = []
    for i in range(min(iterations), max(iterations) + 1):
        if i in iterations:
            index = iterations.index(i)
            filled_iterations.append(iterations[index])
            filled_metrics.append(metrics[index])
        else:
            filled_iterations.append(i)
            filled_metrics.append(default_element)
    return filled_iterations, filled_metrics

def printMetrics(
    average_latency,
    total_fp_finalizations,
    total_ic_finalizations,
    total_dk_finalizations,
    total_non_finalizations,
):
    print("The average time for block finalization is:", average_latency)
    print("The number of iterations in which the block is:")
    print("- FP finalized:", total_fp_finalizations)
    print("- IC finalized:", total_ic_finalizations)
    print("- DK finalized:", total_dk_finalizations)
    print("- not explicitly finalized:", total_non_finalizations)

def processResults(latencies, filled_iterations, filled_finalization_types):
    average_latency = None
    if len(latencies) != 0:
        average_latency = sum(latencies) / len(latencies)
    total_fp_finalizations = filled_finalization_types.count("FP")
    total_ic_finalizations = filled_finalization_types.count("IC")
    total_dk_finalizations = filled_finalization_types.count("DK")
    total_non_finalizations = filled_finalization_types.count("-")

    return (
        average_latency,
        total_fp_finalizations,
        total_ic_finalizations,
        total_dk_finalizations,
        total_non_finalizations,
    )

def plotLatencies(ax, n_replica, filled_iterations, filled_latencies, filled_finalization_types):
    colors = ['#219ebc', "#ffb703", "#fb8500"]
    color_labels = {
        "#219ebc": "FP-finalized block",
        "#ffb703": "IC-finalized block",
        "#fb8500": "finalization from peer"
    }
    fp_bar = None
    ic_bar = None
    for j, type in enumerate(filled_finalization_types):
        if type == "FP":
            fp_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[0], label=color_labels[colors[0]])
        elif type == "IC":
            ic_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[1], label=color_labels[colors[1]])
        elif type == "DK":
            ic_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[2], label=color_labels[colors[2]])
    handles = [fp_bar, ic_bar]
    labels = ["FP-finalized block", "IC-finalized block", "finalization from peer"]
    ax.legend(handles, labels, loc="upper right")

    # Highlight every Nth bar
    for i in range((1 - n_replica) % N, len(filled_iterations), N):
        ax.axvline(filled_iterations[i], color="red", linestyle="--")

def getResults():
    plt.plot() 
    iterations = [int(iteration) for iteration in benchmark["finalization_times"].keys()]
    latencies = [metrics["latency"]["secs"]+metrics["latency"]["nanos"]*1e-9 for metrics in benchmark["finalization_times"].values()]
    filled_iterations, filled_latencies = fillMissingElements(iterations, latencies, 0)
    finalization_types = [metrics["fp_finalization"] for metrics in benchmark["finalization_times"].values()]
    _, filled_finalization_types = fillMissingElements(iterations, finalization_types, "-")

    (
        average_latency,
        total_fp_finalizations,
        total_ic_finalizations,
        total_dk_finalizations,
        total_non_finalizations,
    ) = processResults(latencies, filled_iterations, filled_finalization_types)

    ax = plt.gca()
    ax.set_xlabel("Round")
    ax.set_ylabel("Latency [s]")
    plotLatencies(plt.gca(), 1, filled_iterations, filled_latencies, filled_finalization_types)

    printMetrics(
        average_latency,
        total_fp_finalizations,
        total_ic_finalizations,
        total_dk_finalizations,
        total_non_finalizations,
    )
    plt.show()


def plotAllProposers():
    for i in range(1,N+1):
        benchmark = getBenchmarks(i)
        plt.figure(figsize=(26,13), dpi=300)
        plt.plot() 
        iterations = [int(iteration) for iteration in benchmark["finalization_times"].keys()]
        latencies = [metrics["latency"]["secs"]+metrics["latency"]["nanos"]*1e-9 for metrics in benchmark["finalization_times"].values()]
        filled_iterations, filled_latencies = fillMissingElements(iterations, latencies, 0)
        finalization_types = [metrics["fp_finalization"] for metrics in benchmark["finalization_times"].values()]
        _, filled_finalization_types = fillMissingElements(iterations, finalization_types, "-")

        (
            average_latency,
            total_fp_finalizations,
            total_ic_finalizations,
            total_dk_finalizations,
            total_non_finalizations,
        ) = processResults(latencies, filled_iterations, filled_finalization_types)

        ax = plt.gca()
        ax.set_xlabel("Round")
        ax.set_ylabel("Latency [s]")
        plotLatencies(ax, i, filled_iterations, filled_latencies, filled_finalization_types)

        printMetrics(
            average_latency,
            total_fp_finalizations,
            total_ic_finalizations, 
            total_dk_finalizations,
            total_non_finalizations,
        )
        plt.savefig(f'{folder}{name}/replica{i}.png')
        plt.close()
        #plt.show()

def plotAll():
    for i in range(1,N+1):
        benchmark = getBenchmarks(i)
        plt.figure(figsize=figsize, dpi=300)
        plt.plot() 
        iterations = [int(iteration) for iteration in benchmark["finalization_times"].keys()][:-1]
        latencies = [metrics["latency"]["secs"]+metrics["latency"]["nanos"]*1e-9 for metrics in benchmark["finalization_times"].values()][1:]
        filled_iterations, filled_latencies = fillMissingElements(iterations, latencies, 0)
        finalization_types = [metrics["fp_finalization"] for metrics in benchmark["finalization_times"].values()]
        _, filled_finalization_types = fillMissingElements(iterations, finalization_types, "-")

        (
            average_latency,
            total_fp_finalizations,
            total_ic_finalizations,
            total_dk_finalizations,
            total_non_finalizations,
        ) = processResults(latencies, filled_iterations, filled_finalization_types)

        ax = plt.gca()
        ax.set_xlabel("Round")
        ax.set_ylabel("Latency [s]")
        
        plotLatencies(ax, i, filled_iterations, filled_latencies, filled_finalization_types)

        printMetrics(
            average_latency,
            total_fp_finalizations,
            total_ic_finalizations, 
            total_dk_finalizations,
            total_non_finalizations,
        )
        plt.savefig(f'{folder}{name}/replica{i}.png')
        plt.close()

def plotAgregate():
    plt.figure(figsize=figsize, dpi=300)
    plt.plot() 
    ax = plt.gca()
    ax.set_xlabel("Round")
    ax.set_ylabel("Latency [s]")

    colors = ['#219ebc', "#ffb703", "#fb8500"]
    color_labels = {
        "#219ebc": "FP-finalized block",
        "#ffb703": "IC-finalized block",
        "#fb8500": "finalization from peer"
    }

    #plt.show()
    fp_bar = None
    ic_bar = None
    dk_bar = None
    
    for i in range(1,N+1):
        benchmark = getBenchmarks(i)
        iterations = [int(iteration) for iteration in benchmark["finalization_times"].keys()][:-2]
        latencies = [metrics["latency"]["secs"]+metrics["latency"]["nanos"]*1e-9 for metrics in benchmark["finalization_times"].values()][2:]
        filled_iterations, filled_latencies = fillMissingElements(iterations, latencies, 0)
        finalization_types = [metrics["fp_finalization"] for metrics in benchmark["finalization_times"].values()]
        _, filled_finalization_types = fillMissingElements(iterations, finalization_types, "-")

        for j, type in enumerate(filled_finalization_types):
            if (1-i) % N != j % N:
                continue
            elif type == "FP":
                fp_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[0], label=color_labels[colors[0]])
            elif type == "IC":
                ic_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[1], label=color_labels[colors[1]])
            elif type == "DK":
                dk_bar = ax.bar(filled_iterations[j], filled_latencies[j], width=1, color=colors[2], label=color_labels[colors[2]])
    
    handles = [fp_bar, ic_bar, dk_bar]
    labels = ["FP-finalized block", "IC-finalized block", "Received finalization from peer"]
    ax.legend(handles, labels, loc="upper right")
    ax.set_ylim(yaxis)
    plt.savefig(f'{folder}{name}/prop_latencies_{name}.png')
    plt.close()

#benchmark = getBenchmarks(1)

#getResults()

plotAll()
#plotAllProposers()

plotAgregate()