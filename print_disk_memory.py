import requests
import subprocess
import time
import os

peers = [
    # Cape Town
    {    
        "number": "4",
        "ip": "13.245.18.82",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sao Paolo
    {
        "number": "3",
        "ip": "18.231.108.79",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Melbourne
    {    
        "number": "2",
        "ip": "16.50.238.41",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm
    {
        "number": "1",
        "ip": "13.51.56.252",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]

peers1 = [
    # Tokyo
    {
        "number": "16",
        "ip": "54.238.218.126",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # London
    {
        "number": "15",
        "ip": "3.8.94.18",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Jakarta
    {
        "number": "14",
        "ip": "108.136.215.50",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Cali
    {
        "number": "13",
        "ip": "54.183.129.110",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Ohio
    {
        "number": "12",
        "ip": "18.221.207.66",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Bahrain
    {
        "number": "11",
        "ip": "15.184.220.208",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Paris
    {
        "number": "10",
        "ip": "52.47.154.248",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Frankfurt
    {
        "number": "9",
        "ip": "3.120.206.238",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Montreal
    {
        "number": "8",
        "ip": "3.99.221.224",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Singapore
    {
        "number": "7",
        "ip": "13.212.154.248",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Seoul
    {
        "number": "6",
        "ip": "13.209.9.52",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Mumbai
    {
        "number": "5",
        "ip": "3.111.33.248",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Hong Kong
    {
        "number": "4",
        "ip": "18.162.194.131",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Oregon
    {
        "number": "3",
        "ip": "54.188.124.179",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Cali
    {
        "number": "2",
        "ip": "54.215.31.233",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Ohio
    {
        "number": "1",
        "ip": "3.22.75.75",
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