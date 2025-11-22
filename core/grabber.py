import socket
import ssl

def get_banner(ip, port):
    """
    Attempts to grab the service banner (the 'Welcome Message')
    from a specific port.
    """
    try:
        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2) # Short timeout so we don't get stuck
        
        # If it's HTTPS (443), we must wrap the socket with SSL context
        if port == 443:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            s = context.wrap_socket(s, server_hostname=ip)
        
        s.connect((ip, port))
        
        # STRATEGY 1: Send a generic HTTP probe.
        # Many servers wait for you to speak first.
        # This byte string asks for the server header.
        probe = f"HEAD / HTTP/1.1\r\nHost: {ip}\r\n\r\n"
        s.send(probe.encode())
        
        # STRATEGY 2: Listen for a response.
        # We read up to 1024 bytes.
        banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
        
        s.close()
        
        # Cleanup: We only want the first line (too much text is messy)
        if banner:
            return banner.split('\n')[0]
        else:
            return "Unknown Service"
            
    except Exception as e:
        return "No Banner / Timeout"