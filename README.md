🇬🇧 UK BNO Residency & Citizenship Suite

An advanced algorithmic tool for BNO visa holders to navigate UK Home Office residency requirements.

Project Overview

    This application is a specialized decision-support system engineered to track, simulate, and predict residency status for BNO visa holders. It automates the calculation of the complex "Rolling 180-day" Indefinite Leave to Remain (ILR) rule and provides a simulation engine for future travel planning.

Key Technical Features

    Rolling Window Algorithm: Implements a sliding window check to ensure no 365-day period in a 5-year span exceeds the 180-day absence limit.

    Safe Travel Simulation: A predictive engine that calculates the maximum allowable absence for a future trip based on historical and currently logged travel data.

    "What-If" Logic Engine: Allows users to model hypothetical future trips. The system calculates a "Delta Impact", showing how a proposed trip would change the user's residency health compared to their current confirmed status.

    Application Date Predictor: Calculates the earliest valid ILR application date by accounting for the "Presence Rule" and the 28-day application window.
 


Technical Deep-Dive: The Rolling Window

    One of the core challenges was the Home Office Rolling 180-Day Rule. Unlike a fixed calendar year, the system must check every possible 365-day window.




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