import time
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
from pynput import keyboard, mouse
import win32gui
import psutil  # for system stats

class ActivityMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Activity Monitor")
        self.root.geometry("900x540")  # wider to fit left panel
        self.root.resizable(False, False)

        self.theme = "light"
        self.colors = {
            "light": {
                "bg": "#ffffff",
                "fg": "#000000",
                "highlight": "#2a7ae2",
                "log_bg": "#f4f4f4",
                "log_fg": "#000000",
                "status_bg": "#e0e0e0",
                "status_fg": "#000000"
            },
            "dark": {
                "bg": "#1e1e1e",
                "fg": "#ffffff",
                "highlight": "#58a6ff",
                "log_bg": "#2b2b2b",
                "log_fg": "#f1f1f1",
                "status_bg": "#2a2a2a",
                "status_fg": "#ffffff"
            }
        }

        self.root.configure(bg=self.colors[self.theme]["bg"])

        # Main frame holds left panel and right panel side by side
        self.main_frame = tk.Frame(root, bg=self.colors[self.theme]["bg"])
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left panel for system stats
        self.left_panel = tk.Frame(self.main_frame, width=200, bg=self.colors[self.theme]["bg"])
        self.left_panel.pack(side='left', fill='y', padx=(0,10))

        left_title = tk.Label(self.left_panel, text="System Status", font=("Segoe UI", 14, "bold"),
                              bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        left_title.pack(pady=(0,15))

        self.cpu_label = tk.Label(self.left_panel, text="CPU: --%", font=("Segoe UI", 12),
                                  bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.cpu_label.pack(anchor='w', pady=2)

        self.memory_label = tk.Label(self.left_panel, text="Memory: --%", font=("Segoe UI", 12),
                                     bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.memory_label.pack(anchor='w', pady=2)

        self.disk_label = tk.Label(self.left_panel, text="Disk: --%", font=("Segoe UI", 12),
                                   bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.disk_label.pack(anchor='w', pady=2)

        self.network_label = tk.Label(self.left_panel, text="Network: -- Mbps", font=("Segoe UI", 12),
                                      bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.network_label.pack(anchor='w', pady=2)

        # Right panel holds the existing UI elements
        self.right_panel = tk.Frame(self.main_frame, bg=self.colors[self.theme]["bg"])
        self.right_panel.pack(side='left', fill='both', expand=True)

        self.window_label = tk.Label(self.right_panel, text="Active Window:", font=("Segoe UI", 12, "bold"),
                                     bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.window_label.pack(pady=(10, 0))

        self.window_title = tk.Label(self.right_panel, text="Waiting for activity...", font=("Segoe UI", 11),
                                     fg=self.colors[self.theme]["highlight"], bg=self.colors[self.theme]["bg"])
        self.window_title.pack(pady=(0, 10))

        self.log_area = ScrolledText(self.right_panel, state='disabled', height=22, font=("Consolas", 10),
                                     bg=self.colors[self.theme]["log_bg"], fg=self.colors[self.theme]["log_fg"])
        self.log_area.pack(padx=15, pady=5, fill='both', expand=True)

        btn_frame = tk.Frame(self.right_panel, bg=self.colors[self.theme]["bg"])
        btn_frame.pack(pady=10)

        self.save_btn = tk.Button(btn_frame, text="Save Logs", command=self.save_logs, bg="#4caf50", fg="white",
                                  font=("Segoe UI", 10, "bold"), width=12)
        self.save_btn.pack(side="left", padx=5)

        self.clear_btn = tk.Button(btn_frame, text="Clear Logs", command=self.clear_logs, bg="#f39c12", fg="white",
                                   font=("Segoe UI", 10, "bold"), width=12)
        self.clear_btn.pack(side="left", padx=5)

        self.pause_btn = tk.Button(btn_frame, text="Pause Monitoring", command=self.toggle_pause, bg="#ff9800", fg="white",
                                   font=("Segoe UI", 10, "bold"), width=15)
        self.pause_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Stop Monitoring & Exit", command=self.stop, bg="#e03c3c", fg="white",
                                  font=("Segoe UI", 10, "bold"), width=18)
        self.stop_btn.pack(side="left", padx=5)

        self.theme_btn = tk.Button(btn_frame, text="Dark/Light", command=self.toggle_theme, bg="#607d8b", fg="white",
                                   font=("Segoe UI", 10, "bold"), width=12)
        self.theme_btn.pack(side="left", padx=5)

        self.status_var = tk.StringVar(value="Monitoring active")
        self.status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W,
                                   font=("Segoe UI", 9), bg=self.colors[self.theme]["status_bg"],
                                   fg=self.colors[self.theme]["status_fg"])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.footer = tk.Label(root, text="Made by Amir Hamza", font=("Segoe UI", 9, "italic"),
                               bg=self.colors[self.theme]["bg"], fg=self.colors[self.theme]["fg"])
        self.footer.pack(side=tk.BOTTOM, pady=(2, 4))

        self.monitoring = True
        self.paused = False
        self.last_window_title = ""

        self.start_time = None
        self.elapsed_before_pause = 0
        self.timer_running = False

        self.prev_net_io = psutil.net_io_counters()
        self.prev_time = time.time()

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)

        self.start_monitoring()
        self.update_system_stats()  # start system stats updating

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        c = self.colors[self.theme]
        self.root.configure(bg=c["bg"])
        self.window_label.configure(bg=c["bg"], fg=c["fg"])
        self.window_title.configure(bg=c["bg"], fg=c["highlight"])
        self.log_area.configure(bg=c["log_bg"], fg=c["log_fg"])
        self.status_bar.configure(bg=c["status_bg"], fg=c["status_fg"])
        self.footer.configure(bg=c["bg"], fg=c["fg"])
        self.left_panel.configure(bg=c["bg"])
        self.right_panel.configure(bg=c["bg"])
        for widget in self.left_panel.winfo_children():
            widget.configure(bg=c["bg"], fg=c["fg"])
        for widget in self.right_panel.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=c["bg"])
            else:
                widget.configure(bg=c["bg"], fg=c.get("fg", "black"))

    def start_monitoring(self):
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()
        threading.Thread(target=self.monitor_active_window, daemon=True).start()
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def update_timer(self):
        if self.timer_running and not self.paused:
            elapsed = int(time.time() - self.start_time + self.elapsed_before_pause)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.status_var.set(f"Monitoring active - Elapsed: {time_str}")
            self.root.after(1000, self.update_timer)
        elif self.paused:
            elapsed = int(self.elapsed_before_pause)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            self.status_var.set(f"Monitoring paused - Elapsed: {time_str}")

    def toggle_pause(self):
        if not self.paused:
            self.paused = True
            self.timer_running = False
            self.elapsed_before_pause += time.time() - self.start_time
            self.pause_btn.config(text="Resume Monitoring", bg="#4caf50")
            self.status_var.set(f"Monitoring paused - Elapsed: {self.status_var.get().split()[-1]}")
        else:
            self.paused = False
            self.timer_running = True
            self.start_time = time.time()
            self.pause_btn.config(text="Pause Monitoring", bg="#ff9800")
            self.update_timer()

    def update_system_stats(self):
        # Update CPU
        cpu = psutil.cpu_percent(interval=None)
        self.cpu_label.config(text=f"CPU: {cpu}%")

        # Update Memory
        mem = psutil.virtual_memory()
        self.memory_label.config(text=f"Memory: {mem.percent}%")

        # Update Disk usage (root partition)
        disk = psutil.disk_usage('/')
        self.disk_label.config(text=f"Disk: {disk.percent}%")

        # Update Network speed (Mbps)
        current_net_io = psutil.net_io_counters()
        current_time = time.time()
        time_diff = current_time - self.prev_time

        if time_diff > 0:
            bytes_sent = current_net_io.bytes_sent - self.prev_net_io.bytes_sent
            bytes_recv = current_net_io.bytes_recv - self.prev_net_io.bytes_recv
            total_bytes = bytes_sent + bytes_recv
            mbps = (total_bytes * 8) / (time_diff * 1024 * 1024)  # Convert to Mbps

            self.network_label.config(text=f"Network: {mbps:.2f} Mbps")

            self.prev_net_io = current_net_io
            self.prev_time = current_time

        # Schedule next update
        self.root.after(1000, self.update_system_stats)

    def log(self, message):
        def append():
            self.log_area.config(state='normal')
            self.log_area.insert('end', message + "\n")
            self.log_area.see('end')
            self.log_area.config(state='disabled')
        self.root.after(0, append)

    def get_active_window_title(self):
        hwnd = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(hwnd)

    def monitor_active_window(self):
        while self.monitoring:
            if not self.paused:
                title = self.get_active_window_title()
                if title != self.last_window_title:
                    self.last_window_title = title
                    self.root.after(0, lambda: self.window_title.config(text=title))
                    self.log(f"[Window Changed] {title}")
            time.sleep(1.5)

    def on_key_press(self, key):
        if not self.paused:
            try:
                self.log(f"[Key Pressed] {key.char}")
            except AttributeError:
                self.log(f"[Special Key] {key}")

    def on_key_release(self, key):
        if key == keyboard.Key.esc:
            self.stop()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed and not self.paused:
            self.log(f"[Mouse Click] at ({x}, {y}) with {button}")

    def save_logs(self):
        logs = self.log_area.get('1.0', 'end-1c')
        if not logs.strip():
            messagebox.showinfo("Save Logs", "No logs to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(logs)
                messagebox.showinfo("Save Logs", f"Logs saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Save Logs", f"Error saving logs:\n{e}")

    def clear_logs(self):
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?"):
            self.log_area.config(state='normal')
            self.log_area.delete('1.0', 'end')
            self.log_area.config(state='disabled')

    def stop(self):
        if messagebox.askyesno("Exit", "Stop monitoring and exit the application?"):
            self.monitoring = False
            self.timer_running = False
            self.keyboard_listener.stop()
            self.mouse_listener.stop()
            self.status_var.set("Monitoring stopped")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = ActivityMonitorApp(root)
    root.mainloop()
