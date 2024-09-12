import requests
import netifaces as ni
import socket
import json

# Elasticsearch configuration
ES_HOST = 'http://localhost:9200'  # Elasticsearch host URL
ES_INDEX = 'network-interfaces'     # Name of the index where data will be sent

# Get hostname
def get_hostname():
    return socket.gethostname()

# Get IP addresses, MAC addresses, and other details of all Ethernet interfaces
def get_interface_data():
    interfaces = ni.interfaces()
    interface_data = []

    for interface in interfaces:
        try:
            # Get MAC address
            mac_address = ni.ifaddresses(interface)[ni.AF_LINK][0]['addr']

            # Get all IP addresses (both IPv4 and IPv6 if present)
            if ni.AF_INET in ni.ifaddresses(interface):
                ip_info_list = ni.ifaddresses(interface)[ni.AF_INET]
                
                for ip_info in ip_info_list:
                    ip_address = ip_info.get('addr')
                    netmask = ip_info.get('netmask')

                    # Append the IP address, MAC address, interface, and hostname to the list
                    interface_data.append({
                        'hostname': get_hostname(),   # Include hostname
                        'interface': interface,
                        'ip_address': ip_address,
                        'netmask': netmask,
                        'mac_address': mac_address    # Include MAC address
                    })
        except KeyError:
            # Ignore interfaces that don't have an IP address or MAC address
            continue

    return interface_data

# Send data to Elasticsearch
def send_to_elasticsearch(data):
    url = f'{ES_HOST}/{ES_INDEX}/_doc'
    headers = {'Content-Type': 'application/json'}
    
    for entry in data:
        try:
            response = requests.post(url, data=json.dumps(entry), headers=headers)
            if response.status_code == 201:
                print(f'Successfully sent data for {entry["interface"]} on {entry["hostname"]}')
            else:
                print(f'Failed to send data for {entry["interface"]} on {entry["hostname"]}. Status code: {response.status_code}')
        except Exception as e:
            print(f'Error sending data to Elasticsearch: {str(e)}')

if __name__ == '__main__':
    interface_data = get_interface_data()

    if interface_data:
        print("Sending the following data to Elasticsearch:")
        print(json.dumps(interface_data, indent=4))
        send_to_elasticsearch(interface_data)
    else:
        print("No interface data found to send.")
