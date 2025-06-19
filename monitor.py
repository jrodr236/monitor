# type: ignore

import os
import platform
import subprocess
import time
import re

ARP_FILE = "macs.txt"
SLEEP_TIME = 2  # segons entre escaneigs

def get_arp_table():
    arp_output = subprocess.check_output("arp -a", shell=True, encoding="cp1252")
    entries = []
    regex = re.compile(r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:-]{17})\s+(\w+)", re.UNICODE)
    for line in arp_output.splitlines():
        match = regex.search(line)
        if match:
            ip, mac, tipus = match.groups()
            tipus = tipus.lower()
            if tipus in ["static", "est"]:
                continue
            mac = mac.lower().replace("-", ":")
            entries.append((ip, mac))
    return entries

def load_known_macs():
    macs = {}
    if os.path.exists(ARP_FILE):
        with open(ARP_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(";")
                if len(parts) >= 1:
                    mac = parts[0].lower()
                    desc = parts[1] if len(parts) > 1 else ""
                    macs[mac] = {"desc": desc}
    return macs

def save_macs(macs):
    with open(ARP_FILE, "w") as f:
        for mac, info in macs.items():
            f.write(f"{mac};{info['desc']}\n")

def ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(["ping", param, "1", ip], stdout=subprocess.DEVNULL)
    return result.returncode == 0

def main():
    while True:
        print(f"\n\n{'⏻':<2} {'Descripció':<20} {'MAC':<20} {'IP':<15}")
        print("-" * 65)
        arp_entries = get_arp_table()
        known_macs = load_known_macs()
        updated = False

        mac_to_ip = {mac: ip for ip, mac in arp_entries}

        for ip, mac in arp_entries:
            if mac not in known_macs:
                print(f"🆕 {'NOVA':<20} {mac:<20} {ip:<15}")
                known_macs[mac] = {"desc": "????"}
                updated = True

        if updated:
            save_macs(known_macs)

        for mac, info in known_macs.items():
            if "IGNORA" in info['desc'].upper():
                continue
            ip = mac_to_ip.get(mac)
            if ip:
                active = ping(ip)
                status = "✅" if active else "❌"
            else:
                status = "❌"
                ip = "?"
            print(f"{status} {info['desc']:<20} {mac:<20} {ip:<15}")

        print("-" * 65)
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSortint del monitoratge.")
