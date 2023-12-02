import requests
import subprocess
import time
import os


peers = [ 
     # Cape Town
    {
        "number": "4",
        "ip": "13.246.27.80",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Melbourne
    {
        "number": "3",
        "ip": "16.50.58.129",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sao Paolo
    {
        "number": "2",
        "ip": "15.228.193.25",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm
    {
        "number": "1",
        "ip": "16.170.231.130",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },

]

processes = []

for peer in peers:
    #print("\nEmpty docker on peer ", peer["number"])
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'docker stop $(docker ps -a -q)\''
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)
    processes.append(process)
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'docker rm -vf $(docker ps -aq)\''
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)
    processes.append(process)
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'docker rmi -f $(docker images -aq)\''
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL)
    processes.append(process)

for p in processes:
    p.communicate() # waits for replica to finish

processes = []

for peer in peers:
    #print("\nReboot peer ", peer["number"])
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'sudo reboot\''
    process = subprocess.Popen(cmd, shell=True)
    processes.append(process)

for p in processes:
    p.communicate() # waits for replica to finish