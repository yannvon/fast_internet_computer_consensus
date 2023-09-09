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
    # Sao Paolo
    {
        "number": "3",
        "ip": "15.228.193.25",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm
    {
        "number": "2",
        "ip": "16.170.231.130",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Melbourne
    {
        "number": "1",
        "ip": "16.50.58.129",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]

for peer in peers:
    print("\nDisk usage for peer ", peer["number"])
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'df -H\''
    process = subprocess.Popen(cmd, shell=True)
    process.wait()

for peer in peers:
    print("\nMemory for peer ", peer["number"])
    cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'free -m\''
    process = subprocess.Popen(cmd, shell=True)
    process.wait()
