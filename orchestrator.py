from agents.disruption_agent import DisruptionDetectionAgent
from agents.crew_agent import CrewImpactAgent
from agents.welfare_agent import WelfareAgent
from agents.communication_agent import CommunicationAgent
from agents.management_agent import ManagementInsightAgent
import event_store
 
# Global cache to prevent redundant LLM calls
RESULT_CACHE = {}
 
def handle_disruption(disruptions):
    # Initialize agents
    crew_agent = CrewImpactAgent()
    welfare_agent = WelfareAgent()
    comm_agent = CommunicationAgent()
    mgmt_agent = ManagementInsightAgent()
 
    current_state = []
 
    for event in disruptions:
        flight_id = event['flight']
        delay = round(event['delay_minutes'], 1)
       
        # Check if we already have a fresh result for this flight/delay
        cache_key = f"{flight_id}_{delay}"
       
        if cache_key in RESULT_CACHE:
            # Use cached insights if the data hasn't changed
            event_data = RESULT_CACHE[cache_key]
        else:
            # Data is new or changed - Run agents
            print(f"INFO: Data change for {flight_id}. Running agents...", flush=True)
            crew = crew_agent.run(event)
            welfare = welfare_agent.run(event)
            comm = comm_agent.run(event, crew, welfare)
            insight = mgmt_agent.run(event, crew, welfare)
 
            event_data = {
                "timestamp": event['timestamp'],
                "flight": flight_id,
                "station": event['station'],
                "delay": delay,
                "crew_risk": crew['illegal_crew_count'],
                "crew_rec": crew['recommendation'],
                "welfare": welfare,
                "passenger_msg": comm['passenger_message'],
                "ops_msg": comm['ops_message'],
                "call_center_msg": comm.get('call_center_summary', ""),
                "recipients": comm.get('recipients', []),
                "management_insight": insight
            }
            # Store in cache
            RESULT_CACHE[cache_key] = event_data
 
        current_state.append(event_data)
 
    # Clean cache of old flights no longer in disruptions
    active_keys = [f"{e['flight']}_{round(e['delay_minutes'], 1)}" for e in disruptions]
    for key in list(RESULT_CACHE.keys()):
        if key not in active_keys:
            del RESULT_CACHE[key]
 
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
 
 
