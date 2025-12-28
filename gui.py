# gui.py - Graphical interface for WinSecureAuditor using Tkinter

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import ctypes
from scanner import Scanner
from reporter import write_enhanced_html_report
import webbrowser

class WinSecureAuditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WinSecureAuditor - CIS Scanner")
        self.root.geometry("800x600")

        # Check admin privileges
        if not self.is_admin():
            messagebox.showwarning("Warning", "Some checks require administrator privileges. Run as admin for full functionality.")

        # Variables
        self.scanner = None
        self.results = []
        self.summary = {}

        # Layout
        self.create_widgets()

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_widgets(self):
        # Professional theme
        style = ttk.Style()
        style.theme_use('clam')

        # Top frame: Scan button and Score
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10, fill=tk.X)

        self.scan_button = ttk.Button(top_frame, text="Scan System", command=self.start_scan)
        self.scan_button.pack(side=tk.LEFT, padx=10)

        self.score_label = ttk.Label(top_frame, text="Score: --%", font=("Arial", 24, "bold"))
        self.score_label.pack(side=tk.RIGHT, padx=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="indeterminate")
        self.progress.pack(fill=tk.X, padx=10, pady=5)

        # Filter
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        self.filter_var = tk.StringVar(value="All")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, values=["All", "Passed", "Failed"], state="readonly")
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.apply_filter)

        # Treeview for results
        columns = ("Status", "ID", "Title", "Description")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tooltip
        self.tooltip = tk.Label(self.root, text="", relief="solid", bg="yellow")
        self.tooltip.pack_forget()
        self.tree.bind("<Motion>", self.show_tooltip)
        self.tree.bind("<Leave>", self.hide_tooltip)

        # Bottom frame: Export buttons
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(pady=10, fill=tk.X)

        self.export_button = ttk.Button(bottom_frame, text="Export HTML Report", command=self.export_report, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=10)

    def start_scan(self):
        self.scan_button.config(state=tk.DISABLED)
        self.progress.start()
        self.tree.delete(*self.tree.get_children())  # Clear tree
        self.score_label.config(text="Score: Scanning...")

        # Execute scan in separate thread
        thread = threading.Thread(target=self.run_scan)
        thread.start()

    def run_scan(self):
        try:
            self.scanner = Scanner("./rules/windows")
            self.results = self.scanner.run_scan()
            self.summary = self.scanner.get_summary(weighted=True)  # Use weighted by default

            # Update GUI in main thread
            self.root.after(0, self.update_results)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {e}"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.scan_button.config(state=tk.NORMAL))

    def update_results(self):
        # Update score
        score_percent = self.summary.get('score_percent', 0)
        self.score_label.config(text=f"Score: {score_percent}%")

        # Populate Treeview
        self.all_results = []  # Save for filter
        for r in self.results:
            status_icon = "✅" if r.status == "PASS" else "❌"
            item = self.tree.insert("", tk.END, values=(status_icon, r.rule_id, r.title, r.description))
            self.all_results.append((item, r))

        # Apply initial filter
        self.apply_filter()

        # Enable export
        self.export_button.config(state=tk.NORMAL)

    def apply_filter(self, event=None):
        filter_value = self.filter_var.get()
        for item, r in self.all_results:
            if filter_value == "All":
                self.tree.reattach(item, "", tk.END)
            elif filter_value == "Passed" and r.status == "PASS":
                self.tree.reattach(item, "", tk.END)
            elif filter_value == "Failed" and r.status == "FAIL":
                self.tree.reattach(item, "", tk.END)
            else:
                self.tree.detach(item)

    def show_tooltip(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            bbox = self.tree.bbox(item)
            if bbox:
                x, y, _, _ = bbox
                self.tooltip.config(text="Click for details")
                self.tooltip.place(x=x + self.tree.winfo_x(), y=y + self.tree.winfo_y() + 20)
            else:
                self.hide_tooltip()
        else:
            self.hide_tooltip()

    def hide_tooltip(self, event=None):
        self.tooltip.place_forget()

    def export_report(self):
        if not self.results:
            messagebox.showwarning("Warning", "No results to export.")
            return

        # Generate HTML
        html_path = "./output/report.html"
        os.makedirs(os.path.dirname(html_path), exist_ok=True)
        write_enhanced_html_report(
            results=self.results,
            host="LocalHost",
            os_name="Windows",
            passed_count=self.summary['passed'],
            failed_count=self.summary['failed'],
            html_path=html_path,
            benchmark_name="CIS Windows 10"
        )

        # Open in browser
        webbrowser.open(f"file://{os.path.abspath(html_path)}")
        messagebox.showinfo("Export", f"Report exported to {html_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WinSecureAuditorApp(root)
    root.mainloop()