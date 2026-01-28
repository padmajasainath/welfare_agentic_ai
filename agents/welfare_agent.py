import pandas as pd
from agents.base_agent import BaseAgent


class WelfareAgent(BaseAgent):
    def __init__(self):
        super().__init__("PassengerWelfareAgent")

    def run(self, disruption_event):
        df = pd.read_csv("data/welfare_prod.csv")
        impacted = df[df['flight'] == disruption_event['flight']]

        return {
            "total_impacted": len(impacted),
            "hotel_required": len(impacted[impacted['hotel_required'] == True]),
            "meals_required": len(impacted),
            "transit_pax": len(impacted[impacted['is_transit'] == True])
        }