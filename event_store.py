# Global event store for the dashboard
active_events = []

def set_active_events(events):
    """Replaces the entire history with the current active disruptions."""
    global active_events
    active_events = events

def get_events():
    """Returns the list of current active events."""
    return active_events
