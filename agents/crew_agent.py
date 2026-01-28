import pandas as pd
from agents.base_agent import BaseAgent


class CrewImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__("CrewImpactAgent")

    def run(self, disruption_event):
        crew_df = pd.read_csv("data/crew_assignments.csv")
        impacted = crew_df[crew_df['flight'] == disruption_event['flight']]

        # New column name from the updated CSV: duty_remaining_minutes
        illegal_crew = impacted[impacted['duty_remaining_minutes'] < disruption_event['delay_minutes']]

        return {
            "flight": disruption_event['flight'],
            "illegal_crew_count": len(illegal_crew),
            "recommendation": "Activate standby crew" if len(illegal_crew) > 0 else "No action required"
        }