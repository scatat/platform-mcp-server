"""
Example Team Layer - Minimal Demo

This is a SIMPLE example showing how another team could create their own
team layer. This is NOT a real team - just a minimal example.

Team: Example App Team
Use case: Simple app deployment checks (not Flux)
"""

# =============================================================================
# EXAMPLE TEAM TOOLS
# =============================================================================


def check_app_status():
    """
    Example tool: Check if application is running.

    In a real team layer, this would check actual services.
    This is just a minimal example.
    """
    return {
        "success": True,
        "message": "Example tool - would check app status in real implementation",
        "app_status": "unknown",
        "example": True,
    }


def list_app_deployments():
    """
    Example tool: List application deployments.

    In a real team layer, this would query actual deployment systems.
    This is just a minimal example.
    """
    return {
        "success": True,
        "message": "Example tool - would list deployments in real implementation",
        "deployments": [],
        "example": True,
    }
