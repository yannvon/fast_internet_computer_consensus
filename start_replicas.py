import requests
import subprocess
import time
import os
import json
import matplotlib.pyplot as plt


peers = [
    # California     
    {    
        "number": "16",
        "ip": "54.215.157.199",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "15",
        "ip": "54.219.175.3",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm     
    {    
        "number": "14",
        "ip": "16.170.203.144",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "13",
        "ip": "16.171.0.154",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Canada     
    {    
        "number": "12",
        "ip": "35.182.54.20",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "11",
        "ip": "15.223.46.166",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Mumbai     
    {    
        "number": "10",
        "ip": "52.66.93.156",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "9",
        "ip": "43.204.96.157",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sao Paolo     
    {    
        "number": "8",
        "ip": "15.229.26.89",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "7",
        "ip": "15.228.35.157",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Singapore
    {    
        "number": "6",
        "ip": "54.169.78.134",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "5",
        "ip": "54.169.71.33",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # N. Virginia
    {    
        "number": "4",
        "ip": "54.172.199.112",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "3",
        "ip": "18.234.83.0",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Frankfurt
    {
        "number": "2",
        "ip": "3.68.65.62",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "1",
        "ip": "3.77.156.202",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]


N = len(peers)
F = 5
P = 0
T = 300 # Runtime
D = 3000 # Notarization delay
FICC = True
BI=5
PI=20
BIRU=100
RUT=1

UPDATE_REPO = False
UPDATE_MAIN = False


if UPDATE_MAIN:
    print("\Cleaning repo on replicas")

    for peer in peers:
        print("\nCleaning main for replica", peer["number"])
        clone_repo_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'rm -rf fast_internet_computer_consensus/src/main.rs\''
        process = subprocess.Popen(clone_repo_cmd, shell=True)
        process.wait()


    print("\Cloning main on replicas")

    for peer in peers:
        print("\nCloning main for replica", peer["number"])
        clone_repo_cmd = f'scp -i ./keys/{peer["key_file"]} ./src/main.rs ubuntu@{peer["ip"]}:fast_internet_computer_consensus/src/main.rs'
        process = subprocess.Popen(clone_repo_cmd, shell=True)
        process.wait()

    print("\nRepo cloned on replicas")

    processes = []
    for peer in peers:
        print("\nBuilding container for replica", peer["number"])
        build_container_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'cd fast_internet_computer_consensus && docker compose build\''
        process = subprocess.Popen(build_container_cmd, shell=True, stdout=subprocess.DEVNULL)
        processes.append(process)

    for p in processes:
        p.communicate() # waits for replica to finish

    print("\nContainer built on replicas")



if UPDATE_REPO:
    print("\Cleaning repo on replicas")

    for peer in peers:
        print("\nCleaning repo for replica", peer["number"])
        clone_repo_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'rm -rf fast_internet_computer_consensus/\''
        process = subprocess.Popen(clone_repo_cmd, shell=True)
        process.wait()


    print("\Cloning repo on replicas")

    for peer in peers:
        print("\nCloning repo for replica", peer["number"])
        clone_repo_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'git clone https://github.com/yannvon/fast_internet_computer_consensus.git\''
        process = subprocess.Popen(clone_repo_cmd, shell=True)
        process.wait()

    print("\nRepo cloned on replicas")

    processes = []
    for peer in peers:
        print("\nBuilding container for replica", peer["number"])
        build_container_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'cd fast_internet_computer_consensus && docker compose build\''
        process = subprocess.Popen(build_container_cmd, shell=True, stdout=subprocess.DEVNULL)
        processes.append(process)

    for p in processes:
        p.communicate() # waits for replica to finish

    print("\nContainer built on replicas")


print("\nStarting subnet running " + ("FICC" if FICC else "ICC") + f" with n={N}, f={F} and p={P}")

for peer in peers:
    with open(".env.example", "r") as file:
        contents = file.readlines()
        contents[0] = "REPLICA_NUMBER="+peer["number"]+"\n"
        contents[1] = "TOTAL_REPLICA_NUMBER="+str(N)+"\n"
        contents[2] = "FAULTY_REPLICAS="+str(F)+"\n"
        contents[3] = "DISAGREEING_REPLICA="+str(P)+"\n"
        contents[4] = "EXECUTION_TIME="+str(T)+"\n"
        contents[5] = "NOTARIZATION_DELAY="+str(D)+"\n"
        contents[6] = "BROADCAST_INTERVAL="+str(BI)+"\n"
        contents[7] = "ARTIFACT_MANAGER_POLLING_INTERVAL="+str(PI)+"\n"
        contents[8] = "BROADCAST_INTERVAL_RAMP_UP="+str(BIRU)+"\n"
        contents[9] = "RAMP_UP_TIME="+str(RUT)+"\n"

    with open("./.env.example", "w") as file:
        file.writelines(contents)

    os.chmod("./keys/"+peer["key_file"], 0o400)
    set_params_cmd = f'scp -i ./keys/{peer["key_file"]} ./.env.example ubuntu@{peer["ip"]}:fast_internet_computer_consensus/.env'
    subprocess.run(set_params_cmd, shell=True)

with open("docker-compose.yml", "r") as file:
    contents = file.readlines()
    if FICC:
        contents[8] = '    command: ["--cod", "--r", $REPLICA_NUMBER, "--n", $TOTAL_REPLICA_NUMBER, "--f", $FAULTY_REPLICAS, "--p", $DISAGREEING_REPLICA, "--t", $EXECUTION_TIME, "--d", $NOTARIZATION_DELAY, "--broadcast_interval", "$BROADCAST_INTERVAL","--artifact_manager_polling_interval", "$ARTIFACT_MANAGER_POLLING_INTERVAL", "--broadcast_interval_ramp_up", "$BROADCAST_INTERVAL_RAMP_UP", "--ramp_up_time", "$RAMP_UP_TIME", "--port", $PORT]\n'
    else:
        contents[8] = '    command: ["--r", $REPLICA_NUMBER, "--n", $TOTAL_REPLICA_NUMBER, "--f", $FAULTY_REPLICAS, "--p", $DISAGREEING_REPLICA, "--t", $EXECUTION_TIME, "--d", $NOTARIZATION_DELAY, "--broadcast_interval", "$BROADCAST_INTERVAL","--artifact_manager_polling_interval", "$ARTIFACT_MANAGER_POLLING_INTERVAL", "--broadcast_interval_ramp_up", "$BROADCAST_INTERVAL_RAMP_UP", "--ramp_up_time", "$RAMP_UP_TIME", "--port", $PORT]\n'

with open("docker-compose.yml", "w") as file:
    file.writelines(contents)

for peer in peers:
    set_protocol_cmd = f'scp -i ./keys/{peer["key_file"]} ./docker-compose.yml ubuntu@{peer["ip"]}:fast_internet_computer_consensus/docker-compose.yml'
    subprocess.run(set_protocol_cmd, shell=True)

print("\nReplicas parameters set")

processes = []
for peer in peers:
    start_replica_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} "cd fast_internet_computer_consensus && docker compose up --build"'
    process = subprocess.Popen(start_replica_cmd, shell=True, stdout=subprocess.DEVNULL)
    processes.append(process)

print("\nReplicas started")

time.sleep(100)  # wait for docker containers to start

print("\nConnecting peers")

for peer in peers: 
    response = requests.get("http://"+peer["ip"]+":"+peer["web_server_port"]+"/local_peer_id")
    if response.status_code == 200:
        peer["id"] = response.text[1:-1]
    else:
        print("Peer " + peer["number"] + " not reachable")

print ("\n Peer id collection terminated")
for i,peer in enumerate(peers):
    remote_peers_addresses = ""
    for j,other_peer in enumerate(peers):
        if i != j:
            remote_peers_addresses += "/ip4/"+other_peer["ip"]+"/tcp/"+other_peer["libp2p_port"]+"/p2p/"+other_peer["id"]+","
    peer["remote_peers_addresses"] = remote_peers_addresses[0:-1]

for peer in peers:
    requests.post("http://"+peer["ip"]+":"+peer["web_server_port"]+"/remote_peers_addresses", data=peer["remote_peers_addresses"])

print(f"\nProtocol started for {T} seconds")

for p in processes:
    p.communicate() # waits for replica to finish

print("\nReplicas stopped")

now = int(time.time())
folder = f'{("FICC" if FICC else "ICC")}_{N}_{F}_{P}_{D}_{T}_{now}'
subprocess.run(f'cd benchmark && mkdir {folder}', shell=True, stdout=subprocess.DEVNULL)

for peer in peers:
    get_benchmark_results_cmd = f'scp -i ./keys/{peer["key_file"]} ubuntu@{peer["ip"]}:fast_internet_computer_consensus/benchmark/benchmark_results.json benchmark/{("FICC" if FICC else "ICC")}_{N}_{F}_{P}_{D}_{T}_{now}/benchmark_results_{peer["number"]}.json'
    subprocess.run(get_benchmark_results_cmd, shell=True, stdout=subprocess.DEVNULL)

print(f'\nResults written in folder benchmark/{folder}')

def getBenchmarks():
    with open(f'./benchmark/{folder}/benchmark_results_1.json', 'r') as f:
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

def plotLatencies(ax, filled_iterations, filled_latencies, filled_finalization_types):
    colors = ["green", "blue", "grey"]
    color_labels = {
        "green": "FP-finalized block",
        "blue": "IC-finalized block",
        "grey": "finalization from peer"
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
    plotLatencies(plt.gca(), filled_iterations, filled_latencies, filled_finalization_types)

    printMetrics(
        average_latency,
        total_fp_finalizations,
        total_ic_finalizations,
        total_dk_finalizations,
        total_non_finalizations,
    )
    plt.show()

print("Displaying results for replica 1")

benchmark = getBenchmarks()

getResults()
