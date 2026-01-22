import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class UKResidenceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("BNO Residency Tracker v3 (2024-2029)")
        self.root.geometry("800x700")
        
        # Hardcoded Entry & Visa Data
        self.visa_approval_date = datetime(2024, 8, 7)
        self.entry_date = datetime(2024, 9, 7)
        self.ilr_target_date = self.visa_approval_date + timedelta(days=5*365.25) - timedelta(days=28)
        
        # Hardcoded Trips from your provided list
        raw_data = [
            ("07/08/2024", "07/09/2024"), # Delay to entry
            ("28/03/2025", "03/04/2025"),
            ("08/04/2025", "16/04/2025"),
            ("15/06/2025", "18/08/2025"),
            ("04/12/2025", "07/12/2025"),
            ("11/12/2025", "27/01/2026")
        ]

        self.trips = []
        for dep_str, ret_str in raw_data:
            start = datetime.strptime(dep_str, "%d/%m/%Y")
            end = datetime.strptime(ret_str, "%d/%m/%Y")
            days_absent = max(0, (end - start).days - 1)
            self.trips.append((start, end, days_absent))

        self.editing_index = None
        self.setup_ui()
        self.refresh_tree()
        self.update_calculations()

    def setup_ui(self):
        # Header & Key Dates
        header = ttk.Frame(self.root)
        header.pack(pady=10, padx=20, fill="x")
        ttk.Label(header, text="BNO Path to Settlement", font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w")
        
        dates_info = f"Visa Approved: {self.visa_approval_date.strftime('%d/%m/%Y')} | Entry: {self.entry_date.strftime('%d/%m/%Y')}"
        ttk.Label(header, text=dates_info).grid(row=1, column=0, sticky="w")
        
        self.countdown_label = ttk.Label(header, text="", font=("Arial", 10, "italic"), foreground="blue")
        self.countdown_label.grid(row=2, column=0, sticky="w")

        # Input Area
        input_frame = ttk.LabelFrame(self.root, text="Trip Management")
        input_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(input_frame, text="Dep (DD/MM/YYYY):").grid(row=0, column=0, padx=5, pady=5)
        self.dep_entry = ttk.Entry(input_frame, width=12)
        self.dep_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Ret (DD/MM/YYYY):").grid(row=0, column=2, padx=5, pady=5)
        self.ret_entry = ttk.Entry(input_frame, width=12)
        self.ret_entry.grid(row=0, column=3)

        self.add_btn = ttk.Button(input_frame, text="Add Trip", command=self.add_trip)
        self.add_btn.grid(row=0, column=4, padx=5)
        ttk.Button(input_frame, text="Edit Selected", command=self.load_trip_to_edit).grid(row=0, column=5, padx=5)
        ttk.Button(input_frame, text="Delete", command=self.delete_trip).grid(row=0, column=6, padx=5)

        # Trip Table
        self.tree = ttk.Treeview(self.root, columns=("Start", "End", "Absence"), show='headings', height=10)
        self.tree.heading("Start", text="Left UK")
        self.tree.heading("End", text="Returned")
        self.tree.heading("Absence", text="Full Days Absent")
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Dashboard
        self.status_frame = ttk.LabelFrame(self.root, text="Live Dashboard")
        self.status_frame.pack(pady=10, padx=20, fill="x")
        
        self.rolling_label = ttk.Label(self.status_frame, text="Current Rolling 12-Month Window: --", font=("Arial", 10, "bold"))
        self.rolling_label.pack(anchor="w", padx=10, pady=2)
        
        self.ilr_label = ttk.Label(self.status_frame, text="ILR Rolling Max (180 limit): 0 days")
        self.ilr_label.pack(anchor="w", padx=10)
        
        self.bc_total_label = ttk.Label(self.status_frame, text="BC Total Absences (450 limit): 0 days")
        self.bc_total_label.pack(anchor="w", padx=10)

        # Add this at the bottom of setup_ui
        self.alert_frame = ttk.LabelFrame(self.root, text="⚠️ Rule Violations & Eligibility Alerts")
        self.alert_frame.pack(pady=10, padx=20, fill="x")
        
        self.error_display = tk.Text(self.alert_frame, height=5, state="disabled", 
                                     font=("Arial", 10), foreground="red", background="#fff0f0")
        self.error_display.pack(padx=5, pady=5, fill="x")

    def update_calculations(self):
        today = datetime.now()
        errors = []
        
        # --- 1. ILR TIMELINE ---
        days_to_ilr = (self.ilr_target_date - today).days
        self.countdown_label.config(text=f"Earliest ILR Application: {self.ilr_target_date.strftime('%d/%m/%Y')} ({days_to_ilr} days left)")

        # --- 2. BC TIMELINE (Approx 1 year after ILR) ---
        bc_app_date = self.ilr_target_date + timedelta(days=365)
        bc_final_year_start = bc_app_date - timedelta(days=365)
        bc_qualifying_start = bc_app_date - timedelta(days=5*365) # 5 years before BC app

        # --- 3. ILR ROLLING 180 CHECK ---
        max_rolling = 0
        if self.trips:
            sorted_trips = sorted(self.trips, key=lambda x: x[0])
            for i in range(len(sorted_trips)):
                chk_start = sorted_trips[i][0]
                chk_end = chk_start + timedelta(days=365)
                window_sum = 0
                for start, end, days in sorted_trips:
                    overlap_start = max(start + timedelta(days=1), chk_start)
                    overlap_end = min(end - timedelta(days=1), chk_end)
                    if overlap_end >= overlap_start:
                        window_sum += (overlap_end - overlap_start).days + 1
                max_rolling = max(max_rolling, window_sum)

        if max_rolling > 180:
            errors.append(f"❌ ILR BREACH: You exceeded 180 days ({max_rolling}) in a rolling 12-month period.")

        # --- 4. BC 450-DAY TOTAL CHECK ---
        # Note: BC 5-year window counts back from application date
        bc_total_absent = 0
        for start, end, days in self.trips:
            if end > bc_qualifying_start:
                # Count days only within the 5 years before citizenship application
                actual_start = max(start + timedelta(days=1), bc_qualifying_start)
                actual_end = end - timedelta(days=1)
                if actual_end >= actual_start:
                    bc_total_absent += (actual_end - actual_start).days + 1
        
        if bc_total_absent > 450:
            errors.append(f"❌ BC TOTAL BREACH: Total absences ({bc_total_absent} days) exceed the 450-day 5-year limit.")

        # --- 5. BC 90-DAY FINAL YEAR CHECK ---
        bc_final_year_absent = 0
        for start, end, days in self.trips:
            if end > bc_final_year_start:
                actual_start = max(start + timedelta(days=1), bc_final_year_start)
                actual_end = min(end - timedelta(days=1), bc_app_date)
                if actual_end >= actual_start:
                    bc_final_year_absent += (actual_end - actual_start).days + 1
        
        if bc_final_year_absent > 90:
            errors.append(f"❌ BC FINAL YEAR BREACH: You have {bc_final_year_absent} days away in the final 12 months (Limit: 90).")

        # --- 6. BC 5-YEAR PRESENCE RULE ---
        # You MUST be physically in the UK exactly 5 years before the day the Home Office receives your app.
        was_absent_on_start_date = False
        for start, end, days in self.trips:
            if start <= bc_qualifying_start <= end:
                was_absent_on_start_date = True
                break
        
        if was_absent_on_start_date:
            errors.append(f"❌ BC PRESENCE RULE: You were outside the UK on {bc_qualifying_start.strftime('%d/%m/%Y')}. This will cause an automatic BC refusal.")

        # Update Labels
        self.ilr_label.config(text=f"ILR Rolling Max: {max_rolling} days", foreground="red" if max_rolling > 180 else "green")
        self.bc_total_label.config(text=f"BC 5-Year Total: {bc_total_absent} days (Final Year: {bc_final_year_absent}) ({max(0, 450-bc_total_absent)} left)")

        # Update Error Display
        self.error_display.config(state="normal")
        self.error_display.delete("1.0", tk.END)
        if not errors:
            self.error_display.insert("1.0", "✅ All rules currently met based on entered dates.")
            self.error_display.config(foreground="green")
        else:
            self.error_display.insert("1.0", "\n".join(errors))
            self.error_display.config(foreground="red")
        self.error_display.config(state="disabled")
        
    def add_trip(self):
        try:
            start = datetime.strptime(self.dep_entry.get(), "%d/%m/%Y")
            end = datetime.strptime(self.ret_entry.get(), "%d/%m/%Y")
            days_absent = max(0, (end - start).days - 1)
            if self.editing_index is not None:
                self.trips[self.editing_index] = (start, end, days_absent)
                self.editing_index = None
                self.add_btn.config(text="Add Trip")
            else:
                self.trips.append((start, end, days_absent))
            self.refresh_tree()
            self.update_calculations()
        except: messagebox.showerror("Error", "Use DD/MM/YYYY")

    def load_trip_to_edit(self):
        selected = self.tree.selection()
        if not selected: return
        idx = self.tree.index(selected[0])
        self.dep_entry.delete(0, tk.END); self.dep_entry.insert(0, self.trips[idx][0].strftime("%d/%m/%Y"))
        self.ret_entry.delete(0, tk.END); self.ret_entry.insert(0, self.trips[idx][1].strftime("%d/%m/%Y"))
        self.editing_index = idx; self.add_btn.config(text="Save Edit")

    def delete_trip(self):
        selected = self.tree.selection()
        if selected and messagebox.askyesno("Confirm", "Delete trip?"):
            self.trips.pop(self.tree.index(selected[0]))
            self.refresh_tree(); self.update_calculations()

    def refresh_tree(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for t in sorted(self.trips, key=lambda x: x[0]):
            self.tree.insert("", "end", values=(t[0].strftime("%d/%m/%Y"), t[1].strftime("%d/%m/%Y"), t[2]))

if __name__ == "__main__":
    root = tk.Tk(); app = UKResidenceTracker(root); root.mainloop()