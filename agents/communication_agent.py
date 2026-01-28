from agents.base_agent import BaseAgent


class CommunicationAgent(BaseAgent):
    def __init__(self):
        super().__init__("CommunicationAgent")

    def run(self, disruption, crew_info, welfare_info):
        passenger_msg = (
            f"Dear Guest, your flight {disruption['flight']} is delayed. "
            f"We have arranged meals and accommodation. No action required."
        )

        ops_msg = (
            f"{disruption['flight']} disrupted at {disruption['station']}. "
            f"Hotel rooms: {welfare_info['hotel_required']}. "
            f"Crew action: {crew_info['recommendation']}"
        )

        return {
            "passenger_message": passenger_msg,
            "ops_message": ops_msg
        }