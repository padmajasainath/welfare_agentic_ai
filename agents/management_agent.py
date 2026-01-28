from agents.base_agent import BaseAgent


class ManagementInsightAgent(BaseAgent):
    def __init__(self):
        super().__init__("ManagementInsightAgent")

    def run(self, disruption, crew, welfare):
        return (
            f"Disruption {disruption['flight']} impacted {welfare['total_impacted']} passengers. "
            f"Crew risk: {crew['illegal_crew_count']}. Early intervention recommended."
        )