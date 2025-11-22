import argparse
import sys
import socket
from datetime import datetime
from core.scanner import start_scan
from utils.reporter import save_json_report, save_html_report
from utils.colors import Color

def display_banner():
    banner = r"""
    __      __  _                         
    \ \    / / (_)                        
     \ \  / /   _   _ __     ___   _ __   
      \ \/ /   | | | '_ \   / _ \ | '__|  
       \  /    | | | |_) | |  __/ | |     
        \/     |_| | .__/   \___| |_|     
                   | |                    
                   |_|                    
    -------------------------------------
    Reconnaissance & Vulnerability Scanner
    For Educational Use Only
    -------------------------------------
    """
    print(Color.GREEN + banner + Color.RESET)

def parse_arguments():
    """
    Sets up the command line arguments.
    This allows users to run: python main.py -t 192.168.1.1 -p 80
    """
    parser = argparse.ArgumentParser(description="ViperScan: A Network Reconnaissance Tool")
    
    # Target Argument (Required)
    parser.add_argument("-t", "--target", 
                        help="Target IP address or Domain (e.g., 192.168.1.1)", 
                        required=True)
    
    # Port Argument (Optional - defaults to common ports)
    parser.add_argument("-p", "--ports", 
                        help="Ports to scan (e.g., '1-100', '80,443'). Default: 1-1000", 
                        default="1-1000")
    
    # Threading Argument (Performance)
    parser.add_argument("--threads", 
                        help="Number of threads for faster scanning. Default: 50", 
                        type=int, 
                        default=50)
    
    # Output Argument
    parser.add_argument("-o", "--output", 
                        help="Save results to a JSON file")

    return parser.parse_args()

def validate_target(target):
    """
    Ensures the target is valid before we start blasting packets.
    """
    try:
        # This converts a domain (google.com) to an IP (142.250.x.x)
        # If it's already an IP, it just returns the IP.
        ip_address = socket.gethostbyname(target)
        return ip_address
    except socket.gaierror:
        print(f"[!] Error: Could not resolve hostname {target}")
        sys.exit(1)

def parse_ports(ports_str):
    """
    Parses a string like "1-100" or "80,443" into a list of integers.
    """
    if "-" in ports_str:
        start, end = map(int, ports_str.split("-"))
        return range(start, end + 1)
    elif "," in ports_str:
        return [int(p) for p in ports_str.split(",")]
    else:
        return [int(ports_str)]

def main():
    display_banner()
    
    # 1. Parse the arguments
    args = parse_arguments()
    
    # 2. Validate the target
    print(f"[*] Validating target: {args.target}...")
    target_ip = validate_target(args.target)
    print(f"[*] Target resolved to: {target_ip}")

    # 3. Parse ports
    ports = parse_ports(args.ports)
    print(f"[*] Ports parsed: Scanning {len(ports)} ports")
    print(f"[*] Threads set to: {args.threads}")

    # 4. Start the Scan
    print("\n[+] Starting Scan... (Press Ctrl+C to stop)")
    start_time = datetime.now()

    try:
        # CALL THE NEW MODULE HERE
        open_ports = start_scan(target_ip, ports, args.threads)

        print(f"\n[*] Scan complete. Found {len(open_ports)} open ports.")

    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        sys.exit()
        
    end_time = datetime.now()
    print(f"\n[+] Scan completed in {end_time - start_time}")

    # 5. Save Report
    if args.output:
        if open_ports:
            # Check file extension to decide report type
            if args.output.endswith(".json"):
                save_json_report(target_ip, open_ports, args.output)
            elif args.output.endswith(".html"):
                save_html_report(target_ip, open_ports, args.output)
            else:
                # Default to JSON if no extension provided
                save_json_report(target_ip, open_ports, args.output + ".json")
        else:
            print(f"{Color.RED}[!] No open ports found. Skipping report.")

if __name__ == "__main__":
    main()