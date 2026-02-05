BNO Settlement & Citizenship Suite (2026)
A high-integrity compliance tool for BNO (British National Overseas) visa holders to track residency requirements for Indefinite Leave to Remain (ILR) and British Citizenship (BC).

BNO-tracker automates the complex "Rolling Window" absence logic and "Presence Rule" checks that are often prone to human error during the 5-year residency path.

Key Features
Rolling Window Engine: Automatically identifies the 365-day period with the highest density of absences to ensure compliance with the < 180-day ILR rule.

Safe Travel Planner (What-If): Simulate future travel dates without affecting historical records to see the immediate impact on your travel "budget."

BC Presence Validator: Checks the critical "Presence Rule"—ensuring you were physically in the UK exactly 5 years prior to your citizenship application date.

Persistence Layer: Full Save/Load functionality using JSON serialization for local data privacy.

Dynamic UI Scaling: Modern, accessible interface with real-time zoom and font scaling.

Conflict Detection: Prevents logical errors by blocking overlapping trip dates.


The Logic: How it Works
Calculating UK residency isn't just about counting days; it's about Interval Management.

The Rolling Window Algorithm
Unlike a calendar-year calculation, the ILR rule applies to any rolling 365-day period. This project implements a Dynamic Windowing approach:

The engine iterates through every trip departure.

It projects a 365-day window forward.

It calculates the intersection of all other trips within that window using: Overlap = max(0, min(EndA, EndB) - max(StartA, StartB) + 1)

It returns the maximum density found across the entire history.

Presence Rule Validation
For British Citizenship, the Home Office requires physical presence in the UK on the date 5 years prior to application. The tracker cross-references your planned application date against your trip database to flag "Presence Rule Fails" and suggests the earliest "Safe Date" to apply.



Installation & Usage
Prerequisites
Python 3.8 or higher

pip (Python package manager)


Setup
Clone the repository:

    Bash
    git clone https://github.com/darleksec/BNO-tracker.git
    cd BNO-tracker
Install dependencies:

Bash
    pip install ttkbootstrap
    Run the application:

Bash
    python app.py
    
Tech Stack

    Language: Python 3.x
    
    Library: tkinter / ttk (GUI Development)
    
    Logic: datetime & timedelta (Temporal Algorithms)


 Usage

    Configure Base Dates: Set your Visa Approval and UK Entry dates.
    
    Log Trips: Add confirmed travel history to the Absence Log.
    
    Plan Future Trips: Toggle "What-If" mode to see how a potential trip affects your "Delta Impact."
    
    Consult the Planner: Use the Safe Travel Planner to see the maximum days you can safely leave the UK starting tomorrow.

Portfolio Note

Built as a CS major project to demonstrate proficiency in algorithmic thinking, iterative software design, and GUI engineering for solving real-world regulatory compliance problems.

## Credits & Attribution
* **Lead Developer:** [Kimi Tang/darleksec]
* **Libraries Used:** * [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) by Israel Dryer (Theme & UI)
    * [Tkinter](https://docs.python.org/3/library/tkinter.html) (Standard GUI Framework)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Note : implement view optoins to allow changes to font size/window size