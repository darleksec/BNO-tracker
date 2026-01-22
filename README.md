🇬🇧 UK BNO Residency & Citizenship Suite

An advanced algorithmic tool for BNO visa holders to navigate UK Home Office residency requirements.

🚀 Project Overview

This application is a specialized decision-support system engineered to track, simulate, and predict residency status for BNO visa holders. It automates the calculation of the complex "Rolling 180-day" Indefinite Leave to Remain (ILR) rule and provides a simulation engine for future travel planning.

🛠 Key Technical Features

Rolling Window Algorithm: Implements a sliding window check to ensure no 365-day period in a 5-year span exceeds the 180-day absence limit.

Safe Travel Simulation: A predictive engine that calculates the maximum allowable absence for a future trip based on historical and currently logged travel data.

"What-If" Logic Engine: Allows users to model hypothetical future trips. The system calculates a "Delta Impact", showing how a proposed trip would change the user's residency health compared to their current confirmed status.

Application Date Predictor: Calculates the earliest valid ILR application date by accounting for the "Presence Rule" and the 28-day application window.

JSON Persistence: Implements custom serialization to save and restore user states (visa dates, trip logs, and hypothetical scenarios) to a local bno_data.json file.

📜 Version History & Evolution

This project followed an iterative development lifecycle, evolving from a simple tracker into a comprehensive suite:

Version	Milestone	Key Features Added
v1.0	Core Logic	Implementation of the rolling 180-day absence calculation and basic CRUD for trips.
v2.0	Date Engine	Integration of Visa Approval and UK Entry dates; introduced ILR target date calculations and countdowns.
v3.0	UI Refinement	Migration to a structured ttk.Treeview for better data visualization and trip management.
v4.0	Simulation	Feature Release: Added the "Safe Travel Planner" to simulate future travel limits.
v5.0	Dashboarding	Complete UI overhaul; introduced separate "Residency Health" dashboards for ILR and British Citizenship.
v6.0	Hypotheticals	Added "What-If" trip toggles, allowing users to test scenarios without altering confirmed logs.
v7.0	Persistence	Current Version: Added "Delta Impact" analytics and JSON-based data persistence.
🧠 Technical Deep-Dive: The Rolling Window

One of the core challenges was the Home Office Rolling 180-Day Rule. Unlike a fixed calendar year, the system must check every possible 365-day window.

Python

# Algorithmic approach:
for trip in sorted_trips:
    window_end = trip.end
    window_start = window_end - timedelta(days=365)
    
    # Calculate overlap of all other trips within this specific window
    current_usage = sum_overlaps(all_trips, window_start, window_end)
    max_rolling_breach = max(max_rolling_breach, current_usage)
🛠 Tech Stack

Language: Python 3.x

Library: tkinter / ttk (GUI Development)

Logic: datetime & timedelta (Temporal Algorithms)

Data: JSON (Serialization & Persistence)

📸 Usage

Configure Base Dates: Set your Visa Approval and UK Entry dates.

Log Trips: Add confirmed travel history to the Absence Log.

Plan Future Trips: Toggle "What-If" mode to see how a potential trip affects your "Delta Impact."

Consult the Planner: Use the Safe Travel Planner to see the maximum days you can safely leave the UK starting tomorrow.

🎓 Portfolio Note

Built as a CS major project to demonstrate proficiency in algorithmic thinking, iterative software design, and GUI engineering for solving real-world regulatory compliance problems.
