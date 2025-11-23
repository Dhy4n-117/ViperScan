import argparse
import sys
import socket
from datetime import datetime

# Import our modules
from core.scanner import start_scan
from core.database import initialize_db, save_scan_result, get_last_scan_ports
from utils.reporter import save_json_report, save_html_report
from utils.colors import Color
from core.venom import inject_venom

def display_banner():
    banner = r"""
    __      __  _                         
    \ \    / / (_)                        
     \ \  / /   _   _ __     ___   _ __   
      \ \/ /   | | | '_ \   / _ \ | '__|  
       \  /    | | | |_) | |  __/ | |     
        \/     |_| | .__/   \___| |_|     
                   | |                    
                   |_|                    @DHYAN
    -------------------------------------
    Reconnaissance & Vulnerability Scanner
    For Educational Use Only
    -------------------------------------
    """
    print(Color.GREEN + banner + Color.RESET)


def parse_arguments():
    parser = argparse.ArgumentParser(description="ViperScan: A Network Reconnaissance Tool")
    parser.add_argument("-t", "--target", help="Target IP address or Domain", required=True)
    parser.add_argument("-p", "--ports", help="Ports to scan (e.g. 1-1000 or 80,443)", default="1-1000")
    parser.add_argument("--threads", help="Number of threads", type=int, default=50)
    parser.add_argument("-o", "--output", help="Save results to file (JSON/HTML)")
    return parser.parse_args()


def validate_target(target):
    try:
        ip_address = socket.gethostbyname(target)
        return ip_address
    except socket.gaierror:
        print(f"{Color.RED}[!] Error: Could not resolve hostname {target}{Color.RESET}")
        sys.exit(1)


def parse_ports(ports_str):
    if "-" in ports_str:
        start, end = map(int, ports_str.split("-"))
        return range(start, end + 1)
    elif "," in ports_str:
        return [int(p) for p in ports_str.split(",")]
    else:
        return [int(ports_str)]


def main():
    display_banner()

    # 0. Initialize the brain (Database)
    initialize_db()

    # 1. Parse arguments
    args = parse_arguments()

    # 2. Validate target
    print(f"[*] Validating target: {args.target}...")
    target_ip = validate_target(args.target)
    print(f"[*] Target resolved to: {target_ip}")

    # 3. Parse ports
    ports = parse_ports(args.ports)
    print(f"[*] Ports parsed: Scanning {len(ports)} ports")
    print(f"[*] Threads set to: {args.threads}")

    # 4. Start Scan
    print("\n[+] Starting Scan... (Press Ctrl+C to stop)")
    start_time = datetime.now()

    open_ports = []
    try:
        open_ports = start_scan(target_ip, ports, args.threads)
        print(f"\n[*] Scan complete. Found {len(open_ports)} open ports.")
        if open_ports:
            inject_venom(target_ip, open_ports)
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        sys.exit()

    end_time = datetime.now()
    print(f"[+] Scan completed in {end_time - start_time}")

    # 5. Report Generation (JSON/HTML)
    if args.output:
        if open_ports:
            if args.output.endswith(".json"):
                save_json_report(target_ip, open_ports, args.output)
            elif args.output.endswith(".html"):
                save_html_report(target_ip, open_ports, args.output)
            else:
                save_json_report(target_ip, open_ports, args.output + ".json")
        else:
            print(f"{Color.RED}[!] No open ports found. Skipping report.{Color.RESET}")

    # 6. Database & Diff Logic
    if open_ports:
        print("-" * 40)
        print(f"[*] Analyzing changes for {target_ip}...")

        # A. Get history
        previous_ports = get_last_scan_ports(target_ip)

        # B. Get current ports as a set of numbers
        current_ports_set = {p[0] for p in open_ports}

        if previous_ports is None:
            print(f"{Color.BLUE}[*] First time scanning this target. Saving baseline.{Color.RESET}")
        else:
            # Calculate differences
            new_ports = current_ports_set - previous_ports
            closed_ports = previous_ports - current_ports_set

            if not new_ports and not closed_ports:
                print(f"{Color.GREEN}[*] No changes detected since last scan.{Color.RESET}")
            else:
                # ALERT ON NEW PORTS
                for p in new_ports:
                    print(f"{Color.RED}[!] ALERT: Port {p} is NEW (was closed previously)!{Color.RESET}")

                # INFO ON CLOSED PORTS
                for p in closed_ports:
                    print(f"{Color.YELLOW}[-] Note: Port {p} has CLOSED (was open previously).{Color.RESET}")

        # C. Save the new results to DB
        save_scan_result(target_ip, open_ports)


if __name__ == "__main__":
    main()