import json
import os
from datetime import datetime


def save_json_report(target, open_ports, filename):
    """
    Saves the scan results to a JSON file.
    data structure: (port, banner)
    """
    # Construct the report dictionary
    report = {
        "target": target,
        "scan_date": str(datetime.now()),
        "total_open_ports": len(open_ports),
        "scan_results": []
    }

    # Loop through our results tuple (port, banner)
    for port_info in open_ports:
        report["scan_results"].append({
            "port": port_info[0],
            "service_banner": port_info[1]
        })
    
    # Write to file
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)
        print(f"[+] Report successfully saved to {filename}")
    except Exception as e:
        print(f"[!] Error saving report: {e}")


# Keep your existing save_json_report function here...
def save_html_report(target, open_ports, filename):
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ViperScan Report - {target}</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #1e1e1e; color: #e0e0e0; margin: 40px; }}
            h1 {{ color: #00ff9d; border-bottom: 2px solid #00ff9d; padding-bottom: 10px; }}
            .summary {{ background-color: #2d2d2d; padding: 20px; border-radius: 8px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #252526; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
            th {{ background-color: #333; color: #00ff9d; }}
            tr:hover {{ background-color: #2d2d2d; }}
            .open {{ color: #00ff9d; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h1>🐍 ViperScan Report</h1>
        <div class="summary">
            <p><strong>Target:</strong> {target}</p>
            <p><strong>Date:</strong> {datetime.now()}</p>
            <p><strong>Open Ports Found:</strong> {len(open_ports)}</p>
        </div>
        <table>
            <thead>
                <tr>
                    <th>Port</th>
                    <th>Status</th>
                    <th>Service Banner</th>
                    <th>OS Guess</th>
                </tr>
            </thead>
            <tbody>
    """

    # Add rows dynamically
    rows = ""
    for port_info in open_ports:
        # port_info is now (port, banner, os_guess)
        port, banner, os_guess = port_info
        rows += f"""
        <tr>
            <td>{port}</td>
            <td class="open">OPEN</td>
            <td>{banner}</td>
            <td>{os_guess}</td>
        </tr>
        """

    footer = """
            </tbody>
        </table>
    </body>
    </html>
    """

    # Write full file
    full_html = html_template + rows + footer

    # Fix filename extension
    if not filename.endswith(".html"):
        filename += ".html"

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"[+] HTML Report saved to {filename}")