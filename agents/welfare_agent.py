import pandas as pd
from google import genai
import json
from agents.base_agent import BaseAgent

class WelfareAgent(BaseAgent):
    def __init__(self):
        super().__init__("PassengerWelfareAgent")

    def run(self, disruption_event):
        """
        Two-step process:
        1. Deterministic PNR analysis for counts.
        2. LLM reasoning for high-value welfare recommendations.
        """
        # 1. Read PNR data
        try:
            pnr_df = pd.read_csv("data/pnr_data.csv")
            pnr_df['DepartureDateUTC'] = pd.to_datetime(pnr_df['DepartureDateUTC'])
        except Exception as e:
            print(f"Error reading PNR data: {e}")
            return self._empty_result(disruption_event['flight'])

        # 2. Extract disruption details
        flight_id = disruption_event['flight']
        delay = disruption_event['delay_minutes']
        station = disruption_event['station']
        today = pd.to_datetime(disruption_event['timestamp']).date()

        # 3. Filter PNRs for this specific delayed flight ON TODAY'S DATE
        impacted_pnrs = pnr_df[
            (pnr_df['FlightNumber'] == flight_id) & 
            (pnr_df['DepartureDateUTC'].dt.date == today)
        ].copy()

        # 4. Deterministic Counts
        total_pax = len(impacted_pnrs)
        transit_pax = len(impacted_pnrs[impacted_pnrs['JourneyType'] == 'Return'])
        business_first = len(impacted_pnrs[impacted_pnrs['Cabin_Class'].isin(['Business', 'First'])])
        special_pax = len(impacted_pnrs[impacted_pnrs['WheelChairRequested'] == 1])
        
        meal_count = total_pax if delay >= 15 else 0
        hotel_count = total_pax if delay > 180 else 0

        # 5. LLM Reasoning Layer
        input_data = {
            "disruption": {
                "flight": flight_id,
                "station": station,
                "delay_minutes": delay,
            },
            "pax_stats": {
                "total": total_pax,
                "transit": transit_pax,
                "premium_cabin": business_first,
                "special_assistance": special_pax,
                "hotels_calculated": hotel_count,
                "meals_calculated": meal_count
            }
        }

        prompt = f"""
        Act as an Etihad Guest Experience Manager at {station} HUB.
        Generate a highly specific operational brief for Flight {flight_id}.
        
        Data:
        {json.dumps(input_data, indent=2)}
        
        Mandatory Instructions:
        1. Start with the exact flight number and total passenger count.
        2. Specifically mention connection risks for the {transit_pax} transit guests.
        3. If there are {business_first} Gold/Premium or {special_pax} Special Assistance guests, mention the priority care status.
        4. Use a professional, data-driven narrative (not bullet points).
        5. Explain the reasoning for {hotel_count} hotels (e.g., meeting the 3-hour policy) or {meal_count} meals.
        
        Example Style:
        "{total_pax} guests on {flight_id} are impacted by the {delay}-minute delay at {station}. 
        Specialized care is being coordinated for {special_pax} guests requiring assistance and {business_first} premium cabin members. 
        With {transit_pax} guests transitioning through the hub, connection protection is active. 
        Welfare deployed: {meal_count} meal vouchers issued per policy."
        """

        try:
            response = self.client.models.generate_content(model=self.model_id, contents=prompt)
            summary = response.text.strip()
        except Exception:
            summary = f"{total_pax} passengers impacted. Connection risk for {transit_pax} transit pax. {hotel_count} hotels and {meal_count} meals required."

        # 6. Incremental Update to welfare_prod.csv for Analytics
        if not impacted_pnrs.empty:
            new_welfare = impacted_pnrs[['FlightNumber', 'PAX_id']].copy()
            new_welfare.rename(columns={'FlightNumber': 'flight', 'PAX_id': 'passenger_id'}, inplace=True)
            new_welfare['hotel_required'] = (delay > 180)
            new_welfare['meal_required'] = (delay >= 15)
            new_welfare['date'] = today.isoformat()
            
            try:
                existing_df = pd.read_csv("data/welfare_prod.csv")
                combined_df = pd.concat([existing_df, new_welfare], ignore_index=True)
                combined_df.drop_duplicates(subset=['flight', 'passenger_id', 'date'], keep='last', inplace=True)
            except FileNotFoundError:
                combined_df = new_welfare
            combined_df.to_csv("data/welfare_prod.csv", index=False)

        return {
            "total_impacted": total_pax,
            "hotel_required": hotel_count,
            "meals_required": meal_count,
            "transit_pax": transit_pax,
            "welfare_summary": summary
        }

    def _empty_result(self, flight):
        return {
            "total_impacted": 0, "hotel_required": 0, "meals_required": 0, 
            "transit_pax": 0, "welfare_summary": "Awaiting Signal Data..."
        }