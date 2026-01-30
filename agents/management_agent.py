import json
from google import genai
from agents.base_agent import BaseAgent

class ManagementInsightAgent(BaseAgent):
    def __init__(self):
        super().__init__("ManagementInsightAgent")

    def run(self, disruption, crew, welfare):
        """
        Generates executive insights with what-if simulations and cost estimations.
        """
        # 1. Deterministic Cost Modeling (Mock Values)
        # Assuming constants for executive estimation
        COST_MEAL = 25  # USD
        COST_HOTEL = 250 # USD
        COST_MISSED_CONN = 600 # Re-booking + compensation risk per guest
        
        calculated_welfare_cost = (welfare['meals_required'] * COST_MEAL) + (welfare['hotel_required'] * COST_HOTEL)
        
        # Estimate "Early Action" value
        # Assuming early action saves ~15% of transit connections and avoids 10% of total compensation claims
        est_missed_saved = int(welfare['transit_pax'] * 0.18)
        cost_avoided = (est_missed_saved * COST_MISSED_CONN) + (welfare['total_impacted'] * 20)

        input_data = {
            "flight": disruption['flight'],
            "delay": disruption['delay_minutes'],
            "crew_risk": crew['illegal_crew_count'],
            "pax_impact": welfare['total_impacted'],
            "transit_impact": welfare['transit_pax'],
            "welfare_cost_est": calculated_welfare_cost,
            "cost_avoided_est": cost_avoided,
            "missed_connections_saved": est_missed_saved
        }

        # 2. LLM Simulation & Executive Narrative
        prompt = f"""
        Act as the Etihad Chief Operating Officer (COO). 
        Provide an executive summary and 'What-If' risk assessment for Flight {disruption['flight']}.
        
        Context:
        {json.dumps(input_data, indent=2)}
        
        Instructions:
        1. Summarize the current impact in formal executive language.
        2. Conduct two 'What-If' simulations:
           - Scenario A: If the delay extends by another 30 minutes.
           - Scenario B: If the planned aircraft swap or crew recovery fails.
        3. Highlight the financial effectiveness of early intervention.
        4. Focus on 'Cost Avoided' and 'Brand Protection'.
        
        Output format:
        **Executive Summary:** [Formal overview of {disruption['flight']} status]
        **What-If Simulations:** 
        - [30m extension impact...]
        - [Recovery failure impact...]
        **Financial Performance:** 
        - Welfare Commitment: $[Amount]
        - Early intervention reduced missed connections by 18% and avoided $[Amount] in compensation/rebooking costs.
        """

        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            insight = response.text.strip()
        except Exception as e:
            print(f"DEBUG Management LLM Error: {e}")
            insight = (
                f"Executive Summary: Flight {disruption['flight']} impacted by {disruption['delay_minutes']}m delay. "
                f"Welfare commitment estimated at ${calculated_welfare_cost}. "
                f"Early intervention reduced missed connections and avoided approximately ${cost_avoided} in secondary costs."
            )

        return insight