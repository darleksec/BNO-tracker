from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Trip:
    """Container for absence data. Using a dataclass makes the code more 
    readable and easier to maintain than list indexing."""
    departure: datetime
    return_date: datetime
    is_what_if: bool = False

    @property
    def daysAbsent(self):
        """
        UK Home Office Rule: Only full 24-hour periods outside the UK count as an absence.
        The days of departure and arrival are NOT counted as absences.
        Formula: (Return - Departure) - 1.
        """
        return max(0, (self.return_date - self.departure).days - 1)

class LogicEngine:
    @staticmethod
    def getMilestoneDates(visa_date_str):
        """Calculates key milestones based on visa grant date."""
        try:
            visa_date = datetime.strptime(visa_date_str, "%d/%m/%Y")
            # ILR is usually 5 years (minus 28 days) from visa approval/entry
            ilr_eligible = visa_date + timedelta(days=5*365.25) - timedelta(days=28)
            # BC is usually 1 year after ILR
            bc_eligible = ilr_eligible + timedelta(days=365)
            return ilr_eligible, bc_eligible
        except:
            return None, None

    def getStats(self, trips, bc_eligible):
        """
        THE ROLLING WINDOW ALGORITHM:
        Instead of checking calendar years, we check every 365-day period 
        starting from the departure of every trip to find the highest density of absences.
        """
        max_r = 0
        for t in trips:
            window_start = t.departure 
            window_end = window_start + timedelta(days=365)
            
            # Calculate overlap for every trip within THIS specific 365-day window
            usage = sum(
                max(0, (min(tr.return_date - timedelta(days=1), window_end) - 
                        max(tr.departure + timedelta(days=1), window_start)).days + 1)
                for tr in trips if tr.departure < window_end and tr.return_date > window_start
            )
            max_r = max(max_r, usage)

        # British Citizenship (BC) fixed look-back windows
        bc_5yr_start = bc_eligible - timedelta(days=5*365.25)
        bc_final_start = bc_eligible - timedelta(days=365)

        total_bc = sum(t.daysAbsent for t in trips if t.departure > bc_5yr_start)
        final_bc = sum(t.daysAbsent for t in trips if t.departure > bc_final_start)

        return max_r, total_bc, final_bc

    def get_troubleshooting_advice(self, all_max, all_bc, bc_eligible, trips):
        """The 'Expert System' logic: identifies breaches and suggests fixes."""
        solutions = []
        if all_max > 180:
            solutions.append("ILR BREACH: Rolling window exceeds 180 days.\nSOLUTION: Reduce 'What-If' duration or check for work-related exemptions.")
        
        if all_bc > 450:
            solutions.append(f"BC TOTAL BREACH: {all_bc}/450 days.\nSOLUTION: Delay app until old trips fall out of the 5-year window.")

        # BC Presence Rule: You must be physically in the UK exactly 5 years before the app date
        presence_date = bc_eligible - timedelta(days=5*365)
        conflict = next((t for t in trips if t.departure <= presence_date <= t.return_date), None)
        
        if conflict:
            safe_app = (conflict.return_date + timedelta(days=1)) + timedelta(days=5*365)
            solutions.append(f"BC PRESENCE FAIL: Away on {presence_date.strftime('%d/%m/%Y')}.\nFIX: Apply on/after {safe_app.strftime('%d/%m/%Y')}.")

        return "\n\n".join(solutions) if solutions else ""

    def run_sim(self, current_trips, bc_eligible):
        """
        A 'Brute Force' simulator to find the user's remaining 'Travel Budget'.
        It adds 1 day at a time until a rule is broken.
        """
        today = datetime.now()
        max_safe = 0
        limit_reason = "No upcoming constraints found." 
        
        for d in range(1, 451): # Cap at 450 days (BC limit)
            sim_trip = Trip(departure=today + timedelta(days=1), 
                            return_date=today + timedelta(days=d+1), 
                            is_what_if=True)
            sim_trips = current_trips + [sim_trip]
            sim_max, sim_bc_total, sim_bc_final = self.getStats(sim_trips, bc_eligible)

            if sim_max > 180: limit_reason = "Hit ILR 180-Day Rolling Limit"; break
            if sim_bc_total > 450: limit_reason = "Hit BC 450-Day 5-Year Limit"; break
            if sim_bc_final > 90: limit_reason = "Hit BC 90-Day Final Year Limit"; break
            max_safe = d

        return max_safe, limit_reason