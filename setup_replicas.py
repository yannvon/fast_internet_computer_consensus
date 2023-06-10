import requests
import subprocess
import time
import os

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
    # # Canada     
    # {    
    #     "number": "12",
    #     "ip": "35.182.54.20",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "11",
    #     "ip": "15.223.46.166",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # # Mumbai     
    # {    
    #     "number": "10",
    #     "ip": "52.66.93.156",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "9",
    #     "ip": "43.204.96.157",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # # Sao Paolo     
    # {    
    #     "number": "8",
    #     "ip": "15.229.26.89",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "7",
    #     "ip": "15.228.35.157",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # # Singapore
    # {    
    #     "number": "6",
    #     "ip": "54.169.78.134",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "5",
    #     "ip": "54.169.71.33",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # # N. Virginia
    # {    
    #     "number": "4",
    #     "ip": "54.172.199.112",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "3",
    #     "ip": "18.234.83.0",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # # Frankfurt
    # {
    #     "number": "2",
    #     "ip": "3.68.65.62",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
    # {
    #     "number": "1",
    #     "ip": "3.77.156.202",
    #     "web_server_port": "56790",
    #     "libp2p_port": "56789",
    #     "key_file": "aws_global",
    #     "id": "",
    #     "remote_peers_addresses": "",
    # },
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
