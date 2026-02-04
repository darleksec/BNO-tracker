"""
Project: BNO Settlement & Citizenship Tracker
Author: Kimi Tang
Date: February 2026
License: MIT
Description: A tool to automate UK residency and absence compliance checks.
"""

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import ttkbootstrap as tb 
from ttkbootstrap.widgets import DateEntry
from logic import Trip, LogicEngine
import json

class BNOAdvancedTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("BNO Settlement & Citizenship Suite (2026) ")
        self.root.geometry("1000x1200")
        
        #construtors
        self.engine = LogicEngine()
        self.trips = []
        self.style = tb.Style()
        self.editing_index = None

        #view options
        self.font_scale = 1.0  # 1.0 = 100% zoom
        self.base_font_family = "Segoe UI"

        #func
        self.setup_ui()
    #   self.load_hardcoded_data()
        self.refresh_dashboard()
        self.load_data()

    def setup_ui(self):
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        #  View Menu
        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        
        # Add Zoom commands with keyboard shortcuts
        self.view_menu.add_command(label="Zoom In (+)", command=self.zoom_in, accelerator="Ctrl++")
        self.view_menu.add_command(label="Zoom Out (-)", command=self.zoom_out, accelerator="Ctrl+-")
        self.view_menu.add_separator()
        self.view_menu.add_command(label="Reset Zoom", command=self.reset_zoom, accelerator="Ctrl+0")

        #Zoom bindings
        self.root.bind("<Control-equal>", self.zoom_in)  
        self.root.bind("<Control-plus>", self.zoom_in)  
        self.root.bind("<Control-minus>", self.zoom_out) 
        self.root.bind("<Control-0>", self.reset_zoom)   

        #  "Help" menu
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)
        
        # --- 1. CONFIGURATION FRAME ---
        config_frame = tb.Labelframe(self.root, text="Step 1: Base Residency Configuration", padding=10)
        config_frame.pack(pady=10, padx=20, fill="x")

        tb.Label(config_frame, text="Visa Approved:").grid(row=0, column=0, padx=5)
        self.visa_entry = DateEntry(config_frame, width=15, dateformat="%d/%m/%Y")
        self.visa_entry.entry.delete(0, 'end'); self.visa_entry.entry.insert(0, "07/08/2024")
        self.visa_entry.grid(row=0, column=1)

        tb.Label(config_frame, text="UK Entry Date:").grid(row=0, column=2, padx=5)
        self.entry_date_field = DateEntry(config_frame, width=15, dateformat="%d/%m/%Y")
        self.entry_date_field.entry.delete(0, 'end'); self.entry_date_field.entry.insert(0, "07/09/2024")
        self.entry_date_field.grid(row=0, column=3)

        tb.Button(config_frame, text="Update Milestones", command=self.refresh_dashboard, bootstyle="outline-primary").grid(row=0, column=4, padx=10)
        
        self.ilr_date_display = tb.Label(config_frame, text="Earliest ILR: --", font=("Arial", 14, "bold"))
        self.ilr_date_display.grid(row=1, column=0, columnspan=5, pady=10, sticky="w")

        # --- 2. LOGGING FRAME ---
        trip_frame = tb.Labelframe(self.root, text="Step 2: Absence Log & What-If Planner", padding=10)
        trip_frame.pack(pady=10, padx=20, fill="x")
        
        self.dep_entry = DateEntry(trip_frame, width=12, dateformat="%d/%m/%Y")
        self.dep_entry.grid(row=0, column=1, padx=5)
        self.ret_entry = DateEntry(trip_frame, width=12, dateformat="%d/%m/%Y")
        self.ret_entry.grid(row=0, column=3, padx=5)

        self.what_if_var = tk.BooleanVar(value=False)
        tb.Checkbutton(trip_frame, text="What-If?", variable=self.what_if_var).grid(row=0, column=4, padx=5)

        self.add_btn = tb.Button(trip_frame, text="Add Trip", command=self.add_trip, bootstyle="success")
        self.add_btn.grid(row=0, column=5, padx=5)
        tb.Button(trip_frame, text="Edit", command=self.load_edit, bootstyle="info-outline").grid(row=0, column=6, padx=2)
        tb.Button(trip_frame, text="Delete", command=self.delete_trip, bootstyle="danger-outline").grid(row=0, column=7, padx=2)

        self.tree = tb.Treeview(self.root, columns=("S", "E", "D", "T"), show='headings', height=10)
        for col, head in zip(("S", "E", "D", "T"), ("Departure", "Return", "Days", "Type")):
            self.tree.heading(col, text=head, anchor = "center")
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(pady=0, padx=20, fill="x")
        self.tree.tag_configure('hypothetical', foreground='orange')
        self.style.configure(
            "Treeview",
            borderwidth=5,
            relief="solid",
            font=("Segoe UI", 11),       # Set the row font
            rowheight=35,                
            fieldbackground="#2b3e50"
        )


        # --- 3. DASHBOARD FRAME ---
        dash = tb.Labelframe(self.root, text="Step 3: Residency Health Dashboard", padding=15)
        dash.pack(pady=10, padx=20, fill="x")

        self.ilr_status_lbl = tb.Label(dash, text="ILR MAX: --", font=("Helvetica", 20, "bold"))
        self.ilr_status_lbl.pack(anchor="w")
        self.ilr_left_lbl = tb.Label(dash, text="Impact: --")
        self.ilr_left_lbl.pack(anchor="w", padx=10)

        self.bc_status_lbl = tb.Label(dash, text="BC TOTAL: --", font=("Helvetica", 20, "bold"))
        self.bc_status_lbl.pack(anchor="w", pady=(10,0))
        self.bc_left_lbl = tb.Label(dash, text="Impact: --")
        self.bc_left_lbl.pack(anchor="w", padx=10)

        # --- 4. PLANNER & TROUBLESHOOT ---
        planner = tb.Labelframe(self.root, text="Safe Travel Planner", padding=20)
        planner.pack(pady=10, padx=20, fill="x")
        self.planner_summary = tb.Label(planner, text="Calculating...", font=("Arial", 28, "bold"))
        self.planner_summary.pack()
        self.allowance_details = tb.Label(planner, text="",font=("Arial", 22, "bold"))
        self.allowance_details.pack()

        solve = tb.Labelframe(self.root, text="Troubleshooting & Solutions", padding=10)
        solve.pack(pady=10, padx=20, fill="both", expand=True)
        self.solve_text = tb.Label(solve, text="", wraplength=800, justify="left", font=("Consolas", 24))
        self.solve_text.pack(fill="both")

        #save/load btn
        btn_frame = tb.Frame(config_frame)
        btn_frame.grid(row=0, column=7, padx=20)

        tb.Button(btn_frame, text="💾 Save", command=self.save_data, 
                bootstyle="info", width=8).pack(side="left", padx=2)
        tb.Button(btn_frame, text="📂 Load", command=self.load_data, 
                bootstyle="info-outline", width=8).pack(side="left", padx=2)

    def refresh_dashboard(self):
        """Controller: Orchestrates data flow between Logic and UI."""
        try:
            # 1. Logic Processing
            visa_str = self.visa_entry.entry.get()
            ilr_date, bc_date = self.engine.getMilestoneDates(visa_str)
            if not ilr_date: return 

            real_trips = [t for t in self.trips if not t.is_what_if]
            real_max, real_bc, _ = self.engine.getStats(real_trips, bc_date)
            all_max, all_bc, _ = self.engine.getStats(self.trips, bc_date)
            max_safe, limit = self.engine.run_sim(self.trips, bc_date)
            advice = self.engine.get_troubleshooting_advice(all_max, all_bc, bc_date, self.trips)

            # 2. UI Updates
            self.ilr_date_display.config(text=f"Earliest ILR Application: {ilr_date.strftime('%d/%m/%Y')}")
            self.ilr_left_lbl.config(text=f"What-If Impact: +{all_max - real_max} days")
            self.bc_left_lbl.config(text=f"What-If Impact: +{all_bc - real_bc} days")
            
            self.apply_UI_Styles(all_max, all_bc, max_safe, limit, advice)
        except Exception as e:
            print(f"Dashboard Error: {e}")

    def apply_UI_Styles(self, all_max, all_bc, max_safe, limit, solutions):
        """View: Handles the visual representation of data (Traffic Lights)."""
        # ILR Styling
        self.ilr_status_lbl.config(
            text=f"ILR ROLLING MAX: {all_max}/180 Days", 
            bootstyle="inverse-danger" if all_max > 180 else "inverse-success"
        )
        
        # BC Styling
        self.bc_status_lbl.config(
            text=f"BC 5-YEAR TOTAL: {all_bc}/450 Days", 
            bootstyle="inverse-danger" if all_bc > 450 else "inverse-success"
        )

        # Planner Styling
        self.planner_summary.config(
            text=f"Additional Safe Trip Tomorrow: {max_safe} Days",
            bootstyle="success" if max_safe > 14 else "warning"
        )
        self.allowance_details.config(text=f"Constraint: {limit}")

        # Troubleshooting Styling
        display_solutions = solutions if solutions else "CURRENT PLANS ARE WITHIN RESIDENCY LIMITS."
        style = "success"
        if "BREACH" in display_solutions or "FAIL" in display_solutions: style = "danger"
        elif "⚠️" in display_solutions: style = "warning"
        
        self.solve_text.config(text=display_solutions, bootstyle=style)

    def add_trip(self):
        """Input Handler: Sanitizes date strings and creates Trip objects."""
        raw_s, raw_e = self.dep_entry.entry.get().strip(), self.ret_entry.entry.get().strip()
        
        def parse(d):
            for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                try: return datetime.strptime(d, fmt)
                except: continue
            return None

        s_dt, e_dt = parse(raw_s), parse(raw_e)
        if not s_dt or not e_dt or e_dt <= s_dt:
            messagebox.showerror("Input Error", "Check date format (DD/MM/YYYY) and ensure Return > Departure")
            return


            #---CONFLICT CHECK ---
        for i, existing_trip in enumerate(self.trips):
            # Skip checking the trip against itself if we are currently editing it
            if self.editing_index is not None and i == self.editing_index:
                continue
                
            # Overlap Logic: StartA < EndB AND StartB < EndA
            # < allows for adjoining trips 
            if s_dt < existing_trip.return_date and existing_trip.departure < e_dt:
                trip_type = "What-If" if existing_trip.is_what_if else "Confirmed"
                messagebox.showerror(
                    "Date Conflict", 
                    f"This trip overlaps with an existing {trip_type} trip:\n"
                    f"{existing_trip.departure.strftime('%d/%m/%Y')} to "
                    f"{existing_trip.return_date.strftime('%d/%m/%Y')}"
                )
                return # Stop the function here
        
        new_trip = Trip(departure=s_dt, return_date=e_dt, is_what_if=self.what_if_var.get())
        
        if self.editing_index is not None:
            self.trips[self.editing_index] = new_trip
            self.editing_index = None
            self.add_btn.config(text="Add Trip")
        else:
            self.trips.append(new_trip)

        self.refresh_tree(); self.refresh_dashboard()
        self.dep_entry.entry.delete(0, 'end'); self.ret_entry.entry.delete(0, 'end')

    def load_hardcoded_data(self):
        """Initializes with user data."""
        raw = [("07/08/2024", "07/09/2024"), ("28/03/2025", "03/04/2025"), ("08/04/2025", "16/04/2025"), 
                ("15/06/2025", "18/08/2025"), ("04/12/2025", "07/12/2025"), ("11/12/2025", "27/01/2026")]

        for dep, ret in raw:
            s, e = datetime.strptime(dep, "%d/%m/%Y"), datetime.strptime(ret, "%d/%m/%Y")
            self.trips.append(Trip(departure=s, return_date=e))
        self.refresh_tree()

    def refresh_tree(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        for t in sorted(self.trips, key=lambda x: x.departure):
            self.tree.insert("", "end", values=(
                t.departure.strftime("%d/%m/%Y"), 
                t.return_date.strftime("%d/%m/%Y"),
                t.daysAbsent,
                "WHAT-IF" if t.is_what_if else "CONFIRMED"
            ), tags=('hypothetical',) if t.is_what_if else ())

    def delete_trip(self):
        sel = self.tree.selection()
        if sel:
            item = self.tree.item(sel[0])['values']
            self.trips = [t for t in self.trips if t.departure.strftime("%d/%m/%Y") != item[0]]
            self.refresh_tree(); self.refresh_dashboard()

    def load_edit(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        for i, t in enumerate(self.trips):
            if t.departure.strftime("%d/%m/%Y") == item[0]:
                self.editing_index = i
                self.dep_entry.entry.delete(0, 'end'); self.dep_entry.entry.insert(0, item[0])
                self.ret_entry.entry.delete(0, 'end'); self.ret_entry.entry.insert(0, item[1])
                self.what_if_var.set(t.is_what_if)
                self.add_btn.config(text="Save Edit")
                break

    def save_data(self, filename="trips_data.json"):
        #Serialise

        try:
            #Trip obj to dict (datetime -> str)
            data_to_save = []
            for t in self.trips:
                data_to_save.append({
                    "departure": t.departure.isoformat(),
                    "return_date": t.return_date.isoformat(),
                    "is_what_if": t.is_what_if
                })

            with open(filename, "w") as f:
                json.dump(data_to_save,f , indent=4)

                messagebox.showinfo("Save success:" , f"Data saved to {filename}")

        except Exception as e:
            messagebox.showerror("Save Error:", f"Could not save to {filename}")

    def load_data(self, filename="trips_data.json"):
        try:
            with open(filename, "r") as f:

                raw_data = json.load(f)

            self.trips = [] # clear current list
            for item in raw_data:
                new_trip = Trip(
                    departure=datetime.fromisoformat(item["departure"]),
                    return_date=datetime.fromisoformat(item["return_date"]),
                    is_what_if=item["is_what_if"]
                )

                self.trips.append(new_trip)

            self.refresh_tree()
            self.refresh_dashboard()

            messagebox.showinfo("Loaded", "History synced")
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Load Error", f"Could not read file: {e}")

    def apply_zoom(self):
        """Reconfigures global styles based on the current font_scale."""
        new_size = int(11 * self.font_scale)
        header_size = int(12 * self.font_scale)
        dash_size = int(20 * self.font_scale) # Large numbers in dashboard
        
        # Update Standard Widgets
        self.style.configure("TLabel", font=(self.base_font_family, new_size))
        self.style.configure("TButton", font=(self.base_font_family, new_size))
        self.style.configure("TCheckbutton", font=(self.base_font_family, new_size))
        
        # Update Treeview (Table)
        # Rowheight must scale with font size or text gets cut off!
        self.style.configure("Treeview", 
                            font=(self.base_font_family, new_size), 
                            rowheight=int(35 * self.font_scale))
        self.style.configure("Treeview.Heading", font=(self.base_font_family, header_size, "bold"))
        
        # Update your custom Dashboard labels specifically
        self.ilr_status_lbl.config(font=("Helvetica", dash_size, "bold"))
        self.bc_status_lbl.config(font=("Helvetica", dash_size, "bold"))
        
        # Update the solve text (Troubleshooting box)
        self.solve_text.config(font=("Consolas", new_size), wraplength=int(800 * self.font_scale))

    def zoom_in(self, event=None):
        if self.font_scale < 2.0: # Cap at 200%
            self.font_scale += 0.1
            self.apply_zoom()

    def zoom_out(self, event=None):
        if self.font_scale > 0.7: # Cap at 70%
            self.font_scale -= 0.1
            self.apply_zoom()

    def reset_zoom(self,event=None):
        self.font_scale = 1.0
        self.apply_zoom()


    def show_about(self):
        messagebox.showinfo(
            "About BNO Tracker", 
            "BNO Settlement Suite v2.0\n\n"
            "Developed by: Kimi Tang\n"
            "Built with Python & ttkbootstrap\n\n"
            "Licensed under MIT. (c) 2026"
        ) 
            

        
if __name__ == "__main__":
    root = tb.Window(themename="superhero")
    app = BNOAdvancedTracker(root)
    root.mainloop()