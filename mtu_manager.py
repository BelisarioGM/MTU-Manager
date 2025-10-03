#!/usr/bin/env python3
"""
mtu_manager.py — Listar y cambiar MTU de interfaces de red (Linux/macOS/Windows)

Uso:
  - Listar solamente:
      python3 mtu_manager.py --list
  - Interactivo (listar -> elegir interfaz -> aplicar MTU -> confirmar):
      sudo python3 mtu_manager.py          (Linux/macOS)
      python mtu_manager.py                (Windows, en consola como Administrador)
"""

import argparse
import platform
import subprocess
import sys
import re
from shutil import which

OS = platform.system()

def run(cmd):
    # Ejecuta comando y retorna (rc, stdout, stderr)
    try:
        proc = subprocess.run(cmd, shell=False, capture_output=True, text=True)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"Comando no encontrado: {cmd[0]}"

def list_interfaces():
    """
    Retorna lista de tuplas (name, mtu).
    """
    if OS == "Linux":
        if which("ip"):
            rc, out, err = run(["ip", "-o", "link"])
            if rc == 0:
                # Ejemplo:
                # 2: eth0: <...> mtu 1500 qdisc ...
                ifaces = []
                for line in out.splitlines():
                    m = re.match(r"\d+:\s+([^:]+):.*\smtu\s(\d+)", line)
                    if m:
                        name = m.group(1)
                        mtu = int(m.group(2))
                        ifaces.append((name, mtu))
                return ifaces
        # Fallback: /sys/class/net
        import os
        ifaces = []
        base = "/sys/class/net"
        for name in os.listdir(base):
            try:
                with open(f"{base}/{name}/mtu", "r") as f:
                    mtu = int(f.read().strip())
                ifaces.append((name, mtu))
            except Exception:
                pass
        return ifaces

    elif OS == "Darwin":  # macOS
        rc, out, err = run(["ifconfig", "-a"])
        if rc == 0:
            ifaces = []
            current = None
            for line in out.splitlines():
                m = re.match(r"^([a-z0-9]+):\s", line)
                if m:
                    current = m.group(1)
                    mtu_m = re.search(r"\bmtu\s+(\d+)", line)
                    if mtu_m:
                        ifaces.append((current, int(mtu_m.group(1))))
                else:
                    if current:
                        mtu_m = re.search(r"\bmtu\s+(\d+)", line)
                        if mtu_m:
                            ifaces = [(n, int(mtu_m.group(1)) if n == current else v) for n, v in ifaces]
            return ifaces
        return []

    elif OS == "Windows":
        rc, out, err = run(["netsh", "interface", "ipv4", "show", "subinterfaces"])
        if rc != 0 or not out:
            return []
        ifaces = []
        lines = [l for l in out.splitlines() if l.strip()]
        for line in lines:
            m = re.match(r"\s*(\d+)\s+.+?\s+(.+)$", line)
            if m and m.group(1).isdigit():
                mtu = int(m.group(1))
                name = m.group(2).strip()
                ifaces.append((name, mtu))
        return ifaces

    else:
        return []

def set_mtu(interface, mtu):
    mtu = str(mtu)
    if OS == "Linux":
        if which("ip"):
            return run(["ip", "link", "set", "dev", interface, "mtu", mtu])
        if which("ifconfig"):
            return run(["ifconfig", interface, "mtu", mtu])
        return (127, "", "No se encontró 'ip' ni 'ifconfig'.")

    elif OS == "Darwin":  # macOS
        return run(["ifconfig", interface, "mtu", mtu])

    elif OS == "Windows":
        # netsh requiere name=<Interfaz> para evitar problemas con espacios
        return run(["netsh", "interface", "ipv4", "set", "subinterface", f"name={interface}", f"mtu={mtu}", "store=persistent"])

    else:
        return (1, "", f"Sistema operativo no soportado: {OS}")

def print_table(ifaces, header="Interfaces y MTU actuales"):
    if not ifaces:
        print("No se detectaron interfaces.")
        return
    w = max(len(n) for n, _ in ifaces)
    print(f"\n{header}:")
    print("-" * (w + 10))
    print(f"{'INTERFAZ'.ljust(w)}  MTU")
    print("-" * (w + 10))
    for n, m in ifaces:
        print(f"{n.ljust(w)}  {m}")
    print("-" * (w + 10))

def valid_mtu(value):
    try:
        v = int(value)
        return 576 <= v <= 9216
    except ValueError:
        return False

def interactive_flow():
    # 1) Listar
    ifaces = list_interfaces()
    print_table(ifaces)

    if not ifaces:
        sys.exit(1)

    # 2) Elegir interfaz
    names = [n for n, _ in ifaces]
    iface = input("\n¿A qué interfaz quieres cambiarle el MTU? (escribe el nombre exacto): ").strip()

    if iface not in names:
        print(f"❌ Interfaz '{iface}' no encontrada. Debe ser una de: {', '.join(names)}")
        sys.exit(1)

    # 3) Nuevo valor MTU
    mtu = input("Nuevo valor de MTU (576–9216 es típico): ").strip()
    if not valid_mtu(mtu):
        print("❌ MTU inválido. Debe ser entero y estar entre 576 y 9216.")
        sys.exit(1)

    # 4) Aplicar
    print(f"\nAplicando MTU {mtu} a '{iface}'...")
    rc, out, err = set_mtu(iface, int(mtu))
    if rc != 0:
        print("❌ No se pudo aplicar el cambio.")
        if out:
            print("STDOUT:", out)
        if err:
            print("STDERR:", err)
        if OS in ("Linux", "Darwin"):
            print("\nSugerencias:")
            print("- Asegúrate de ejecutarlo con sudo.")
            print("- Verifica que la interfaz exista y no esté controlada por otra herramienta.")
        elif OS == "Windows":
            print("\nSugerencias:")
            print("- Ejecuta la consola como Administrador.")
            print("- Usa el nombre EXACTO de la interfaz que muestra 'netsh interface ipv4 show subinterfaces'.")
        sys.exit(1)
    else:
        print("✅ Cambio aplicado correctamente.")

    # 5) Confirmar
    ifaces2 = list_interfaces()
    print_table(ifaces2, header="Confirmación (listado actualizado)")

def parse_args():
    p = argparse.ArgumentParser(description="Listar y cambiar MTU de interfaces (Linux/macOS/Windows)")
    p.add_argument("--list", action="store_true", help="Listar interfaces y MTU y salir")
    return p.parse_args()

def main():
    args = parse_args()
    if args.list:
        ifaces = list_interfaces()
        print_table(ifaces)
        sys.exit(0)
    interactive_flow()

if __name__ == "__main__":
    main()
