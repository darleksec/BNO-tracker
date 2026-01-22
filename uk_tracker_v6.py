import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class BNOAdvancedTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("BNO Settlement & Citizenship Suite (2026) v5")
        self.root.geometry("900x850")

        # --- Initial State ---
        self.trips = []
        self.editing_index = None

        self.setup_ui()
        self.load_hardcoded_data()
        self.update_calculations()

    def setup_ui(self):
        # 1. Base Configuration (Visa & Entry Dates)
        config_frame = ttk.LabelFrame(self.root, text="Step 1: Base Residency Configuration")
        config_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(config_frame, text="Visa Approved:").grid(row=0, column=0, padx=5, pady=5)
        self.visa_entry = ttk.Entry(config_frame, width=15)
        self.visa_entry.insert(0, "07/08/2024")
        self.visa_entry.grid(row=0, column=1)

        ttk.Label(config_frame, text="UK Entry Date:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_date_field = ttk.Entry(config_frame, width=15)
        self.entry_date_field.insert(0, "07/09/2024")
        self.entry_date_field.grid(row=0, column=3)

        ttk.Button(config_frame, text="Update Base Dates", command=self.update_calculations).grid(row=0, column=4, padx=10)
        # Add this right after the "Update Base Dates" button in setup_ui:
        self.ilr_date_display = ttk.Label(config_frame, text="Earliest ILR Application: --", 
                                          font=("Arial", 10, "bold"), foreground="green")
        self.ilr_date_display.grid(row=1, column=0, columnspan=5, pady=5, sticky="w", padx=5)
        

        # 2. Trip Management
        trip_frame = ttk.LabelFrame(self.root, text="Step 2: Absence Log")
        trip_frame.pack(pady=10, padx=20, fill="x")
        
        ttk.Label(trip_frame, text="Depart:").grid(row=0, column=0, padx=5)
        self.dep_entry = ttk.Entry(trip_frame, width=12); self.dep_entry.grid(row=0, column=1)
        ttk.Label(trip_frame, text="Return:").grid(row=0, column=2, padx=5)
        self.ret_entry = ttk.Entry(trip_frame, width=12); self.ret_entry.grid(row=0, column=3)
         # Add this Checkbutton next to your "Return" entry field
        self.what_if_var = tk.BooleanVar(value=False)
        self.what_if_check = ttk.Checkbutton(trip_frame, text="What-If Trip?", variable=self.what_if_var)
        self.what_if_check.grid(row=0, column=5, padx=5)
        
        self.add_btn = ttk.Button(trip_frame, text="Add Trip", command=self.add_trip); self.add_btn.grid(row=0, column=4, padx=5)
        ttk.Button(trip_frame, text="Edit", command=self.load_edit).grid(row=0, column=6)
        ttk.Button(trip_frame, text="Delete", command=self.delete_trip).grid(row=0, column=7)
       

        # Reposition your existing Add/Edit buttons to column 5 and 6
        self.add_btn.grid(row=0, column=5, padx=5)
        # ... (adjust other buttons to grid columns 6 and 7)

        self.tree = ttk.Treeview(self.root, columns=("S", "E", "D"), show='headings', height=5)
        self.tree.heading("S", text="Departure"); self.tree.heading("E", text="Return"); self.tree.heading("D", text="Days Absent")
        self.tree.pack(pady=5, padx=20, fill="x")

        # 3. Separated Stats Dashboard
        dash = ttk.LabelFrame(self.root, text="Step 3: Residency Health Dashboard")
        dash.pack(pady=10, padx=20, fill="x")

        # ILR Section
        self.ilr_frame = ttk.Frame(dash); self.ilr_frame.pack(fill="x", padx=10, pady=5)
        self.ilr_status_lbl = ttk.Label(self.ilr_frame, text="ILR ROLLING MAX: --", font=("Arial", 10, "bold"))
        self.ilr_status_lbl.pack(side="left")
        self.ilr_left_lbl = ttk.Label(self.ilr_frame, text="| Days Remaining: --", foreground="blue")
        self.ilr_left_lbl.pack(side="left", padx=10)

        # BC Section
        self.bc_frame = ttk.Frame(dash); self.bc_frame.pack(fill="x", padx=10, pady=5)
        self.bc_status_lbl = ttk.Label(self.bc_frame, text="BC 5-YEAR TOTAL: --", font=("Arial", 10, "bold"))
        self.bc_status_lbl.pack(side="left")
        self.bc_left_lbl = ttk.Label(self.bc_frame, text="| Days Remaining: --", foreground="blue")
        self.bc_left_lbl.pack(side="left", padx=10)

        # Add this before the solve_frame in setup_ui:
        self.planner_frame = ttk.LabelFrame(self.root, text="✈️ Safe Travel Planner (Starting Tomorrow)")
        self.planner_frame.pack(pady=10, padx=20, fill="x")
        
        self.planner_summary = ttk.Label(self.planner_frame, text="Calculating...", font=("Arial", 11, "bold"), foreground="blue")
        self.planner_summary.pack(pady=5)
        
        self.allowance_details = ttk.Label(self.planner_frame, text="", font=("Arial", 9))
        self.allowance_details.pack(pady=2)

        # 4. Troubleshooting & Solutions
        self.solve_frame = ttk.LabelFrame(self.root, text="⚠️ Troubleshooting & Rule Solutions")
        self.solve_frame.pack(pady=10, padx=20, fill="both", expand=True)
        self.solve_text = tk.Text(self.solve_frame, height=8, state="disabled", background="#f9f9f9", font=("Consolas", 10))
        self.solve_text.pack(padx=10, pady=10, fill="both", expand=True)

    def update_calculations(self):
        try:
            # 1. Date Parsing & ILR Timeline
            visa_date = datetime.strptime(self.visa_entry.get(), "%d/%m/%Y")
            entry_date = datetime.strptime(self.entry_date_field.get(), "%d/%m/%Y")
            today = datetime.now()
            
            # ILR Eligibility: 5 years from Visa Approval minus 28 days
            ilr_eligible = visa_date + timedelta(days=5*365.25) - timedelta(days=28)
            # BC Eligibility: Exactly 12 months after ILR
            bc_eligible = ilr_eligible + timedelta(days=365)
            
            self.ilr_date_display.config(text=f"Earliest ILR Application: {ilr_eligible.strftime('%d/%m/%Y')}")

            # 2. Residency Calculations (Rolling & Totals)
            max_rolling = 0
            sorted_trips = sorted(self.trips, key=lambda x: x[0])
            for t in sorted_trips:
                window_start, window_end = t[0], t[0] + timedelta(days=365)
                usage = sum(max(0, (min(tr[1]-timedelta(days=1), window_end) - max(tr[0]+timedelta(days=1), window_start)).days + 1) 
                            for tr in self.trips if tr[0] < window_end and tr[1] > window_start)
                max_rolling = max(max_rolling, usage)

            bc_5yr_start = bc_eligible - timedelta(days=5*365)
            bc_final_yr_start = bc_eligible - timedelta(days=365)
            bc_total = sum(t[2] for t in self.trips if t[0] >= bc_5yr_start)
            bc_final = sum(t[2] for t in self.trips if t[0] >= bc_final_yr_start)

            # 3. Safe Travel Planner Simulation
            max_safe_days = 0
            limit_reason = "No limit within 450 days"
            
            for hypothetical_days in range(1, 451):
                temp_ret = today + timedelta(days=hypothetical_days + 1)
                temp_trips = self.trips + [(today + timedelta(days=1), temp_ret, hypothetical_days)]
                
                # Check simulation against all rules
                sim_max_r = 0
                all_sim_trips = sorted(temp_trips, key=lambda x: x[0])
                for st in all_sim_trips:
                    w_s, w_e = st[0], st[0] + timedelta(days=365)
                    sim_usage = sum(max(0, (min(tr[1]-timedelta(days=1), w_e) - max(tr[0]+timedelta(days=1), w_s)).days + 1) 
                                   for tr in temp_trips if tr[0] < w_e and tr[1] > w_s)
                    sim_max_r = max(sim_max_r, sim_usage)
                
                if sim_max_r > 180:
                    limit_reason = "ILR Rolling 180-Day Rule"
                    break
                if (bc_total + hypothetical_days) > 450:
                    limit_reason = "BC 450-Day Total Limit"
                    break
                if (bc_final + (hypothetical_days if temp_ret > bc_final_yr_start else 0)) > 90:
                    limit_reason = "BC 90-Day Final Year Limit"
                    break
                max_safe_days = hypothetical_days

            # 4. Update UI Dashboard
            self.planner_summary.config(text=f"Maximum Safe Trip: {max_safe_days} Days")
            self.allowance_details.config(text=f"Constraint: Your travel is limited by the {limit_reason}.")
            
            self.ilr_status_lbl.config(text=f"ILR ROLLING MAX: {max_rolling}/180 Days", foreground="red" if max_rolling > 180 else "black")
            self.ilr_left_lbl.config(text=f"| Allowance Remaining: {max(0, 180 - max_rolling)} Days")
            self.bc_status_lbl.config(text=f"BC 5-YEAR TOTAL: {bc_total}/450 Days", foreground="red" if bc_total > 450 else "black")
            self.bc_left_lbl.config(text=f"| Allowance Remaining: {max(0, 450 - bc_total)} Days")

            # 5. Troubleshooting Engine & Solutions
            solutions = []
            
            # Fix for ILR Rolling Breach
            if max_rolling > 180:
                solutions.append(f"🔴 ILR ROLLING BREACH ({max_rolling} days)\n"
                                 f"   SOLUTION: You have broken the 'Continuous Residence' requirement. \n"
                                 f"   You must wait for 5 'clean' years to pass from the end of your heaviest \n"
                                 f"   travel window before you can apply for ILR.")

            # Fix for BC Total Breach
            if bc_total > 450:
                solutions.append(f"🔴 CITIZENSHIP TOTAL BREACH ({bc_total} days)\n"
                                 f"   SOLUTION: You cannot apply for BC on {bc_eligible.strftime('%d/%m/%Y')}.\n"
                                 f"   Wait until your oldest absences 'fall out' of the 5-year lookback window.")

            # Fix for BC Presence (Anniversary) Rule
            presence_date = bc_eligible - timedelta(days=5*365)
            conflicting_trip = next((t for t in self.trips if t[0] <= presence_date <= t[1]), None)
            
            if conflicting_trip:
                # Calculate the first safe date to apply
                safe_presence_date = conflicting_trip[1] + timedelta(days=1)
                suggested_app_date = safe_presence_date + timedelta(days=5*365)
                solutions.append(f"🔴 BC PRESENCE RULE FAIL\n"
                                 f"   You were away on {presence_date.strftime('%d/%m/%Y')} (the 5-year anniversary).\n"
                                 f"   SOLUTION: Shift your citizenship application date to {suggested_app_date.strftime('%d/%m/%Y')}.\n"
                                 f"   On that day, 5 years prior ({safe_presence_date.strftime('%d/%m/%Y')}), you were in the UK.")

            # Final Output to Troubleshooting Box
            self.solve_text.config(state="normal")
            self.solve_text.delete("1.0", tk.END)
            if not solutions:
                self.solve_text.insert("1.0", f"✅ ALL RULES MET\n\n"
                                              f"Target ILR: {ilr_eligible.strftime('%d/%m/%Y')}\n"
                                              f"Target BC:  {bc_eligible.strftime('%d/%m/%Y')}\n\n"
                                              f"You are currently on track for settlement.")
            else:
                self.solve_text.insert("1.0", "\n\n".join(solutions))
            self.solve_text.config(state="disabled")

        except Exception as e:
            messagebox.showerror("Calc Error", f"Check date formats (DD/MM/YYYY). Error: {e}")
            
    # --- Standard UI Management Functions ---
    def add_trip(self):
        try:
            s, e = datetime.strptime(self.dep_entry.get(), "%d/%m/%Y"), datetime.strptime(self.ret_entry.get(), "%d/%m/%Y")
            d = max(0, (e - s).days - 1)
            if self.editing_index is not None: self.trips[self.editing_index] = (s, e, d); self.editing_index = None; self.add_btn.config(text="Add Trip")
            else: self.trips.append((s, e, d))
            self.refresh_tree(); self.update_calculations()
        except: messagebox.showerror("Format Error", "Use DD/MM/YYYY")

    def load_hardcoded_data(self):
        raw = [("07/08/2024", "07/09/2024"), ("28/03/2025", "03/04/2025"), ("08/04/2025", "16/04/2025"), 
               ("15/06/2025", "18/08/2025"), ("04/12/2025", "07/12/2025"), ("11/12/2025", "27/01/2026")]
        for dep, ret in raw:
            s, e = datetime.strptime(dep, "%d/%m/%Y"), datetime.strptime(ret, "%d/%m/%Y")
            self.trips.append((s, e, max(0, (e - s).days - 1)))
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in sorted(self.trips, key=lambda x: x[0]): self.tree.insert("", "end", values=(t[0].strftime("%d/%m/%Y"), t[1].strftime("%d/%m/%Y"), t[2]))

    def delete_trip(self):
        sel = self.tree.selection()
        if sel: self.trips.pop(self.tree.index(sel[0])); self.refresh_tree(); self.update_calculations()

    def load_edit(self):
        sel = self.tree.selection()
        if not sel: return
        idx = self.tree.index(sel[0]); self.editing_index = idx
        self.dep_entry.delete(0, tk.END); self.dep_entry.insert(0, self.trips[idx][0].strftime("%d/%m/%Y"))
        self.ret_entry.delete(0, tk.END); self.ret_entry.insert(0, self.trips[idx][1].strftime("%d/%m/%Y"))
        self.add_btn.config(text="Save Edit")

if __name__ == "__main__":
    root = tk.Tk(); app = BNOAdvancedTracker(root); root.mainloop()