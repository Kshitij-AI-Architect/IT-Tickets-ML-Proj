"""Utility helper functions."""
import uuid
from datetime import datetime


def generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def now_iso() -> str:
    """Get current UTC time in ISO format."""
    return datetime.utcnow().isoformat()


def calculate_automation_percentage(steps: list[dict]) -> float:
    """
    Calculate automation percentage from resolution steps.
    
    Args:
        steps: List of steps with 'classification' field
               ('auto', 'semi', 'manual')
    
    Returns:
        Percentage (0-100)
    """
    if not steps:
        return 0.0
    
    weights = {"auto": 1.0, "semi": 0.5, "manual": 0.0}
    total_weight = sum(weights.get(s.get("classification", "manual"), 0) for s in steps)
    
    return round((total_weight / len(steps)) * 100, 1)


def calculate_time_weighted_automation(steps: list[dict]) -> float:
    """
    Calculate automation percentage weighted by time.
    
    Args:
        steps: List of steps with 'classification' and 'time_mins' fields
    
    Returns:
        Percentage (0-100)
    """
    if not steps:
        return 0.0
    
    total_time = sum(s.get("time_mins", 1) for s in steps)
    if total_time == 0:
        return calculate_automation_percentage(steps)
    
    weights = {"auto": 1.0, "semi": 0.5, "manual": 0.0}
    weighted_auto = sum(
        s.get("time_mins", 1) * weights.get(s.get("classification", "manual"), 0)
        for s in steps
    )
    
    return round((weighted_auto / total_time) * 100, 1)
