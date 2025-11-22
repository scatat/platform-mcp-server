# PI Team Operating Rules

This document contains rules specific to the Platform Integrations (PI) team.

## 1. Teleport & Kubernetes Safety (`tsh`, `kubectl`, `flux`)

- **Rule 1.1 (Always Verify Cluster)**: Before using any `tsh` command, you **must** first run `tsh status` to verify the active Teleport cluster. Present the active cluster and ask for confirmation before proceeding.
- **Rule 1.2 (Default to Staging)**: Always assume operations are for a **non-production** environment unless explicitly specified.
- **Rule 1.3 (Production Lockout)**: **Never** run a `tsh ssh` or `tsh kube` command against a cluster that appears to be production. For production environments, generate the command for me to review and run myself. This ensures the action is captured by Teleport's audited session recording under my identity.
- **Rule 1.4 (Assume `sudo`)**: Assume that all `kubectl` and `flux` commands run on a remote Kubernetes node require `sudo`.

## 2. Pull Request (PR) Process

- **Rule 2.1 (Discover and Use PR Template)**: Before creating a pull request, you **must** search the repository for an existing PR template (e.g., `.github/pull_request_template.md`). If found, you must use it.
- **Rule 2.2 (Infer from Existing PRs)**: If no template file exists, you **must** search for the most recently merged pull requests to infer the correct format.
- **Rule 2.3 (Assign and Label)**: When creating a pull request, you **must** assign it to the user who initiated the request and add the label `change: standard`.
