import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import ttkbootstrap as tb 
from ttkbootstrap.constants import *

    #ttkbootstrap theme 
class BNOAdvancedTracker:
    def __init__(self, root):
        self.root = root
        self.style = tb.Style(theme="superhero")
        self.root.title("BNO Settlement & Citizenship Suite (2026) v8")
        self.root.geometry("1000x900")

        # --- Initial State ---
        # Format: (Departure, Return, Days, is_what_if)
        self.trips = []
        self.editing_index = None

        self.setup_ui()
        self.load_hardcoded_data()
        self.update_calculations()

    def setup_ui(self):
        # 1. Base Configuration (Visa & Entry Dates)
        config_frame = tb.LabelFrame(self.root, text="Step 1: Base Residency Configuration")
        config_frame.pack(pady=10, padx=20, fill="x")

        tb.Label(config_frame, text="Visa Approved:").grid(row=0, column=0, padx=5, pady=5)
        self.visa_entry = tb.Entry(config_frame, width=15)
        self.visa_entry.insert(0, "07/08/2024")
        self.visa_entry.grid(row=0, column=1)

        tb.Label(config_frame, text="UK Entry Date:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_date_field = tb.Entry(config_frame, width=15)
        self.entry_date_field.insert(0, "07/09/2024")
        self.entry_date_field.grid(row=0, column=3)

        tb.Button(config_frame, text="Update Base Dates", command=self.update_calculations).grid(row=0, column=4, padx=10)
        
        self.ilr_date_display = tb.Label(config_frame, text="Earliest ILR Application: --", 
                                          font=("Arial", 16, "bold"), foreground="red")
        self.ilr_date_display.grid(row=1, column=0, columnspan=5, pady=5, sticky="w", padx=5)

        # 2. Trip Management
        trip_frame = tb.LabelFrame(self.root, text="Step 2: Absence Log & What-If Planner")
        trip_frame.pack(pady=10, padx=20, fill="x")
        
        tb.Label(trip_frame, text="Depart:").grid(row=0, column=0, padx=5)
        self.dep_entry = tb.Entry(trip_frame, width=12); self.dep_entry.grid(row=0, column=1)
        tb.Label(trip_frame, text="Return:").grid(row=0, column=2, padx=5)
        self.ret_entry = tb.Entry(trip_frame, width=12); self.ret_entry.grid(row=0, column=3)
        
        self.what_if_var = tk.BooleanVar(value=False)
        self.what_if_check = tb.Checkbutton(trip_frame, text="What-If Trip?", variable=self.what_if_var)
        self.what_if_check.grid(row=0, column=4, padx=10)

        self.add_btn = tb.Button(trip_frame, text="Add Trip", command=self.add_trip, bootstyle="success")
        self.add_btn.grid(row=0, column=5, padx=5)
        tb.Button(trip_frame, text="Edit", command=self.load_edit, bootstyle="info-outline").grid(row=0, column=6, padx=2)
        tb.Button(trip_frame, text="Delete", command=self.delete_trip, bootstyle="danger-outline").grid(row=0, column=7, padx=2)

        self.tree = tb.Treeview(self.root, columns=("S", "E", "D", "T"), show='headings', height=6)
        self.tree.heading("S", text="Departure"); self.tree.heading("E", text="Return")
        self.tree.heading("D", text="Days Absent"); self.tree.heading("T", text="Type")
        self.tree.column("T", width=100)
        self.tree.pack(pady=5, padx=30, fill="x")
        self.tree.tag_configure('hypothetical', foreground='gray', font=('Arial', 16, 'bold'))

        style = tb.Style()
        style.configure("Treeview", rowheight=30)
        self.tree.configure(style="Treeview")

       # 3. Separated Stats Dashboard
        dash = tb.LabelFrame(self.root, text="Step 3: Residency Health Dashboard")
        dash.pack(pady=20, padx=50, fill="x") # Reduced pady from 80 to 20 to avoid cutting off the UI

        # ILR Section
        self.ilr_frame = tb.Frame(dash)
        self.ilr_frame.pack(fill="x", padx=10, pady=10)

        self.ilr_status_lbl = tb.Label(
            self.ilr_frame,
            text="ILR Rolling Max: --",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-success"
        )
        self.ilr_status_lbl.pack(side="left")

        self.ilr_left_lbl = tb.Label(self.ilr_frame, text="| Delta Impact: --", font=("Helvetica", 12), foreground="white")
        self.ilr_left_lbl.pack(side="left", padx=16)

        # BC Section
        self.bc_frame = tb.Frame(dash)
        self.bc_frame.pack(fill="x", padx=10, pady=10)

        self.bc_status_lbl = tb.Label(
            self.bc_frame, 
            text="BC 5-YEAR TOTAL: --",
            font=("Helvetica", 24, "bold"),
            bootstyle="inverse-success" 
        )
        self.bc_status_lbl.pack(side="left")

        self.bc_left_lbl = tb.Label(self.bc_frame, text="| Delta Impact: --", font=("Helvetica", 12), foreground="white")
        self.bc_left_lbl.pack(side="left", padx=10)

        # Safe Travel Planner
        self.planner_frame = tb.Labelframe(self.root, text=" Safe Travel Planner (Impact of Current Plans)", bootstyle="primary")
        self.planner_frame.pack(pady=10, padx=20, fill="x")
        self.planner_summary = tb.Label(self.planner_frame, text="Calculating...", font=("Arial", 11, "bold"), foreground="red")
        self.planner_summary.pack(pady=5)
        self.allowance_details = tb.Label(self.planner_frame, text="", font=("Arial", 9))
        self.allowance_details.pack(pady=2)

        # 4. Troubleshooting & Solutions
        self.solve_frame = tb.LabelFrame(self.root, text="Troubleshooting & Rule Solutions")
        self.solve_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.solve_text = tk.Text(self.solve_frame, height=10, state="disabled", background="#f9f9f9", font=("Consolas", 10))
        self.solve_text.pack(padx=10, pady=10, fill="both", expand=True)

    def update_calculations(self):
        try:
            # 1. Timeline Setup
            visa_date = datetime.strptime(self.visa_entry.get(), "%d/%m/%Y")
            today = datetime.now()
            ilr_eligible = visa_date + timedelta(days=5*365.25) - timedelta(days=28)
            bc_eligible = ilr_eligible + timedelta(days=365)
            self.ilr_date_display.config(text=f"Earliest ILR Application: {ilr_eligible.strftime('%d/%m/%Y')}")

            # 2. Logic for Real vs All (What-If)
            def get_stats(trip_list):
                # Rolling 180 Max
                max_r = 0
                for t in trip_list:
                    window_start, window_end = t[0], t[0] + timedelta(days=365)
                    usage = sum(max(0, (min(tr[1]-timedelta(days=1), window_end) - max(tr[0]+timedelta(days=1), window_start)).days + 1) 
                                for tr in trip_list if tr[0] < window_end and tr[1] > window_start)
                    max_r = max(max_r, usage)
                # BC Totals
                bc_5yr_start = bc_eligible - timedelta(days=5*365)
                bc_final_start = bc_eligible - timedelta(days=365)
                total_bc = sum(tr[2] for tr in trip_list if tr[0] >= bc_5yr_start)
                final_bc = sum(tr[2] for tr in trip_list if tr[0] >= bc_final_start)
                return max_r, total_bc, final_bc

            real_trips = [t for t in self.trips if not t[3]]
            real_max, real_bc_total, real_bc_final = get_stats(real_trips)
            all_max, all_bc_total, all_bc_final = get_stats(self.trips)

            # 3. Delta UI Updates
            delta_max = all_max - real_max
            delta_bc = all_bc_total - real_bc_total

            self.ilr_status_lbl.config(text=f"ILR ROLLING MAX: {all_max}/180 Days", foreground="red" if all_max > 180 else "black")
            self.ilr_left_lbl.config(text=f"| What-If Impact: +{delta_max} days")
            
            self.bc_status_lbl.config(text=f"BC 5-YEAR TOTAL: {all_bc_total}/450 Days", foreground="red" if all_bc_total > 450 else "black")
            self.bc_left_lbl.config(text=f"| What-If Impact: +{delta_bc} days")

            # 4. Safe Travel Planner (Simulation including What-If commitment)
            max_safe = 0
            limit_res = "None"
            for d in range(1, 451):
                sim_ret = today + timedelta(days=d + 1)
                sim_trips = self.trips + [(today + timedelta(days=1), sim_ret, d, False)]
                s_max, s_bc_t, s_bc_f = get_stats(sim_trips)
                
                if s_max > 180: limit_res = "ILR 180-Day Rolling Rule"; break
                if s_bc_t > 450: limit_res = "BC 450-Day Total Limit"; break
                if s_bc_f > 90: limit_res = "BC 90-Day Final Year Limit"; break
                max_safe = d

            self.planner_summary.config(text=f"Additional Safe Trip Tomorrow: {max_safe} Days", bootstyle="info")
            self.allowance_details.config(text=f"Constraint based on current plans: {limit_res}")

            # 5. Troubleshooting Logic
            solutions = []
            if all_max > 180:
                self.ilr_status_lbl.configure(bootstyle="danger")
                solutions.append(f"ILR BREACH: Rolling window exceeds 180 days.\n   SOLUTION: If this is a What-If trip, reduce its duration. If confirmed, your 5-year ILR clock may reset.")
            
            if all_bc_total > 450:
                self.bc_status_lbl.configure(bootstyle="danger")
                solutions.append(f"BC TOTAL BREACH: {all_bc_total}/450 days.\n   SOLUTION: Postpone Citizenship application until oldest trips fall out of the 5-year window.")
            else:
                self.bc_status_lbl.configure(bootstyle="success")

            # BC Presence Rule Fail
            presence_date = bc_eligible - timedelta(days=5*365)
            conflict = next((t for t in self.trips if t[0] <= presence_date <= t[1]), None)
            if conflict:
                safe_app = (conflict[1] + timedelta(days=1)) + timedelta(days=5*365)
                solutions.append(f"BC PRESENCE RULE FAIL: Away on {presence_date.strftime('%d/%m/%Y')}.\n   FIX: Apply on/after {safe_app.strftime('%d/%m/%Y')} to ensure you were in the UK 5 years prior.")

            self.solve_text.config(state="normal"); self.solve_text.delete("1.0", tk.END)
            self.solve_text.insert("1.0", "\n\n".join(solutions) if solutions else "✅ CURRENT PLANS ARE WITHIN LIMITS.\nAll residency and presence requirements are met.")
            self.solve_text.config(state="disabled")

        except Exception as e: print(f"Calc Error: {e}")

    def add_trip(self):
        try:
            s, e = datetime.strptime(self.dep_entry.get(), "%d/%m/%Y"), datetime.strptime(self.ret_entry.get(), "%d/%m/%Y")
            d = max(0, (e - s).days - 1)
            is_wi = self.what_if_var.get()
            if self.editing_index is not None: 
                self.trips[self.editing_index] = (s, e, d, is_wi)
                self.editing_index = None; self.add_btn.config(text="Add Trip")
            else: 
                self.trips.append((s, e, d, is_wi))
            self.refresh_tree(); self.update_calculations()
        except: messagebox.showerror("Format Error", "Use DD/MM/YYYY")

    def load_hardcoded_data(self):
        raw = [("07/08/2024", "07/09/2024"), ("28/03/2025", "03/04/2025"), ("08/04/2025", "16/04/2025"), 
               ("15/06/2025", "18/08/2025"), ("04/12/2025", "07/12/2025"), ("11/12/2025", "27/01/2026")]
        for dep, ret in raw:
            s, e = datetime.strptime(dep, "%d/%m/%Y"), datetime.strptime(ret, "%d/%m/%Y")
            self.trips.append((s, e, max(0, (e - s).days - 1), False))
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in sorted(self.trips, key=lambda x: x[0]):
            tag = 'hypothetical' if t[3] else ''
            t_type = "WHAT-IF" if t[3] else "CONFIRMED"
            self.tree.insert("", "end", values=(t[0].strftime("%d/%m/%Y"), t[1].strftime("%d/%m/%Y"), t[2], t_type), tags=(tag,))

    def delete_trip(self):
        sel = self.tree.selection()
        if sel:
            # Find trip in master list by matching values
            item = self.tree.item(sel[0])['values']
            for i, t in enumerate(self.trips):
                if t[0].strftime("%d/%m/%Y") == item[0]:
                    self.trips.pop(i); break
            self.refresh_tree(); self.update_calculations()

    def load_edit(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        for i, t in enumerate(self.trips):
            if t[0].strftime("%d/%m/%Y") == item[0]:
                self.editing_index = i
                self.dep_entry.delete(0, tk.END); self.dep_entry.insert(0, item[0])
                self.ret_entry.delete(0, tk.END); self.ret_entry.insert(0, item[1])
                self.what_if_var.set(True if item[3] == "WHAT-IF" else False)
                self.add_btn.config(text="Save Edit")
                break

if __name__ == "__main__":
    import ttkbootstrap as tb
    root = tb.Window(themename="superhero")
    app = BNOAdvancedTracker(root)
    root.mainloop()