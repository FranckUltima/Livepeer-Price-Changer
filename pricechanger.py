import requests
import os
import subprocess
import json

# Dictionary of containers and configuration files for each node
NODES = {
    'Node1': {'container_name': 'node1-standalone', 'port': '7935', 'config_file': '/root/.lpData/livepeer_NODE1.conf'},
    'Node2': {'container_name': 'node2-standalone', 'port': '7935', 'config_file': '/root/.lpData/livepeer_NODE2.conf'},
    'Node3': {'container_name': 'node3-standalone', 'port': '7935', 'config_file': '/root/.lpData/livepeer_NODE3.conf'},
    'Node4': {'container_name': 'node4-standalone', 'port': '7935', 'config_file': '/root/.lpData/livepeer_NODE4.conf'},
}

def get_container_ip(container_name):
    try:
        result = subprocess.run(['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name], stdout=subprocess.PIPE, check=True)
        ip_address = result.stdout.decode().strip()
        if not ip_address:
            raise ValueError(f"Could not find IP address for container {container_name}")
        return ip_address
    except subprocess.CalledProcessError as e:
        print(f"Error inspecting container {container_name}: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing container info for {container_name}: {e}")
        return None

def set_price(node, price):
    data = {
        'pixelsPerUnit': 1e12,
        'pricePerUnit': price,
        'currency': 'USD',
        'broadcasterEthAddr': 'default'
    }
    container_name = node['container_name']
    container_ip = get_container_ip(container_name)
    if not container_ip:
        print(f"Could not get IP address for container {container_name}. Skipping...")
        return
    url = f'http://{container_ip}:{node["port"]}/setPriceForBroadcaster'
    print(f"Sending POST request to {url} with data {data}")
    response = requests.post(url, data=data)
    print(f"Response: {response.status_code} {response.text}")

def update_config_file(node, price):
    container_name = node['container_name']
    config_file = node['config_file']
    
    # Read the configuration file from the container
    command = f"docker exec {container_name} cat {config_file}"
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error reading configuration file {config_file} in container {container_name}: {result.stderr.decode()}")
        return

    lines = result.stdout.decode().splitlines()

    # Initialize a variable to track if the update has been made
    update_done = False

    # Replace the line containing the price per pixel with the new value in USD
    for i, line in enumerate(lines):
        if 'pricePerUnit' in line:
            lines[i] = f'pricePerUnit {price}USD\n'
            update_done = True
            break  # Stop the loop after the first update

    # If the line was not found (and therefore not updated), add the new value
    if not update_done:
        lines.append(f'pricePerUnit {price}USD\n')

    # Write the changes to the configuration file in the container
    new_config = "\n".join(lines)
    command = f"echo '{new_config}' | docker exec -i {container_name} sh -c 'cat > {config_file}'"
    result = subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    if result.returncode != 0:
        print(f"Error writing configuration file {config_file} in container {container_name}: {result.stderr.decode()}")

def main():
    while True:
        # Display available nodes
        node_names = list(NODES.keys())
        for i, node_name in enumerate(node_names, 1):
            print(f'{i}. {node_name}')
        print(f'{len(node_names) + 1}. Quit')

        # Ask the user which node they want to modify
        node_index = int(input('Which node do you want to modify? (Enter the number) ')) - 1

        if node_index == len(node_names):
            break

        node_name = node_names[node_index]
        node = NODES[node_name]
        print(f'You have selected the node {node_name}.')

        # Ask the user for the new price per pixel
        price = float(input('What is the new price in USD? '))

        # Modify the price and update the configuration file
        set_price(node, price)
        update_config_file(node, price)

        print(f'The price for {node_name} has been set to {price}.')

if __name__ == '__main__':
    main()