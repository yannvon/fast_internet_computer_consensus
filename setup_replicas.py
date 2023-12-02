import requests
import subprocess
import time
import os



peers = [
    # North Virginia
    {
        "number": "16",
        "ip": "18.212.98.107",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Ohio
    {
        "number": "15",
        "ip": "52.15.97.86",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # California
    {
        "number": "14",
        "ip": "18.144.174.69",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Oregon
    {
        "number": "13",
        "ip": "54.149.56.126",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Frankfurt
    {
        "number": "12",
        "ip": "52.28.27.163",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # London
    {
        "number": "11",
        "ip": "13.40.113.238",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Paris
    {
        "number": "10",
        "ip": "15.237.41.56",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm
    {
        "number": "9",
        "ip": "16.170.231.130",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Zurich
    {
        "number": "8",
        "ip": "16.62.64.179",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Hong Kong
    {
        "number": "7",
        "ip": "43.198.109.155",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Jakarta
    {    
        "number": "6",
        "ip": "108.137.96.187",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Melbourne
    {
        "number": "5",
        "ip": "16.50.58.129",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Mumbai
    {    
        "number": "4",
        "ip": "65.2.127.126",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Osaka
    {
        "number": "3",
        "ip": "15.168.60.10",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Seoul
    {
        "number": "2",
        "ip": "13.209.74.15",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Singapore
    {
        "number": "1",
        "ip": "54.255.180.185",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]

others = [
    # Tokyo
    {
        "number": "x",
        "ip": "3.112.230.168",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Montreal
    {
        "number": "x",
        "ip": "35.182.194.19",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Cape Town
    {
        "number": "x",
        "ip": "13.246.27.80",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Bahrain
    {
        "number": "x",
        "ip": "157.175.47.82",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sao Paolo
    {
        "number": "x",
        "ip": "15.228.193.25",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # California 2
    {
        "number": "x",
        "ip": "54.177.165.217",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Ohio 2
    {
        "number": "x",
        "ip": "3.23.131.96",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Zurich 2
    {
        "number": "x",
        "ip": "16.62.97.69",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
]




# Add hosts to known hosts
for peer in peers:
    print("\nAdding IP to known hosts", peer["number"])
    cmd = f'ssh-keyscan {peer["ip"]} >> ~/.ssh/known_hosts'
    process = subprocess.Popen(cmd, shell=True)
    process.wait()


for peer in peers:
    print("\nInstalling docker for replica", peer["number"])
    os.chmod("./keys/"+peer["key_file"], 0o400)
    docker_installation_cmds = [
        "sudo apt-get update",
        "sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
        'echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null',
        "sudo apt-get update",
        "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
        "sudo usermod -aG docker $USER"
    ]
    for cmd in docker_installation_cmds:
        install_docker_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'{cmd}\''
        process = subprocess.Popen(install_docker_cmd, shell=True)
        process.wait()

print("\nDocker installed on new replicas")

for peer in peers:
    print("\nCloning repo for replica", peer["number"])
    clone_repo_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'git clone https://github.com/yannvon/fast_internet_computer_consensus.git\''
    process = subprocess.Popen(clone_repo_cmd, shell=True)
    process.wait()

print("\nRepo cloned on new replicas")

processes = []
for peer in peers:
    print("\nBuilding container for replica", peer["number"])
    build_container_cmd = f'ssh -i ./keys/{peer["key_file"]} -t -q ubuntu@{peer["ip"]} \'cd fast_internet_computer_consensus && docker compose build\''
    process = subprocess.Popen(build_container_cmd, shell=True, stdout=subprocess.DEVNULL)
    processes.append(process)

for p in processes:
    p.communicate() # waits for replica to finish

print("\nContainer built on new replicas")
