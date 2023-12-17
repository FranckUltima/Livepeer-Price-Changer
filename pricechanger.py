import requests
import os

# Dictionnaire des ports et des fichiers de configuration pour chaque nœud
NODES = {
    'Ultima Ratio': {'port': '7935', 'config_file': '/etc/go-livepeer/livepeer_UR.conf'},
    'Tiny Hoshi': {'port': '7970', 'config_file': '/etc/go-livepeer/livepeer_HOSHI.conf'},
    'Utopia': {'port': '7975', 'config_file': '/etc/go-livepeer/livepeer_UTOPIA.conf'},
    'Event Horizon': {'port': '7971', 'config_file': '/etc/go-livepeer/livepeer_EVENT.conf'},
}

def set_price(node, price):
    data = {
        'pixelsPerUnit': 1,
        'pricePerUnit': price,
        'broadcasterEthAddr': 'default'
    }
    url = f'http://127.0.0.1:{node["port"]}/setPriceForBroadcaster'
    requests.post(url, data=data)

def update_config_file(node, price):
    with open(node['config_file'], 'r') as file:
        lines = file.readlines()

    # Replace the line with the price per pixel with the new value
    for i, line in enumerate(lines):
        if 'pricePerUnit' in line:
            lines[i] = f'pricePerUnit={price}\n'

    with open(node['config_file'], 'w') as file:
        file.writelines(lines)

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
        price = int(input('What is the new price per pixel? '))

        # Modify the price and update the configuration file
        set_price(node, price)
        update_config_file(node, price)

        print(f'The price for {node_name} has been set to {price}.')

if __name__ == '__main__':
    main()