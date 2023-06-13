import requests
import subprocess
import time
import os



peers = [
    # Sao Paolo
    {
        "number": "16",
        "ip": "54.94.232.44",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sao Paolo
    {
        "number": "15",
        "ip": "18.231.108.79",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Bahrain
    {
        "number": "14",
        "ip": "15.184.220.208",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Stockholm
    {
        "number": "13",
        "ip": "13.51.56.252",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Frankfurt
    {
        "number": "12",
        "ip": "3.120.206.238",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Montreal
    {
        "number": "11",
        "ip": "3.99.221.224",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Sydney
    {
        "number": "10",
        "ip": "13.54.192.50",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Singapore
    {
        "number": "9",
        "ip": "13.212.154.248",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Seoul
    {
        "number": "8",
        "ip": "13.209.9.52",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Mumbai
    {
        "number": "7",
        "ip": "3.111.33.248",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Melbourne
    {    
        "number": "6",
        "ip": "16.50.238.41",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
    # Hong Kong
    {
        "number": "5",
        "ip": "18.162.194.131",
        "web_server_port": "56790",
        "libp2p_port": "56789",
        "key_file": "aws_global",
        "id": "",
        "remote_peers_addresses": "",
    },
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
