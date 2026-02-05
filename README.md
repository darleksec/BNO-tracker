# BNO Settlement and Citizenship Suite (2026)

[Project Repository](https://github.com/darleksec/BNO-tracker)

A high-integrity compliance and tracking suite for British National (Overseas) visa holders. This tool automates the validation of residency requirements for Indefinite Leave to Remain (ILR) and British Citizenship (BC) applications.

## Overview

The BNO-tracker is a Python-based desktop application designed to eliminate human error in calculating "Rolling Window" absences. UK Home Office rules regarding residency are mathematically complex; this suite provides a reliable logic engine to ensure applicants remain within the statutory limits of their visa class.

## Core Capabilities

* **Rolling 365-Day Absence Monitor**: Identifies the maximum absence density across any possible 365-day window to prevent ILR breaches.
* **Hypothetical Trip Simulation**: A "What-If" engine that allows users to test travel plans against their current residency data without permanent record modification.
* **Statutory Presence Validator**: Cross-references application dates against historical travel to ensure physical presence in the UK exactly five years prior to the BC application date.
* **Conflict Resolution**: Integrated collision detection for overlapping or logically impossible travel dates.
* **Data Persistence**: Local JSON-based serialization for user privacy and offline data management.

## Technical Logic and Algorithms

The primary challenge of UK immigration compliance is that the 180-day limit is not based on a calendar year, but on any rolling 365-day period.

### Rolling Window Calculation

The logic engine utilizes a forward-projecting windowing algorithm. For every trip departure recorded, the engine creates a window: $[T_{start}, T_{start} + 365]$. It then calculates the intersection of all other recorded trips within this range.

The intersection of two intervals, Trip A $[S_1, E_1]$ and Trip B $[S_2, E_2]$, is calculated using the following formula:

$$Overlap = \max(0, \min(E_1, E_2) - \max(S_1, S_2) + 1)$$

### Absence Counting Convention

In accordance with Home Office guidance, only full days spent outside the UK are counted. The days of departure and arrival are excluded from the total. 

$$Absence = \max(0, (Date_{Return} - Date_{Departure}) - 1)$$



## System Requirements and Dependencies

| Dependency | Version | Purpose |
| :--- | :--- | :--- |
| Python | 3.8+ | Core Runtime |
| ttkbootstrap | Latest | Themed UI Framework |
| Tkinter | Standard | GUI Base |
| JSON | Standard | Data Persistence |

## Installation and Execution

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


### Usage

Configure Base Dates: Set your Visa Approval and UK Entry dates.

Log Trips: Add confirmed travel history to the Absence Log.

Plan Future Trips: Toggle "What-If" mode to see how a potential trip affects your "Delta Impact."

Consult the Planner: Use the Safe Travel Planner to see the maximum days you can safely leave the UK starting tomorrow.



## Credits & Attribution
* **Lead Developer:** [Kimi Tang/darleksec]
* **Libraries Used:** * [ttkbootstrap](https://github.com/israel-dryer/ttkbootstrap) by Israel Dryer (Theme & UI)
    * [Tkinter](https://docs.python.org/3/library/tkinter.html) (Standard GUI Framework)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


