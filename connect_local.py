import requests
import subprocess
import time
import os
import json
import matplotlib.pyplot as plt


# Example command to run locally:
# ./target/debug/fast_internet_computer_consensus --cod --r 2 --n 2 --f 0 --p 0 --t 20 --d 3000 --broadcast_interval 10 --artifact_manager_polling_interval 20 --broadcast_interval_ramp_up 100 --ramp_up_time 100 --port 56791 --blocksize 5

peers = [
    {
        "number": "2",
        "ip": "127.0.0.1",
        "web_server_port": "56792",
        "libp2p_port": "56791",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    {
        "number": "1",
        "ip": "127.0.0.1",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]

for peer in peers:
    response = requests.get(
        "http://" + peer["ip"] + ":" + peer["web_server_port"] + "/local_peer_id"
    )
    if response.status_code == 200:
        peer["id"] = response.text[1:-1]
    else:
        print("Peer " + peer["number"] + " not reachable")

print("\n Peer id collection terminated")
for i, peer in enumerate(peers):
    remote_peers_addresses = ""
    for j, other_peer in enumerate(peers):
        if i != j:
            remote_peers_addresses += (
                "/ip4/"
                + other_peer["ip"]
                + "/tcp/"
                + other_peer["libp2p_port"]
                + "/p2p/"
                + other_peer["id"]
                + ","
            )
    peer["remote_peers_addresses"] = remote_peers_addresses[0:-1]

for peer in peers:
    requests.post(
        "http://"
        + peer["ip"]
        + ":"
        + peer["web_server_port"]
        + "/remote_peers_addresses",
        data=peer["remote_peers_addresses"],
    )

print(f"\nProtocol started for seconds")
