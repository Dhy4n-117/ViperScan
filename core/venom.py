import socket
import requests
import ftplib
from utils.colors import Color


def check_ftp_anonymous(ip):
    """
    Attempts to login to FTP with username 'anonymous'.
    Returns True if successful (VULNERABLE).
    """
    try:
        ftp = ftplib.FTP(ip, timeout=5)
        ftp.login('anonymous', 'anonymous')
        ftp.quit()
        return True
    except:
        return False


def check_http_headers(ip, port):
    """
    Checks web servers for missing security headers.
    Returns a list of missing headers.
    """
    target = f"http://{ip}:{port}"
    issues = []
    try:
        # We use a short timeout so scans don't hang
        res = requests.get(target, timeout=3)
        headers = res.headers

        # 1. X-Frame-Options (Prevents Clickjacking)
        if 'X-Frame-Options' not in headers:
            issues.append("Missing 'X-Frame-Options' header (Clickjacking Risk)")

        # 2. Content-Security-Policy (Prevents XSS)
        if 'Content-Security-Policy' not in headers:
            issues.append("Missing 'Content-Security-Policy' header (XSS Risk)")

        # 3. Server (Information Leakage) - optional but good to know
        if 'Server' in headers:
            issues.append(f"Server Header Revealed: {headers['Server']}")

        return issues
    except:
        return []


def inject_venom(target_ip, open_ports):
    """
    The Controller: Decides which checks to run based on the port number.
    open_ports: list of tuples (port, banner, ...)
    """
    print(f"\n{Color.BLUE}[*] initiating Venom Module (Vulnerability Checks)...{Color.RESET}")

    vuln_found = False

    for port_info in open_ports:
        port = port_info[0]

        # --- FTP CHECK (Port 21) ---
        if port == 21:
            print(f"    [*] Checking Port 21 for Anonymous FTP...")
            if check_ftp_anonymous(target_ip):
                print(f"    {Color.RED}[!] CRITICAL: Anonymous FTP Login Allowed on {target_ip}!{Color.RESET}")
                vuln_found = True

        # --- HTTP CHECK (Ports 80, 8080) ---
        elif port in [80, 8080]:
            print(f"    [*] Checking Port {port} for Web Vulnerabilities...")
            issues = check_http_headers(target_ip, port)

            if issues:
                vuln_found = True
                for issue in issues:
                    # Check if it's just info or a risk
                    if "Risk" in issue:
                        print(f"    {Color.YELLOW}[!] {issue}{Color.RESET}")
                    else:
                        print(f"    {Color.BLUE}[i] {issue}{Color.RESET}")

    if not vuln_found:
        print(f"{Color.GREEN}    [*] No obvious vulnerabilities found in basic checks.{Color.RESET}")