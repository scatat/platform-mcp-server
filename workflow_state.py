
import json
from pathlib import Path

STATE_FILE = Path(__file__).parent / ".ephemeral" / "workflow-state.json"

def get_workflow_state():
    """Reads and returns the current workflow state."""
    if not STATE_FILE.exists():
        return {"design_validated": False, "critical_path_analyzed": False}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def update_workflow_state(key, value):
    """Updates a specific key in the workflow state file."""
    state = get_workflow_state()
    state[key] = value
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def reset_workflow_state():
    """Resets the workflow state to its default."""
    initial_state = {"design_validated": False, "critical_path_analyzed": False}
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(initial_state, f, indent=2)
