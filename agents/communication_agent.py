import json
import pandas as pd
from google import genai
from agents.base_agent import BaseAgent

class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("CommunicationAgent")

    def run(self, disruption, crew, welfare):
        """
        Generates proactive communication streams and fetches passenger contact data for WhatsApp.
        """
        # 1. Fetch Contact Data from PNR
        recipients = []
        try:
            pnr_df = pd.read_csv("data/pnr_data.csv")
            pnr_df['DepartureDateUTC'] = pd.to_datetime(pnr_df['DepartureDateUTC'])
            
            flight_id = disruption['flight']
            today = pd.to_datetime(disruption['timestamp']).date()

            # Filter for specific flight and today's date
            impacted_contacts = pnr_df[
                (pnr_df['FlightNumber'] == flight_id) & 
                (pnr_df['DepartureDateUTC'].dt.date == today)
            ]
            
            for _, row in impacted_contacts.iterrows():
                recipients.append({
                    "name": row['PaxName'],
                    "phone": row['phoneNumber'],
                    "pnr": row['PNR']
                })
        except Exception as e:
            print(f"Error fetching contact data: {e}")

        # 2. Prepare AI Prompt
        input_data = {
            "flight": disruption['flight'],
            "delay": disruption['delay_minutes'],
            "station": disruption['station'],
            "welfare_summary": welfare['welfare_summary'],
            "hotel_count": welfare['hotel_required'],
            "meal_count": welfare['meals_required'],
            "crew_strategy": crew['recommendation']
        }

        prompt = f"""
        Act as the Etihad Guest Communications & Ops Liaison.
        Convert the following operational data into three distinct, proactive communication streams.
        
        Operational Data:
        {json.dumps(input_data, indent=2)}
        
        Required Outputs:
        
        1. Passenger SMS/Broadcast (Professional & Caring):
           - Focus on 'Proactive Care'. 
           - Mention that meals/hotels are arranged (if applicable per data).
           - Shift from 'apology' to 'action taken'.
           - Keep it concise.
           
        2. Airport Ops Briefing (Targeted & Tactical):
           - Specifically for Ground Operations at {disruption['station']}.
           - Must include counts (e.g., [H] hotel rooms required).
           - Mention crew recovery status.
           
        3. Call-Center Summary (Contextual for Agents):
           - Focus on the 'Why' and 'Current Status' so agents can handle calls.
        
        Tone: Modern, Etihad Premium, Proactive.
        
        Output Format:
        ---
        PASSENGER_MSG: [Content]
        ---
        OPS_BRIEF: [Content]
        ---
        CALL_CENTER_SUMMARY: [Content]
        """

        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            full_text = response.text.strip()
            
            # Parsing the structured response
            parts = full_text.split("---")
            passenger_msg = "Awaiting Message..."
            ops_msg = "Awaiting Briefing..."
            call_center_msg = "Awaiting Summary..."

            for part in parts:
                if "PASSENGER_MSG:" in part:
                    passenger_msg = part.replace("PASSENGER_MSG:", "").strip()
                elif "OPS_BRIEF:" in part:
                    ops_msg = part.replace("OPS_BRIEF:", "").strip()
                elif "CALL_CENTER_SUMMARY:" in part:
                    call_center_msg = part.replace("CALL_CENTER_SUMMARY:", "").strip()

        except Exception as e:
            print(f"DEBUG Comm LLM Error: {e}")
            passenger_msg = f"Dear Guest, your {disruption['flight']} flight is delayed. We've arranged care measures at {disruption['station']}. No action needed."
            ops_msg = f"Welfare triggered for {disruption['flight']}. {welfare['hotel_required']} hotels required."
            call_center_msg = f"Flight {disruption['flight']} delayed by {disruption['delay_minutes']}m. Welfare and crew recovery in progress."

        return {
            "passenger_message": passenger_msg,
            "ops_message": ops_msg,
            "call_center_summary": call_center_msg,
            "recipients": recipients
        }