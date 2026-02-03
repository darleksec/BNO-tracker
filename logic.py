from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class Trip:
    #container for trips
    departure: datetime
    return_date: datetime
    is_what_if : bool = False

    @property
    def daysAbsent(self):
        #only full 24 hr outside = absent -> out-in-1 = absent 
        return max(0, (self.return_date-self.departure).days-1 )
        
class LogicEngine:

    @staticmethod
    def getMilestoneDates(visa_date_str): #earliest application date
        visa_date = datetime.strptime(visa_date_str, "%d/%m/%Y")
        ilr_eligible = visa_date + timedelta(days = 5*365.25) - timedelta(days=28)
        bc_eligible = ilr_eligible + timedelta(days=365)
        return ilr_eligible, bc_eligible
    

    def getStats(self, trips, bc_eligible):
        max_r = 0
        for t in trips:
            window_start = t.departure 
            window_end = window_start + timedelta(days=365)
            # overlap for every trip in this 365 day window
            usage = sum(
                max(0, (min(tr.return_date - timedelta(days=1), window_end) - 
                        max(tr.departure + timedelta(days=1), window_start)).days + 1)
                for tr in trips if tr.departure < window_end and tr.return_date > window_start
            )
            max_r = max(max_r, usage)

        
        bc_5yr_start = bc_eligible - timedelta(days=5*365.25)
        bc_final_start = bc_eligible - timedelta(days=365)

        total_bc = sum(t.daysAbsent for t in trips if t.departure > bc_5yr_start)
        final_bc = sum(t.daysAbsent for t in trips if t.departure > bc_final_start)

        return max_r, total_bc, final_bc
    
    def get_troubleshooting_advice(self, all_max, all_bc, bc_eligible, trips):
        """Generates the text for the Solutions box based on rules."""
        solutions = []
        if all_max > 180:
            solutions.append("🔴 ILR BREACH: Rolling window exceeds 180 days.\n   SOLUTION: Reduce 'What-If' duration or check for work-related exemptions.")
        
        if all_bc > 450:
            solutions.append(f"🔴 BC TOTAL BREACH: {all_bc}/450 days.\n   SOLUTION: Delay Citizenship app until older trips fall out of the 5-year window.")

        # BC Presence Rule Logic
        presence_date = bc_eligible - timedelta(days=5*365)
        conflict = next((t for t in trips if t.departure <= presence_date <= t.return_date), None)
        if conflict:
            safe_app = (conflict.return_date + timedelta(days=1)) + timedelta(days=5*365)
            solutions.append(f"🔴 BC PRESENCE RULE FAIL: Away on {presence_date.strftime('%d/%m/%Y')}.\n   FIX: Apply on/after {safe_app.strftime('%d/%m/%Y')}.")

        return "\n\n".join(solutions) if solutions else "✅ CURRENT PLANS ARE WITHIN LIMITS."
    
    def run_sim(self, current_trips, bc_eligible):
        today = datetime.now()
        max_safe = 0
        limit_reason = "None" 
        
        for d in range (1, 451):
            sim_ret = today + timedelta(days=d+1)
            sim_trip = Trip (departure=today + timedelta(days=1), 
            return_date=sim_ret, 
            is_what_if=True)
            sim_trips = current_trips + [sim_trip]
            sim_max, sim_bc_total, sim_bc_final = self.getStats(sim_trips, bc_eligible)

            if sim_max > 180: limit_reason = "ILR 180 Days Rule"; break
            if sim_bc_total > 450: limit_reason = "BC 450 Day Limit"; break
            if sim_bc_final > 90: limit_reason = "BC 90 Day final year limit"; break
            max_safe = d

        return max_safe, limit_reason