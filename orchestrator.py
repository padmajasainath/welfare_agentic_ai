from agents.disruption_agent import DisruptionDetectionAgent
from agents.crew_agent import CrewImpactAgent
from agents.welfare_agent import WelfareAgent
from agents.communication_agent import CommunicationAgent
from agents.management_agent import ManagementInsightAgent
import event_store

def handle_disruption(disruptions):
    # Initialize all agents once
    crew_agent = CrewImpactAgent()
    welfare_agent = WelfareAgent()
    comm_agent = CommunicationAgent()
    mgmt_agent = ManagementInsightAgent()

    current_state = []

    for event in disruptions:
        # Process disruption through agent chain
        crew = crew_agent.run(event)
        welfare = welfare_agent.run(event)
        comm = comm_agent.run(event, crew, welfare)
        insight = mgmt_agent.run(event, crew, welfare)

        # Prepare the event package
        event_data = {
            "timestamp": event['timestamp'],
            "flight": event['flight'],
            "station": event['station'],
            "delay": event['delay_minutes'],
            "crew_risk": crew['illegal_crew_count'],
            "crew_rec": crew['recommendation'],
            "welfare": welfare,
            "passenger_msg": comm['passenger_message'],
            "ops_msg": comm['ops_message'],
            "call_center_msg": comm.get('call_center_summary', ""),
            "recipients": comm.get('recipients', []),
            "management_insight": insight
        }
        current_state.append(event_data)

    # Sync the in-memory store with the CURRENT state of the CSV
    event_store.set_active_events(current_state)
    if disruptions:
        print(f"DEBUG: Synced {len(disruptions)} active disruptions to store.")
    else:
        # Optional: log when clear
        pass

def start_orchestrator():
    # Start the background detection
    disruption_agent = DisruptionDetectionAgent(poll_interval=2)
    BUCKET = "welfare-agentic-ai-data-bucket"
    disruption_agent.run(f"gs://{BUCKET}/data/flight_schedule.csv", handle_disruption)

if __name__ == "__main__":
    start_orchestrator()
