import sqlite3
from datetime import datetime

DB_NAME = "viperscan.db"

def get_db_connection():
    """Establishes a connection to the SQLite database file."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def initialize_db():
    """
    Creates the necessary tables if they don't exist.
    Run this every time the tool starts.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Table 1: The 'Parent' table. Records WHO we scanned and WHEN.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_ip TEXT NOT NULL,
            scan_date TEXT NOT NULL
        )
    ''')
    
    # Table 2: The 'Child' table. Records WHAT we found.
    # The 'scan_id' links this port back to the parent scan.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_id INTEGER,
            port_number INTEGER,
            banner TEXT,
            FOREIGN KEY (scan_id) REFERENCES scans (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[*] Database initialized successfully.")

def save_scan_result(target_ip, open_ports):
    """
    Saves a complete scan to the database.
    open_ports is a list of tuples: (port, banner, os_guess)
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Insert the Scan (Parent)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('INSERT INTO scans (target_ip, scan_date) VALUES (?, ?)', 
                   (target_ip, current_time))
    
    # Get the ID of the scan we just created
    scan_id = cursor.lastrowid
    
    # 2. Insert all the Ports (Children)
    for port_data in open_ports:
        # port_data is (port, banner, os_guess)
        # We only store port and banner for now
        port_num = port_data[0]
        banner = port_data[1]
        
        cursor.execute('''
            INSERT INTO ports (scan_id, port_number, banner)
            VALUES (?, ?, ?)
        ''', (scan_id, port_num, banner))
        
    conn.commit()
    conn.close()
    print(f"[+] Saved scan results to database (Scan ID: {scan_id})")


def get_last_scan_ports(target_ip):
    """
    Retrieves the set of open ports from the MOST RECENT scan of this target.
    Returns: A set of integers (e.g., {80, 443}) or None if no previous scan exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Find the most recent scan ID for this IP
    cursor.execute('''
        SELECT id FROM scans 
        WHERE target_ip = ? 
        ORDER BY id DESC 
        LIMIT 1
    ''', (target_ip,))

    row = cursor.fetchone()

    if not row:
        conn.close()
        return None  # We have never scanned this target before

    last_scan_id = row['id']

    # 2. Get all ports associated with that Scan ID
    cursor.execute('''
        SELECT port_number FROM ports 
        WHERE scan_id = ?
    ''', (last_scan_id,))

    # Convert list of rows into a Python Set {80, 443}
    previous_ports = {row['port_number'] for row in cursor.fetchall()}

    conn.close()
    return previous_ports