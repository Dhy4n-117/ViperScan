import socket
from concurrent.futures import ThreadPoolExecutor
from core.grabber import get_banner
from utils.colors import Color


def analyze_banner(banner):
    """
    Simple heuristic to guess the OS based on the banner string.
    """
    banner_lower = banner.lower()
    if "ubuntu" in banner_lower or "debian" in banner_lower:
        return "Linux (Debian/Ubuntu)"
    elif "windows" in banner_lower or "microsoft" in banner_lower:
        return "Windows Server"
    elif "apache" in banner_lower:
        return "Likely Linux/Unix"
    else:
        return "Unknown OS"


def scan_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        result = s.connect_ex((ip, port))
        s.close()

        if result == 0:
            banner = get_banner(ip, port)
            os_guess = analyze_banner(banner)
            return (port, banner, os_guess)
    except:
        pass
    return None


def start_scan(target_ip, ports, threads):
    print(f"{Color.BLUE}[*] Scanning {len(ports)} ports on {target_ip} with {threads} threads...")

    results_list = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        results = executor.map(lambda p: scan_port(target_ip, p), ports)

        for result in results:
            if result:
                port, banner, os_guess = result

                # Professional formatted output
                print(
                    f"    {Color.GREEN}[+] Port {port:<5} OPEN {Color.RESET}| {banner[:40]:<40} | {Color.YELLOW}{os_guess}")

                results_list.append(result)

    return results_list