"""
MCP Server Layers Package

This package implements the 3-layer architecture model:
- platform.py: Universal infrastructure primitives (Teleport, SSH)
- team.py: Team-specific patterns (Flux, K8s access patterns)
- personal.py: Individual developer tools (session management, workflows)

See: resources/architecture/layer-model.yaml for architecture details
"""

__version__ = "2.0.0"
