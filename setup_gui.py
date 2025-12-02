import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import re

class GatewaySetupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dragino PG1302 Gateway Setup")
        self.root.geometry("600x500")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Variables
        self.ip_var = tk.StringVar()
        self.user_var = tk.StringVar(value="pi")
        self.pass_var = tk.StringVar(value="raspberry")
        self.eui_var = tk.StringVar()
        self.lns_var = tk.StringVar(value="wss://eu1.cloud.thethings.network:443")
        self.cups_var = tk.StringVar(value="https://eu1.cloud.thethings.network:443")
        self.api_key_var = tk.StringVar()

        # Tabs
        self.create_connection_tab()
        self.create_config_tab()
        self.create_log_tab()

    def create_connection_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Connection")

        frame = ttk.LabelFrame(tab, text="Raspberry Pi Details", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="IP Address:").grid(row=0, column=0, sticky="w", pady=5)
        ip_entry = ttk.Entry(frame, textvariable=self.ip_var)
        ip_entry.grid(row=0, column=1, sticky="ew", pady=5)
        ip_entry.insert(0, "192.168.x.x") # Placeholder hint
        ip_entry.bind("<FocusIn>", lambda args: ip_entry.delete('0', 'end') if ip_entry.get() == "192.168.x.x" else None)

        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.user_var).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.pass_var, show="*").grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Button(frame, text="Connect & Get EUI", command=self.get_eui).grid(row=3, column=1, sticky="e", pady=10)

        # EUI Display
        eui_frame = ttk.LabelFrame(tab, text="Gateway EUI (Required for TTN)", padding=10)
        eui_frame.pack(fill="x", padx=10, pady=10)
        
        self.eui_entry = ttk.Entry(eui_frame, textvariable=self.eui_var, state="readonly", font=("Courier", 12))
        self.eui_entry.pack(fill="x", pady=5)
        ttk.Button(eui_frame, text="Copy EUI", command=self.copy_eui).pack(anchor="e")

    def create_config_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Configuration")

        frame = ttk.LabelFrame(tab, text="TTN Credentials", padding=10)
        frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(frame, text="LNS URI (wss://...):").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.lns_var, width=40).grid(row=0, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="CUPS URI (https://...):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.cups_var, width=40).grid(row=1, column=1, sticky="ew", pady=5)

        ttk.Label(frame, text="API Key:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(frame, textvariable=self.api_key_var, width=40).grid(row=2, column=1, sticky="ew", pady=5)

        ttk.Button(tab, text="Start Installation & Configuration", command=self.start_configuration).pack(pady=20)

    def create_log_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Logs")
        
        self.log_area = scrolledtext.ScrolledText(tab, state='disabled', height=20)
        self.log_area.pack(expand=True, fill='both', padx=10, pady=10)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def run_ssh_command(self, cmd):
        ip = self.ip_var.get()
        user = self.user_var.get()
        password = self.pass_var.get()
        
        command = ["./ssh_pi.exp", ip, user, password, cmd]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            self.log(f"Error executing: {cmd}\n{stderr}")
            return None
        return stdout.strip()

    def get_eui(self):
        self.log("Retrieving Gateway EUI...")
        def task():
            cmd = "cat /sys/class/net/eth0/address | sed 's/://g' | sed 's/\\(.\\{6\\}\\)\\(.\\{10\\}\\)/\\1fffe\\2/'"
            result = self.run_ssh_command(cmd)
            if result:
                # Clean up result (remove potential ssh banner noise)
                eui = result.splitlines()[-1].strip()
                self.eui_var.set(eui)
                self.log(f"Success! EUI: {eui}")
                messagebox.showinfo("Success", f"Gateway EUI retrieved:\n{eui}")
            else:
                self.log("Failed to retrieve EUI.")

        threading.Thread(target=task).start()

    def copy_eui(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.eui_var.get())
        messagebox.showinfo("Copied", "EUI copied to clipboard!")

    def start_configuration(self):
        if not self.api_key_var.get():
            messagebox.showerror("Error", "Please enter the TTN API Key.")
            return

        self.notebook.select(2) # Switch to logs
        self.log("Starting configuration process...")
        
        def task():
            cmds = [
                # 1. Enable SPI
                "sudo raspi-config nonint do_spi 0",
                
                # 2. Install Software (Check if installed first to save time?)
                "wget -O draginofwd-32bit.deb https://www.dragino.com/downloads/downloads/LoRa_Gateway/PG1302/software/draginofwd-32bit.deb && sudo dpkg -i draginofwd-32bit.deb",
                
                # 3. Configure SPI Device
                "sudo sed -i 's|/dev/spidev1.0|/dev/spidev0.0|g' /etc/station/station.conf",
                
                # 4. Link Reset Script
                "sudo ln -sf /usr/bin/rinit.sh /etc/station/rinit.sh",
                
                # 5. Configure Credentials
                f"echo '{self.lns_var.get()}' | sudo tee /etc/station/tc.uri",
                f"echo '{self.cups_var.get()}' | sudo tee /etc/station/cups.uri",
                f"echo 'Authorization: Bearer {self.api_key_var.get()}' | sudo tee /etc/station/tc.key",
                f"echo 'Authorization: Bearer {self.api_key_var.get()}' | sudo tee /etc/station/cups.key",
                
                # 6. Trust Cert
                "sudo wget -O /etc/station/cups.trust https://letsencrypt.org/certs/isrgrootx1.pem && sudo cp /etc/station/cups.trust /etc/station/tc.trust",
                
                # 7. Persistence
                "sudo systemctl stop draginofwd && sudo systemctl disable draginofwd",
                "sudo systemctl enable draginostation && sudo systemctl restart draginostation"
            ]

            for cmd in cmds:
                self.log(f"Executing: {cmd[:50]}...")
                self.run_ssh_command(cmd)
            
            self.log("Configuration Complete! Checking status...")
            status = self.run_ssh_command("sudo systemctl status draginostation | grep Active")
            self.log(f"Service Status: {status}")
            messagebox.showinfo("Done", "Gateway configuration completed!")

        threading.Thread(target=task).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = GatewaySetupApp(root)
    root.mainloop()
