import requests
import subprocess
import time
import os

peers = [
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
