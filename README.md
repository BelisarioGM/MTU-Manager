# mtu_manager.py

Interactive **Python 3** script to **list** and **change** the **MTU** of your network interfaces on **Linux**, **macOS**, and **Windows**.

---

## ✅ Features

- Lists all interfaces with their current **MTU**.
- Interactively changes the **MTU** for a chosen interface.
- `--list` flag to **only list** interfaces and exit.
- Uses native OS tools:
  - Linux: `ip` (preferred) or `ifconfig`
  - macOS: `ifconfig`
  - Windows: `netsh interface ipv4`

---

## 📦 Requirements

- **Python 3.7+**
- Admin privileges to change MTU:
  - Linux/macOS: run with `sudo`
  - Windows: open terminal as **Administrator**
- System tools:
  - Linux: `iproute2` (`ip`) or `net-tools` (`ifconfig`)
  - macOS: `ifconfig` (preinstalled)
  - Windows: `netsh` (preinstalled)

---

## 📥 Installation

1. Save the script as `mtu_manager.py`.
2. (Optional) Make it executable on Linux/macOS:
   ```bash
   chmod +x mtu_manager.py
   ```

---

## 🧪 Usage

### 1) List interfaces and MTU only
```bash
python3 mtu_manager.py --list
```

**Example output (Linux):**
```
Interfaces and current MTU:
---------------------------
INTERFACE   MTU
---------------------------
lo          65536
eth0        1500
wlan0       1500
---------------------------
```

### 2) Interactive flow (list → pick interface → set MTU → confirm)

**Linux / macOS**
```bash
sudo python3 mtu_manager.py
```

**Windows (PowerShell or CMD as Administrator)**
```powershell
python mtu_manager.py
```

**Sample interaction:**
```
Interfaces and current MTU:
---------------------------
INTERFACE   MTU
---------------------------
Ethernet    1500
Wi-Fi       1500
---------------------------

Which interface do you want to change? (type exact name): Ethernet
New MTU value (576–9216 is typical): 1400

Applying MTU 1400 to 'Ethernet'...
✅ Change applied successfully.

Confirmation (updated list):
---------------------------
INTERFACE   MTU
---------------------------
Ethernet    1400
Wi-Fi       1500
---------------------------
```

---

## 🔧 OS Notes

### Linux
- Preferred: `ip link set dev <iface> mtu <value>`
- Fallback: `ifconfig <iface> mtu <value>`
- For persistence (to avoid NetworkManager/systemd-networkd overwrites):
  - **NetworkManager**: edit the profile in `/etc/NetworkManager/system-connections/*.nmconnection` → `mtu=1400`
  - **netplan (Ubuntu)**: add `mtu: 1400` under the interface in `/etc/netplan/*.yaml`

### macOS
- Uses: `ifconfig <iface> mtu <value>`
- Changes may revert after reconnect/reboot; persist via your network profile if needed.

### Windows
- View: `netsh interface ipv4 show subinterfaces`
- Set: `netsh interface ipv4 set subinterface name="<InterfaceName>" mtu=<value> store=persistent`
- The **name must match exactly** (keep quotes if it has spaces).

---

## 📏 MTU Guidance

- **1500**: standard Ethernet
- **576–9216**: validated range in the script (covers common jumbo frames)
- Ensure your **end-to-end path** supports the chosen MTU. Test with non-fragmenting pings.

---

## 🧰 Troubleshooting

- **“Permission denied / Could not apply change”**
  - Linux/macOS: run with `sudo`
  - Windows: run terminal as Administrator
- **“Interface not found”**
  - Use the **exact** interface name shown by the script / `netsh`
- **MTU reverts after reboot/reconnect**
  - Make the change **persistent** in your network manager (see OS Notes)
- **Missing commands (`ip`, `ifconfig`)**
  - Install `iproute2` or `net-tools` on your distro

---

## 🔎 Fragmentation Tests

### Linux
```bash
# Find largest payload without fragmentation to 8.8.8.8
# (MTU ≈ payload + 28 bytes for ICMP/IPv4)
ping -M do -s 1472 8.8.8.8
```

### Windows
```powershell
# Adjust payload size; -f forbids fragmentation
ping 8.8.8.8 -f -l 1472
```

---

## 📄 License

MIT. Use at your own operational responsibility.

---

## 🗂 Suggested Repo Layout

```
.
├── mtu_manager.py
├── README.md
└── LICENSE
```

---

## 📝 Changelog

- **v1.1**: Added `--list` flag (list and exit).
- **v1.0**: Initial interactive version (list → change → confirm).
