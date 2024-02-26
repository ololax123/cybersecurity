import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import signal
import os

# Define global variables to hold the results
tcp_results = []
udp_results = []

def signal_handler(signal, frame):
    print("\nScan interrupted, printing results...")
    print_results()
    os._exit(0)
    
signal.signal(signal.SIGINT, signal_handler)

def print_results():
    # Function to process and print results for both TCP and UDP
    process_results('TCP', tcp_results)
    process_results('UDP', udp_results)


def process_results(protocol, results):
    if not results:
        return
    results.sort(key=lambda x: x[0])  # Ensure results are sorted by port number
    start_port = results[0][0]
    end_port = start_port
    status = results[0][1]

    for port, current_status in results[1:]:
        # If consecutive and status matches, extend the range
        if port == end_port + 1 and current_status == status:
            end_port = port
        else:
            # Print the range and reset for the next range
            print_range(start_port, end_port, status, protocol)
            start_port = port
            end_port = port
            status = current_status

    # Print the last range
    print_range(start_port, end_port, status, protocol)

def print_range(start_port, end_port, status, protocol):
    if start_port == end_port:
        print(f"[{protocol}] Port {start_port} is {status}")
    else:
        print(f"[{protocol}] Ports {start_port}-{end_port} are {status}")


def scan_tcp_port(target_ip, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                return (port, "Open")
    except Exception:
        pass
    return (port, False)

def scan_udp_port(target_ip, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(timeout)
            message = b''
            sock.sendto(message, (target_ip, port))
            sock.recvfrom(1024)
            return (port, 'Open')
    except socket.timeout:
        return (port, 'Possibly Open/Filtered')
    except Exception:
        pass
    return (port, 'Closed')

def load_port_services(protocol):
    filename = f"{protocol}-ports.txt"
    port_services = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if ',' in line:
                    service, port_str = line.strip().split(',')
                    port_services[int(port_str)] = service
    except FileNotFoundError:
        print(f"Warning: {filename} not found. Proceeding without service names.")
    return port_services

# Load services for both protocols at the start
tcp_services = load_port_services('tcp')
udp_services = load_port_services('udp')

def process_results(protocol, results):
    if not results:
        return
    results.sort()
    start_port = results[0][0]
    last_port = start_port
    last_status = results[0][1]

    for port, status in results[1:]:
        if port == last_port + 1 and status == last_status:
            last_port = port
        else:
            print_range(start_port, last_port, last_status, protocol)
            start_port = port
            last_port = port
            last_status = status

    print_range(start_port, last_port, last_status, protocol)

def print_range(start_port, end_port, status, protocol):
    services = tcp_services if protocol == 'TCP' else udp_services
    if start_port == end_port:
        service_name = services.get(start_port, "Unknown Service")
        print(f"[{protocol}] Port {start_port} ({service_name}) is {status}")
    else:
        start_service = services.get(start_port, "Unknown Service")
        end_service = services.get(end_port, "Unknown Service")
        print(f"[{protocol}] Ports {start_port}-{end_port} ({start_service} to {end_service}) are {status}")

def scan_port(args):
    target_ip, port, protocol, timeout = args
    if protocol == 'tcp':
        result = scan_tcp_port(target_ip, port, timeout)
        if result[1]:
            tcp_results.append(result)
    elif protocol == 'udp':
        result = scan_udp_port(target_ip, port, timeout)
        if result[1] != 'Closed':
            udp_results.append(result)

def main(hostname, start_port, end_port, udp, tcp, max_workers=100):
    target_ip = socket.gethostbyname(hostname)
    print(f"Starting scan on host: {target_ip}")

    protocols = []
    if tcp:
        protocols.append('tcp')
    if udp:
        protocols.append('udp')

    scan_args = [(target_ip, port, protocol, 1.0) for port in range(start_port, end_port + 1) for protocol in protocols]
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(scan_port, arg) for arg in scan_args]
        try:
            for future in as_completed(futures):
                future.result()
        except KeyboardInterrupt:
            print("\nScan interrupted, printing results...")

    process_results('TCP', tcp_results)
    process_results('UDP', udp_results)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan both TCP and UDP ports on a given host.")
    parser.add_argument("hostname", help="Hostname or IP address of the target")
    parser.add_argument("-s", "--startport", type=int, default=1, help="Start port (default: 1)")
    parser.add_argument("-e", "--endport", type=int, default=65535, help="End port (default: 65535)")
    parser.add_argument("-u", "--udp", action='store_true', help="Include UDP ports in the scan")
    parser.add_argument("-t", "--tcp", action='store_true', help="Include TCP ports in the scan")
    parser.add_argument("-p", "--portrange", type=str, help="Specify a port range (e.g., 20-80)")

    args = parser.parse_args()

    # Parse port range if specified
    if args.portrange:
        start, end = map(int, args.portrange.split("-"))
        args.startport = start
        args.endport = end

    # Ensure at least one protocol is selected
    if not args.udp and not args.tcp:
        print("No protocol selected, defaulting to TCP.")
        args.tcp = True

    main(args.hostname, args.startport, args.endport, args.udp, args.tcp)
