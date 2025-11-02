#!/usr/bin/env python3
"""
Design Validation Module - Programmatic Enforcement of Design Checklist

This module provides programmatic validation of tool designs against the
design-checklist.yaml rules. It's the enforcement mechanism for MW-002.

ANALOGY: Like a pre-flight checklist for pilots - systematic checks that must
be completed before proceeding.

Architecture:
- Reads design-checklist.yaml
- Validates tool proposals against the checklist
- Generates validation tokens for approved designs
- Stores proposals in .ephemeral/tool-proposals/

This is NOT optional documentation - it's a required gate in the development
process.
"""

import hashlib
import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


class DesignValidator:
    """
    Validates tool designs against design-checklist.yaml.

    This class provides programmatic enforcement of the design principles
    that were previously only documented.
    """

    def __init__(self, checklist_path: Optional[str] = None):
        """
        Initialize the validator.

        Args:
            checklist_path: Path to design-checklist.yaml (auto-detected if None)
        """
        if checklist_path is None:
            # Find design-checklist.yaml relative to this file
            script_dir = Path(__file__).parent
            checklist_path = (
                script_dir / "resources" / "rules" / "design-checklist.yaml"
            )

        self.checklist_path = Path(checklist_path)
        self.checklist = self._load_checklist()

        # Directory for storing validated proposals
        self.proposals_dir = script_dir / ".ephemeral" / "tool-proposals"
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

    def _load_checklist(self) -> Dict[str, Any]:
        """Load and parse the design checklist."""
        if not self.checklist_path.exists():
            raise FileNotFoundError(
                f"Design checklist not found: {self.checklist_path}"
            )

        with open(self.checklist_path, "r") as f:
            return yaml.safe_load(f)

    def validate_tool_proposal(
        self,
        tool_name: str,
        purpose: str,
        layer: str,
        dependencies: List[str],
        requires_system_state_change: bool = False,
        implementation_approach: str = "",
    ) -> Dict[str, Any]:
        """
        Validate a tool proposal against the design checklist.

        This is the main validation entry point. It runs through all the
        checklist items and checks for red flags.

        Args:
            tool_name: Name of the proposed tool
            purpose: What the tool does (one sentence)
            layer: Which layer (platform/team/personal)
            dependencies: List of dependencies (tools, external services, etc.)
            requires_system_state_change: Does it modify system state?
            implementation_approach: How will it be implemented?

        Returns:
            dict: Validation results with token if approved
            {
                "valid": bool,
                "token": str,  # Only if valid
                "proposal_id": str,
                "issues": List[str],
                "warnings": List[str],
                "checklist_results": Dict[str, Any],
                "timestamp": str,
                "proposal_path": str  # Path to saved proposal
            }
        """
        results = {
            "valid": False,
            "proposal_id": str(uuid.uuid4())[:8],
            "tool_name": tool_name,
            "issues": [],
            "warnings": [],
            "checklist_results": {},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        # Run checklist validations
        checklist_results = {}

        # 1. Configuration vs Code
        config_check = self._check_configuration(
            tool_name, implementation_approach, dependencies
        )
        checklist_results["configuration"] = config_check
        if not config_check["pass"]:
            results["issues"].extend(config_check["issues"])

        # 2. Layer Placement
        layer_check = self._check_layer_placement(layer, dependencies, purpose)
        checklist_results["layer_placement"] = layer_check
        if not layer_check["pass"]:
            results["issues"].extend(layer_check["issues"])

        # 3. Dependencies
        dep_check = self._check_dependencies(dependencies, layer)
        checklist_results["dependencies"] = dep_check
        if not dep_check["pass"]:
            results["issues"].extend(dep_check["issues"])

        # 4. Ansible-first principle (if system state change required)
        if requires_system_state_change:
            ansible_check = self._check_ansible_first(implementation_approach)
            checklist_results["ansible_first"] = ansible_check
            if not ansible_check["pass"]:
                results["issues"].extend(ansible_check["issues"])

        # 5. Red flag detection
        red_flags = self._detect_red_flags(
            tool_name, implementation_approach, dependencies
        )
        checklist_results["red_flags"] = red_flags
        if red_flags["found"]:
            results["warnings"].extend(red_flags["warnings"])

        results["checklist_results"] = checklist_results

        # Determine if validation passes
        if len(results["issues"]) == 0:
            results["valid"] = True
            # Generate validation token
            token_data = {
                "proposal_id": results["proposal_id"],
                "tool_name": tool_name,
                "timestamp": results["timestamp"],
            }
            results["token"] = self._generate_token(token_data)

            # Save the proposal
            proposal_path = self._save_proposal(
                results["proposal_id"],
                {
                    "tool_name": tool_name,
                    "purpose": purpose,
                    "layer": layer,
                    "dependencies": dependencies,
                    "requires_system_state_change": requires_system_state_change,
                    "implementation_approach": implementation_approach,
                    "validation_results": results,
                },
            )
            results["proposal_path"] = str(proposal_path)

        return results

    def _check_configuration(
        self, tool_name: str, implementation: str, dependencies: List[str]
    ) -> Dict[str, Any]:
        """Check if configuration is properly externalized."""
        issues = []

        # Check for hardcoded values in implementation description
        hardcode_patterns = [
            r"staging",
            r"production",
            r"pi-k8",
            r"teleport\.tw\.ee",
            r"ALLOWED_CLUSTERS\s*=",
        ]

        for pattern in hardcode_patterns:
            if re.search(pattern, implementation, re.IGNORECASE):
                issues.append(
                    f"⚠️  Potential hardcoded configuration detected: '{pattern}'. "
                    "Consider using config/clusters.yaml or similar."
                )

        return {
            "pass": len(issues) == 0,
            "issues": issues,
            "category": "Configuration vs Code",
        }

    def _check_layer_placement(
        self, layer: str, dependencies: List[str], purpose: str
    ) -> Dict[str, Any]:
        """Validate layer placement."""
        issues = []
        valid_layers = ["platform", "team", "personal"]

        if layer.lower() not in valid_layers:
            issues.append(f"❌ Invalid layer '{layer}'. Must be one of: {valid_layers}")

        # Check layer contracts
        layer_contracts = self.checklist.get("layer_contracts", {})
        layer_config = layer_contracts.get(layer.lower(), {})

        if layer.lower() == "platform":
            # Platform layer should not depend on team-specific tools
            team_keywords = ["flux", "kustomization", "k8s-master"]
            if any(keyword in purpose.lower() for keyword in team_keywords):
                issues.append(
                    "⚠️  Platform layer tool appears to have team-specific assumptions. "
                    "Platform tools should work for ANY team."
                )

        return {
            "pass": len(issues) == 0,
            "issues": issues,
            "category": "Layer Placement",
        }

    def _check_dependencies(
        self, dependencies: List[str], layer: str
    ) -> Dict[str, Any]:
        """Check dependency structure."""
        issues = []

        # Dependencies should be abstractions, not implementations
        concrete_patterns = [
            r"directly calls.*ssh",
            r"hardcoded.*command",
            r"assumes.*exists",
        ]

        deps_str = " ".join(dependencies).lower()
        for pattern in concrete_patterns:
            if re.search(pattern, deps_str):
                issues.append(
                    f"⚠️  Dependency appears too concrete: '{pattern}'. "
                    "Consider depending on abstractions (interfaces) instead."
                )

        return {
            "pass": len(issues) == 0,
            "issues": issues,
            "category": "Dependencies",
        }

    def _check_ansible_first(self, implementation: str) -> Dict[str, Any]:
        """Check adherence to Ansible-first principle."""
        issues = []

        # If system state change is required, should use Ansible
        anti_patterns = [
            r"\.sh\s+script",
            r"bash.*install",
            r"manual.*installation",
            r"install\.sh",
        ]

        for pattern in anti_patterns:
            if re.search(pattern, implementation, re.IGNORECASE):
                issues.append(
                    f"❌ Ansible-first principle violation: '{pattern}'. "
                    "System state changes must be managed by Ansible playbooks, not shell scripts."
                )

        return {
            "pass": len(issues) == 0,
            "issues": issues,
            "category": "Ansible-First Principle",
        }

    def _detect_red_flags(
        self, tool_name: str, implementation: str, dependencies: List[str]
    ) -> Dict[str, Any]:
        """Detect anti-patterns from the red flags list."""
        warnings = []
        found_flags = []

        red_flags = self.checklist.get("red_flags", {})

        # Check for hardcoded infrastructure
        if "hardcoded_infrastructure" in red_flags:
            flag = red_flags["hardcoded_infrastructure"]
            if re.search(flag["pattern"], implementation):
                warnings.append(f"🚩 {flag['name']}: {flag['problem']}")
                found_flags.append("hardcoded_infrastructure")

        # Check for god tools (action parameters)
        if "god_tools" in red_flags:
            flag = red_flags["god_tools"]
            if re.search(r"action.*parameter", implementation, re.IGNORECASE):
                warnings.append(
                    f"🚩 {flag['name']}: Tools should be focused and single-purpose"
                )
                found_flags.append("god_tools")

        # Check for tight coupling
        deps_str = " ".join(dependencies).lower()
        if any(word in deps_str for word in ["import", "internal", "private"]):
            warnings.append(
                "🚩 Tight Coupling: Avoid importing internal/private modules from other layers"
            )
            found_flags.append("tight_layer_coupling")

        return {
            "found": len(found_flags) > 0,
            "warnings": warnings,
            "flags": found_flags,
        }

    def _generate_token(self, token_data: Dict[str, Any]) -> str:
        """Generate a validation token."""
        # Create a hash of the token data
        token_str = json.dumps(token_data, sort_keys=True)
        token_hash = hashlib.sha256(token_str.encode()).hexdigest()[:16]
        return f"valid-{token_data['proposal_id']}-{token_hash}"

    def _save_proposal(self, proposal_id: str, proposal_data: Dict[str, Any]) -> Path:
        """Save an approved proposal to disk."""
        filename = f"{proposal_id}_{proposal_data['tool_name']}.json"
        filepath = self.proposals_dir / filename

        with open(filepath, "w") as f:
            json.dump(proposal_data, f, indent=2, default=str)

        return filepath

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify a validation token.

        Args:
            token: The validation token to verify

        Returns:
            dict: Verification results
            {
                "valid": bool,
                "proposal_id": str,
                "proposal_data": Dict[str, Any],
                "message": str
            }
        """
        # Extract proposal ID from token
        parts = token.split("-")
        if len(parts) < 3 or parts[0] != "valid":
            return {
                "valid": False,
                "message": "❌ Invalid token format",
            }

        proposal_id = parts[1]

        # Find the proposal file
        proposal_files = list(self.proposals_dir.glob(f"{proposal_id}_*.json"))
        if not proposal_files:
            return {
                "valid": False,
                "proposal_id": proposal_id,
                "message": f"❌ No proposal found for ID: {proposal_id}",
            }

        # Load and verify
        with open(proposal_files[0], "r") as f:
            proposal_data = json.load(f)

        # Regenerate token to verify
        token_data = {
            "proposal_id": proposal_id,
            "tool_name": proposal_data["tool_name"],
            "timestamp": proposal_data["validation_results"]["timestamp"],
        }
        expected_token = self._generate_token(token_data)

        if token != expected_token:
            return {
                "valid": False,
                "proposal_id": proposal_id,
                "message": "❌ Token verification failed (tampered or expired)",
            }

        return {
            "valid": True,
            "proposal_id": proposal_id,
            "proposal_data": proposal_data,
            "message": "✅ Token is valid",
        }

    def list_proposals(self) -> List[Dict[str, Any]]:
        """List all validated proposals."""
        proposals = []

        for filepath in sorted(self.proposals_dir.glob("*.json")):
            with open(filepath, "r") as f:
                data = json.load(f)
                proposals.append(
                    {
                        "proposal_id": data["validation_results"]["proposal_id"],
                        "tool_name": data["tool_name"],
                        "layer": data["layer"],
                        "timestamp": data["validation_results"]["timestamp"],
                        "filepath": str(filepath),
                    }
                )

        return proposals


# Convenience function for quick validation
def validate_tool(
    tool_name: str,
    purpose: str,
    layer: str,
    dependencies: List[str],
    requires_system_state_change: bool = False,
    implementation_approach: str = "",
) -> Dict[str, Any]:
    """
    Convenience function to validate a tool proposal.

    This is the main entry point for validation.
    """
    validator = DesignValidator()
    return validator.validate_tool_proposal(
        tool_name=tool_name,
        purpose=purpose,
        layer=layer,
        dependencies=dependencies,
        requires_system_state_change=requires_system_state_change,
        implementation_approach=implementation_approach,
    )
