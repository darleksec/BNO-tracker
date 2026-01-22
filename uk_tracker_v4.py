import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class UKResidenceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("UK BNO Path: Safe Travel & Residency Tracker v4")
        self.root.geometry("850x850")
        
        # --- Core Dates ---
        self.visa_approval_date = datetime(2024, 8, 7)
        self.entry_date = datetime(2024, 9, 7)
        self.ilr_target_date = self.visa_approval_date + timedelta(days=5*365.25) - timedelta(days=28)
        self.bc_app_date = self.ilr_target_date + timedelta(days=365) # Approx BC date
        
        # --- Data Persistence ---
        raw_data = [
            ("07/08/2024", "07/09/2024"), ("28/03/2025", "03/04/2025"),
            ("08/04/2025", "16/04/2025"), ("15/06/2025", "18/08/2025"),
            ("04/12/2025", "07/12/2025"), ("11/12/2025", "27/01/2026")
        ]
        self.trips = []
        for dep, ret in raw_data:
            s, e = datetime.strptime(dep, "%d/%m/%Y"), datetime.strptime(ret, "%d/%m/%Y")
            self.trips.append((s, e, max(0, (e - s).days - 1)))

        self.editing_index = None
        self.setup_ui()
        self.refresh_tree()
        self.update_calculations()

    def setup_ui(self):
        # Header
        header = ttk.Frame(self.root)
        header.pack(pady=10, padx=20, fill="x")
        ttk.Label(header, text="British Citizenship & ILR Residency Tracker", font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        self.countdown_label = ttk.Label(header, text="", font=("Arial", 10, "italic"))
        self.countdown_label.grid(row=1, column=0, sticky="w")

        # Trip Input
        input_frame = ttk.LabelFrame(self.root, text="Log Trip Details")
        input_frame.pack(pady=5, padx=20, fill="x")
        self.dep_entry = ttk.Entry(input_frame, width=12); self.dep_entry.grid(row=0, column=1, padx=5)
        self.ret_entry = ttk.Entry(input_frame, width=12); self.ret_entry.grid(row=0, column=3, padx=5)
        self.add_btn = ttk.Button(input_frame, text="Add Trip", command=self.add_trip); self.add_btn.grid(row=0, column=4, padx=5)
        ttk.Button(input_frame, text="Edit", command=self.load_trip_to_edit).grid(row=0, column=5); ttk.Button(input_frame, text="Delete", command=self.delete_trip).grid(row=0, column=6)

        # Table
        self.tree = ttk.Treeview(self.root, columns=("Start", "End", "Absence"), show='headings', height=6)
        for col in ("Start", "End", "Absence"): self.tree.heading(col, text=col)
        self.tree.pack(pady=5, padx=20, fill="both")

        # --- Safe Travel Planner Dashboard ---
        self.planner_frame = ttk.LabelFrame(self.root, text="✈️ Safe Travel Planner (Starting Tomorrow)")
        self.planner_frame.pack(pady=10, padx=20, fill="x")
        
        self.planner_summary = ttk.Label(self.planner_frame, text="Calculating...", font=("Arial", 11, "bold"), foreground="blue")
        self.planner_summary.pack(pady=5)
        
        self.allowance_details = ttk.Label(self.planner_frame, text="", font=("Arial", 9))
        self.allowance_details.pack(pady=2)

        # Alerts Section
        self.alert_frame = ttk.LabelFrame(self.root, text="⚠️ Rule Violations & Status")
        self.alert_frame.pack(pady=10, padx=20, fill="x")
        self.error_display = tk.Text(self.alert_frame, height=5, state="disabled", foreground="red", background="#fff0f0")
        self.error_display.pack(padx=5, pady=5, fill="x")

    def get_days_in_window(self, start_date, end_date):
        """Helper to count full days absent within a specific date range."""
        days = 0
        for s, e, _ in self.trips:
            actual_start = max(s + timedelta(days=1), start_date)
            actual_end = min(e - timedelta(days=1), end_date)
            if actual_end >= actual_start:
                days += (actual_end - actual_start).days + 1
        return days

    def update_calculations(self):
        today = datetime.now()
        errors = []
        
        # 1. ILR Timeline
        days_to_ilr = (self.ilr_target_date - today).days
        self.countdown_label.config(text=f"Earliest ILR App: {self.ilr_target_date.strftime('%d/%m/%Y')} ({days_to_ilr} days left)")

        # 2. Current Window Usage (12 months ending today)
        current_usage = self.get_days_in_window(today - timedelta(days=365), today)
        
        # 3. BC Calculations
        bc_5yr_start = self.bc_app_date - timedelta(days=5*365)
        bc_final_yr_start = self.bc_app_date - timedelta(days=365)
        bc_total = self.get_days_in_window(bc_5yr_start, self.bc_app_date)
        bc_final = self.get_days_in_window(bc_final_yr_start, self.bc_app_date)

        # 4. Safe Travel Calculation Logic
        # How many days can you go for tomorrow?
        max_safe_days = 0
        limit_reason = ""
        
        for hypothetical_days in range(1, 451):
            temp_ret = today + timedelta(days=hypothetical_days + 1)
            # Add hypothetical trip to a temp list
            temp_trips = self.trips + [(today + timedelta(days=1), temp_ret, hypothetical_days)]
            
            # Check ILR (Rolling 180) - Must check all windows including future ones
            max_r = 0
            all_trips_sorted = sorted(temp_trips, key=lambda x: x[0])
            for i in range(len(all_trips_sorted)):
                chk_s = all_trips_sorted[i][0]
                chk_e = chk_s + timedelta(days=365)
                w_sum = 0
                for s, e, _ in all_trips_sorted:
                    overlap_s = max(s + timedelta(days=1), chk_s)
                    overlap_e = min(e - timedelta(days=1), chk_e)
                    if overlap_e >= overlap_s: w_sum += (overlap_e - overlap_s).days + 1
                max_r = max(max_r, w_sum)
            
            # Check BC Limits
            temp_bc_total = bc_total + hypothetical_days
            temp_bc_final = bc_final + hypothetical_days if temp_ret > bc_final_yr_start else bc_final
            
            if max_r > 180:
                limit_reason = "Rolling 180-Day Rule (ILR)"
                break
            if temp_bc_total > 450:
                limit_reason = "450-Day Total Limit (Citizenship)"
                break
            if temp_bc_final > 90:
                limit_reason = "90-Day Final Year Limit (Citizenship)"
                break
            
            max_safe_days = hypothetical_days

        # Update Safe Travel Planner UI
        self.planner_summary.config(text=f"Maximum Safe Trip: {max_safe_days} Days")
        detail_text = (f"Current window usage (past 12m): {current_usage} days used. ({180-current_usage} left in window ending today).\n"
                       f"Constraint: Your next trip is limited by the '{limit_reason}'.")
        self.allowance_details.config(text=detail_text)

        # 5. Presence Rule Check
        was_absent_on_bc_start = any(s <= bc_5yr_start <= e for s, e, _ in self.trips)
        if was_absent_on_bc_start: errors.append(f"❌ PRESENCE BREACH: You were away on {bc_5yr_start.strftime('%d/%m/%Y')}. Citizenship WILL be refused.")
        if bc_total > 450: errors.append(f"❌ BC TOTAL BREACH: {bc_total}/450 days used.")
        if bc_final > 90: errors.append(f"❌ BC FINAL YEAR BREACH: {bc_final}/90 days used.")

        # Update Error UI
        self.error_display.config(state="normal"); self.error_display.delete("1.0", tk.END)
        if not errors: self.error_display.insert("1.0", "✅ All criteria met."), self.error_display.config(foreground="green")
        else: self.error_display.insert("1.0", "\n".join(errors)), self.error_display.config(foreground="red")
        self.error_display.config(state="disabled")

    def refresh_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for t in sorted(self.trips, key=lambda x: x[0]):
            self.tree.insert("", "end", values=(t[0].strftime("%d/%m/%Y"), t[1].strftime("%d/%m/%Y"), t[2]))

    def add_trip(self):
        try:
            s, e = datetime.strptime(self.dep_entry.get(), "%d/%m/%Y"), datetime.strptime(self.ret_entry.get(), "%d/%m/%Y")
            d = max(0, (e - s).days - 1)
            if self.editing_index is not None: self.trips[self.editing_index] = (s, e, d); self.editing_index = None; self.add_btn.config(text="Add Trip")
            else: self.trips.append((s, e, d))
            self.refresh_tree(); self.update_calculations()
        except: messagebox.showerror("Error", "Use DD/MM/YYYY")

    def load_trip_to_edit(self):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0]); self.editing_index = idx
        self.dep_entry.delete(0, tk.END); self.dep_entry.insert(0, self.trips[idx][0].strftime("%d/%m/%Y"))
        self.ret_entry.delete(0, tk.END); self.ret_entry.insert(0, self.trips[idx][1].strftime("%d/%m/%Y"))
        self.add_btn.config(text="Save Edit")

    def delete_trip(self):
        selected = self.tree.selection()
        if selected and messagebox.askyesno("Confirm", "Delete?"):
            self.trips.pop(self.tree.index(selected[0]))
            self.refresh_tree(); self.update_calculations()

if __name__ == "__main__":
    root = tk.Tk(); app = UKResidenceTracker(root); root.mainloop()