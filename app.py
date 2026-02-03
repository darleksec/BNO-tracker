import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import ttkbootstrap as tb 
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from logic import Trip, LogicEngine

    #ttkbootstrap theme 
class BNOAdvancedTracker:
    def __init__(self, root):
        self.root = root
        self.engine = LogicEngine()
        self.trips = []
        self.style = tb.Style(theme="superhero")
        self.root.title("BNO Settlement & Citizenship Suite (2026) v9")
        self.root.geometry("1000x900")
        self.editing_index = None
        # --- Initial State ---
        # Format: (Departure, Return, Days, is_what_if)
        
        

        self.setup_ui()
        self.load_hardcoded_data()
        self.refresh_dashboard()

    def setup_ui(self):
        # 1. Base Configuration (Visa & Entry Dates)
        config_frame = tb.LabelFrame(self.root, text="Step 1: Base Residency Configuration")
        config_frame.pack(pady=10, padx=20, fill="x")

        tb.Label(config_frame, text="Visa Approved:").grid(row=0, column=0, padx=5, pady=5)
        self.visa_entry = DateEntry(config_frame, width=15)
        self.visa_entry.entry.delete(0, 'end')
        self.visa_entry.entry.insert(0, "07/08/2024")
        self.visa_entry.grid(row=0, column=1)

        tb.Label(config_frame, text="UK Entry Date:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_date_field = DateEntry(config_frame, width=15)
        self.entry_date_field.entry.delete(0, 'end')  
        self.entry_date_field.entry.insert(0, "07/09/2024")
        self.entry_date_field.grid(row=0, column=3)

        tb.Button(config_frame, text="Update Base Dates", command=self.refresh_dashboard).grid(row=0, column=4, padx=10)
        
        self.ilr_date_display = tb.Label(config_frame, text="Earliest ILR Application: --", 
                                          font=("Arial", 16, "bold"), foreground="red")
        self.ilr_date_display.grid(row=1, column=0, columnspan=5, pady=5, sticky="w", padx=5)

        # 2. Trip Management
        trip_frame = tb.LabelFrame(self.root, text="Step 2: Absence Log & What-If Planner")
        trip_frame.pack(pady=10, padx=20, fill="x")
        
        tb.Label(trip_frame, text="Depart:").grid(row=0, column=0, padx=5)
        self.dep_entry = tb.DateEntry(
            trip_frame, 
            width=12, 
            dateformat="%d/%m/%Y",  # Strictly force 4-digit year
            firstweekday=0          # Starts week on Monday
        )
        self.dep_entry.grid(row=0, column=1)

        # Return Date Picker
        tb.Label(trip_frame, text="Return:").grid(row=0, column=2, padx=5)
        self.ret_entry = tb.DateEntry(
            trip_frame, 
            width=12, 
            dateformat="%d/%m/%Y", 
            firstweekday=0
        )
        self.ret_entry.grid(row=0, column=3)

        self.dep_entry.entry.configure(validate=None)
        self.ret_entry.entry.configure(validate=None)
        
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

    
        pass

    def refresh_dashboard(self):
        try:
                #fetch date from logic
            ilr_date , bc_date = self.engine.getMilestoneDates(self.visa_entry.entry.get())
            if not ilr_date: return 
            self.ilr_date_display.config(text=f"Earliest ILR: {ilr_date.strftime('%d/%m/%Y')}")

            # limit_reason = self.engine.run_sim(limit_reason.get())

            real_trips = [t for t in self.trips if not t.is_what_if]
            real_max, real_bc, _ = self.engine.getStats(real_trips, bc_date)
            all_max, all_bc , _ = self.engine.getStats(self.trips, bc_date)
            max_safe, limit = self.engine.run_sim(self.trips, bc_date)

            self.apply_UI_Styles(all_max, all_bc, max_safe, limit)

           

            self.planner_summary.config(text=f"Additional Safe Trip Tomorrow: {max_safe} Days", bootstyle="info")
            self.allowance_details.config(text=f"Constraint based on current plans: {limit}")


             # 3. Delta UI Updates
            delta_max = all_max - real_max
            delta_bc = all_bc - real_bc

            self.ilr_status_lbl.config(text=f"ILR ROLLING MAX: {all_max}/180 Days", foreground="red" if all_max > 180 else "black")
            self.ilr_left_lbl.config(text=f"| What-If Impact: +{delta_max} days")
            
            self.bc_status_lbl.config(text=f"BC 5-YEAR TOTAL: {all_bc}/450 Days", foreground="red" if all_bc > 450 else "black")
            self.bc_left_lbl.config(text=f"| What-If Impact: +{delta_bc} days")


                # # 5. Troubleshooting Logic
                # solutions = []
                # if all_max > 180:
                #     self.ilr_status_lbl.configure(bootstyle="danger")
                #     solutions.append(f"ILR BREACH: Rolling window exceeds 180 days.\n   SOLUTION: If this is a What-If trip, reduce its duration. If confirmed, your 5-year ILR clock may reset.")
                
                # if all_bc_total > 450:
                #     self.bc_status_lbl.configure(bootstyle="danger")
                #     solutions.append(f"BC TOTAL BREACH: {all_bc_total}/450 days.\n   SOLUTION: Postpone Citizenship application until oldest trips fall out of the 5-year window.")
                # else:
                #     self.bc_status_lbl.configure(bootstyle="success")

                # # BC Presence Rule Fail
                # presence_date = bc_eligible - timedelta(days=5*365)
                # conflict = next((t for t in self.trips if t[0] <= presence_date <= t[1]), None)
                # if conflict:
                #     safe_app = (conflict[1] + timedelta(days=1)) + timedelta(days=5*365)
                #     solutions.append(f"BC PRESENCE RULE FAIL: Away on {presence_date.strftime('%d/%m/%Y')}.\n   FIX: Apply on/after {safe_app.strftime('%d/%m/%Y')} to ensure you were in the UK 5 years prior.")

                # self.solve_text.config(state="normal"); self.solve_text.delete("1.0", tk.END)
                # self.solve_text.insert("1.0", "\n\n".join(solutions) if solutions else "✅ CURRENT PLANS ARE WITHIN LIMITS.\nAll residency and presence requirements are met.")
                # self.solve_text.config(state="disabled")

            

            
        except Exception as e:
            print(f"Dashboard update Error: {e}")


    def apply_UI_Styles(self, all_max, all_bc, max_safe, limit):
        # ILR Styling
        self.ilr_status_lbl.config(
            text=f"ILR Rolling Max: {all_max}/180", 
            bootstyle="inverse-danger" if all_max > 180 else "inverse-success"
        )
        
        # BC Styling
        self.bc_status_lbl.config(
            text=f"BC 5-Year Total: {all_bc}/450", 
            bootstyle="inverse-danger" if all_bc > 450 else "inverse-success"
        )

        # Planner Styling
        self.planner_summary.config(
            text=f"Additional Safe Trip Tomorrow: {max_safe} Days",
            bootstyle="success" if max_safe > 30 else "warning"
        )


    def add_trip(self):
        try:
            s = self.dep_date.entry.get() 
            e = self.ret_date.entry.get()


            if end_dt <= start_dt:
                messagebox.showwarning("Logic Error", "Return date must be after departure.")
                return

            is_wi = self.what_if_var.get()
            new_trip = Trip(departure=start_dt, return_date=end_dt, is_what_if=is_wi)

            if self.editing_index is not None: 
                self.trips[self.editing_index] = new_trip
                self.editing_index = None; self.add_btn.config(text="Add Trip")
            else: 
                self.trips.append(new_trip)
            self.refresh_tree(); self.refresh_dashboard()
        except: messagebox.showerror("Format Error", "Use DD/MM/YYYY, Error: {e}")

    def load_hardcoded_data(self):
        raw = [("07/08/2024", "07/09/2024"), ("28/03/2025", "03/04/2025"), ("08/04/2025", "16/04/2025"), 
               ("15/06/2025", "18/08/2025"), ("04/12/2025", "07/12/2025"), ("11/12/2025", "27/01/2026")]

        # raw = [
        #     # 1. The "Presence Rule" Trap (Critical for BC)
        #     # Assuming you apply for BC on 10/08/2030, you MUST be in the UK on 10/08/2025.
        #     # This trip covers that date to trigger the "Presence Rule Fail" logic.
        #     ("05/08/2025", "15/08/2025"), 

        #     # 2. The "Rolling 180" Stressor (ILR Rule)
        #     # A very long trip that puts you near the limit.
        #     ("01/01/2026", "20/06/2026"), # 170 Days

        #     # 3. The "Final Year" Breach (BC Rule)
        #     # This trip happens in 2029/2030 (the final year before BC).
        #     # We'll make it 95 days to trigger the "90-day final year" breach.
        #     ("01/01/2030", "07/04/2030"), 

        #     # 4. Standard small trips to pad the 5-year total (BC 450-day rule)
        # ("10/11/2027", "20/11/2027"),
        # ("05/05/2028", "15/05/2028")
        # ]
        for dep, ret in raw:
            s, e = datetime.strptime(dep, "%d/%m/%Y"), datetime.strptime(ret, "%d/%m/%Y")
            self.trips.append(Trip(departure=s,return_date=e,is_what_if= False))
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in sorted(self.trips, key=lambda x: x.departure):
        # for t in sorted(self.trips, key=lambda x: x[0]):
            tag = 'hypothetical' if t.is_what_if else ''
            t_type = "WHAT-IF" if t.is_what_if else "CONFIRMED"
            self.tree.insert("", "end", values=(t.departure.strftime("%d/%m/%Y"), t.return_date.strftime("%d/%m/%Y"), t.daysAbsent, t_type), tags=(tag,))

    def delete_trip(self):
        sel = self.tree.selection()
        if sel:
            # Find trip in master list by matching values
            item = self.tree.item(sel[0])['values']
            for i, t in enumerate(self.trips):
                if t[0].strftime("%d/%m/%Y") == item[0]:
                    self.trips.pop(i); break
            self.refresh_tree(); self.refresh_dashboard()

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