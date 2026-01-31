import pandas as pd
from google import genai
import json
from agents.base_agent import BaseAgent

class CrewImpactAgent(BaseAgent):
    def __init__(self):
        super().__init__("CrewImpactAgent")

    def run(self, disruption_event):
        """
        Two-step process:
        1. Rule-based computation (Python/Pandas)
        2. LLM reasoning (Gemini 2.0) for ops-grade recommendations
        """
        # Step 1: Rule-based computation (Deterministic)
        BUCKET = "welfare-agentic-ai-data-bucket"
        try:
            crew_df = pd.read_csv(f"gs://{BUCKET}/data/crew_assignments.csv")
            crew_df['duty_start_utc'] = pd.to_datetime(crew_df['duty_start_utc'])
        except Exception as e:
            return {
                "flight": disruption_event['flight'],
                "illegal_crew_count": 0,
                "recommendation": f"Error reading crew data: {str(e)}"
            }
        
        # Use simple date for matching (current day of disruption)
        today = pd.to_datetime(disruption_event['timestamp']).date()

        # Find all crew assigned to the specific flight ON TODAY'S DATE
        impacted_crew = crew_df[
            (crew_df['flight'] == disruption_event['flight']) & 
            (crew_df['duty_start_utc'].dt.date == today)
        ]
        
        # Identify illegal crew: those whose 'duty_remaining_minutes' is less than the current 'delay_minutes'
        delay = disruption_event['delay_minutes']
        illegal_crew = impacted_crew[impacted_crew['duty_remaining_minutes'] < delay]
        
        # Find available standby crew at the same station ON TODAY'S DATE
        standby_crew = crew_df[
            (crew_df['is_standby'] == True) & 
            (crew_df['station'] == disruption_event['station']) &
            (crew_df['duty_start_utc'].dt.date == today)
        ]

        # Step 2: Prepare compact JSON for LLM reasoning layer
        input_data = {
            "disruption": {
                "flight": disruption_event['flight'],
                "station": disruption_event['station'],
                "delay_minutes": delay,
                "timestamp": disruption_event['timestamp']
            },
            "impacted_crew": illegal_crew[['crew_id', 'crew_role', 'next_flight']].to_dict(orient='records'),
            "standby_available": standby_crew[['crew_id', 'crew_role']].to_dict(orient='records'),
            "total_crew_on_flight": len(impacted_crew)
        }

        # Step 3: LLM reasoning layer
        prompt = f"""
        Act as a Crew Control Duty Manager.
        Recommend recovery actions minimizing knock-on delays.
        
        Context Data (Deterministic Results):
        {json.dumps(input_data, indent=2)}
        
        Instructions:
        1. Analyze if the delay causes crew to exceed duty limits based on the 'impacted_crew' list.
        2. VERY IMPORTANT: Identify specific risks to 'next_flight' schedules mentioned in the data (e.g. EY108).
        3. Formulate a recovery strategy using 'standby_available' crew.
        4. Focus on 'ops-grade' professional tone.
        
        Output format (Human-readable + Dashboard-ready):
        **Strategy:** [Analysis of impact on current and onward flights]
        **Recommended Action:** [Primary recovery step]
        **Secondary Option:** [Alternative strategy]
        """

        try:
            # Use the new SDK's generate_content
            model = genai.GenerativeModel(self.model_id)
            response = model.generate_content(prompt)
            recommendation = response.text.strip()
            # Clean up potential markdown if AI adds it
            if recommendation.startswith('"') and recommendation.endswith('"'):
                recommendation = recommendation[1:-1]
        except Exception as e:
            print(f"DEBUG LLM Error: {e}")
            # High-quality fallback if AI fails
            if len(illegal_crew) > 0:
                details = []
                for _, row in illegal_crew.iterrows():
                    impact = f"{row['crew_role']} (Next: {row['next_flight'] if pd.notna(row['next_flight']) else 'None'})"
                    details.append(impact)
                
                recommendation = (
                    f"**Strategy:** {len(illegal_crew)} crew members exceed duty limits. Impacted: {', '.join(details)}.\n\n"
                    f"**Recommended Action:** Immediate standby activation at {disruption_event['station']}.\n\n"
                    f"**Secondary Option:** Request crew swap if standby unavailable."
                )
            else:
                recommendation = "No crew duty violations detected. Monitor for further delays."

        return {
            "flight": disruption_event['flight'],
            "illegal_crew_count": len(illegal_crew),
            "recommendation": recommendation
        }
