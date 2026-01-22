import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class UKResidenceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("UK BNO Residency & Absence Tracker (2026)")
        self.root.geometry("700x600")
        self.editing_index = None  # Add this at the end of __init__
        raw_data = [
            ("07/08/2024", "07/09/2024"),
            ("28/03/2025", "03/04/2025"),
            ("08/04/2025", "16/04/2025"),
            ("15/06/2025", "18/08/2025"),
            ("04/12/2025", "07/12/2025"),
            ("11/12/2025", "27/01/2026")
        ]
        # Data storage: List of tuples (start_date, end_date)
        self.trips = []
        for dep_str, ret_str in raw_data:
            start = datetime.strptime(dep_str, "%d/%m/%Y")
            end = datetime.strptime(ret_str, "%d/%m/%Y")
            days_absent = max(0, (end - start).days - 1)
            self.trips.append((start, end, days_absent))

        self.entry_date = datetime(2024, 9, 7) # Your entry date
        

        self.setup_ui()
        self.refresh_tree()
        self.update_calculations()


    def setup_ui(self):
        # Header
        ttk.Label(self.root, text="BNO Visa Absence Tracker", font=("Arial", 16, "bold")).pack(pady=10)
        ttk.Label(self.root, text=f"UK Entry Date: {self.entry_date.strftime('%d/%m/%Y')}", font=("Arial", 10)).pack()

        # Input Area
        input_frame = ttk.LabelFrame(self.root, text="Add New Trip")
        input_frame.pack(pady=10, padx=20, fill="x")

        ttk.Label(input_frame, text="Departure (DD/MM/YYYY):").grid(row=0, column=0, padx=5, pady=5)
        self.dep_entry = ttk.Entry(input_frame)
        self.dep_entry.grid(row=0, column=1)

        ttk.Label(input_frame, text="Return (DD/MM/YYYY):").grid(row=0, column=2, padx=5, pady=5)
        self.ret_entry = ttk.Entry(input_frame)
        self.ret_entry.grid(row=0, column=3)

        # Replace the existing Add Trip button line with these three:
        self.add_btn = ttk.Button(input_frame, text="Add Trip", command=self.add_trip)
        self.add_btn.grid(row=0, column=4, padx=5)

        ttk.Button(input_frame, text="Edit Selected", command=self.load_trip_to_edit).grid(row=0, column=5, padx=5)
        ttk.Button(input_frame, text="Delete", command=self.delete_trip).grid(row=0, column=6, padx=5)

        # Trip List
        self.tree = ttk.Treeview(self.root, columns=("Start", "End", "Absence"), show='headings', height=8)
        self.tree.heading("Start", text="Date Left UK")
        self.tree.heading("End", text="Date Returned")
        self.tree.heading("Absence", text="Full Days Absent")
        self.tree.pack(pady=10, padx=20, fill="both", expand=True)

        # Dashboard
        self.status_frame = ttk.LabelFrame(self.root, text="Status Dashboard")
        self.status_frame.pack(pady=10, padx=20, fill="x")
        
        self.ilr_label = ttk.Label(self.status_frame, text="ILR (Rolling 180): Pass", foreground="green")
        self.ilr_label.pack(anchor="w", padx=10)
        
        self.bc_total_label = ttk.Label(self.status_frame, text="BC Total (450 days limit): 0 days used")
        self.bc_total_label.pack(anchor="w", padx=10)

    def add_trip(self):
        try:
            start = datetime.strptime(self.dep_entry.get(), "%d/%m/%Y")
            end = datetime.strptime(self.ret_entry.get(), "%d/%m/%Y")
            
            if end <= start:
                raise ValueError("Return date must be after departure.")
            
            days_absent = max(0, (end - start).days - 1)
            new_trip = (start, end, days_absent)

            if self.editing_index is not None:
                # Update existing trip
                self.trips[self.editing_index] = new_trip
                self.editing_index = None
                self.add_btn.config(text="Add Trip")
            else:
                # Add new trip
                self.trips.append(new_trip)

            self.refresh_tree()
            self.update_calculations()
            self.dep_entry.delete(0, tk.END)
            self.ret_entry.delete(0, tk.END)
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")

    def load_trip_to_edit(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a trip to edit.")
            return
        
        # Get index of selected item
        idx = self.tree.index(selected[0])
        trip = self.trips[idx]
        
        # Fill entry boxes
        self.dep_entry.delete(0, tk.END)
        self.dep_entry.insert(0, trip[0].strftime("%d/%m/%Y"))
        self.ret_entry.delete(0, tk.END)
        self.ret_entry.insert(0, trip[1].strftime("%d/%m/%Y"))
        
        self.editing_index = idx
        self.add_btn.config(text="Save Edit")

    def delete_trip(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select", "Please select a trip to delete.")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this trip?"):
            idx = self.tree.index(selected[0])
            self.trips.pop(idx)
            self.refresh_tree()
            self.update_calculations()

    def refresh_tree(self):
        # Clears and redraws the list
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.trips:
            self.tree.insert("", "end", values=(t[0].strftime("%d/%m/%Y"), t[1].strftime("%d/%m/%Y"), t[2]))

    def update_calculations(self):
        total_absent = sum(t[2] for t in self.trips)
        
        # BC Total Check
        self.bc_total_label.config(text=f"BC Total (450 limit): {total_absent} days used ({450 - total_absent} left)")
        if total_absent > 450:
            self.bc_total_label.config(foreground="red")
        
        # Rolling 180 Day Check for ILR
        max_rolling = 0
        if self.trips:
            # Sort trips by date
            sorted_trips = sorted(self.trips, key=lambda x: x[0])
            for i in range(len(sorted_trips)):
                window_end = sorted_trips[i][1]
                window_start = window_end - timedelta(days=365)
                
                # Count absences in this 12-month window
                window_sum = 0
                for start, end, days in sorted_trips:
                    if end > window_start and start < window_end:
                        # Simple overlap calculation
                        overlap_start = max(start + timedelta(days=1), window_start)
                        overlap_end = min(end - timedelta(days=1), window_end)
                        if overlap_end >= overlap_start:
                            window_sum += (overlap_end - overlap_start).days + 1
                
                max_rolling = max(max_rolling, window_sum)

        self.ilr_label.config(text=f"ILR Rolling Max (180 limit): {max_rolling} days")
        if max_rolling > 180:
            self.ilr_label.config(text=f"ILR Rolling Max: {max_rolling} (BREACHED)", foreground="red")
        else:
            self.ilr_label.config(foreground="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = UKResidenceTracker(root)
    root.mainloop()