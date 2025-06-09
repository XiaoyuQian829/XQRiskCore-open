# core/request_context.py

from core.permissions_manager import PermissionsManager
from utils.time_utils import get_timestamps


class RequestContext:
    """
    RequestContext — User Session Container
    =======================================

    Encapsulates the identity, permissions, client scope, and governance metadata
    for a user session. Used across all modules to enforce role-based access,
    action auditing, and scoped visibility.
    """

    def __init__(
        self,
        user_id,
        role,
        permissions=None,
        source=None,
        client_id=None,
        is_active=True,
        assigned_clients=None
    ):
        # --- Identity & Role ---
        # Store the user's unique ID and their assigned role (e.g. admin, auditor)
        # Enforce deactivation checks immediately.
        pass

        # --- Client Scope ---
        # Determine which clients this user can operate on.
        # Supports single-client, multi-client, or full access (__ALL__).
        pass

        # --- Permissions ---
        # Normalize permissions into a dictionary: key → bool.
        # Legacy list-based permission structures are converted.
        pass

        # --- Session Source ---
        # Track where this session was created from: UI login, API call, background system.
        pass

        # --- Timestamping ---
        # Attach a timezone-aware timestamp for all user actions.
        # Used in audit logging, lifecycle monitoring, and expiry validation.
        pass

    def has_permission(self, action: str) -> bool:
        """
        Check whether this session includes permission for the given action key.
        Used by all access-controlled views and risk gates.
        """
        pass

    def to_dict(self):
        """
        Return a serialized snapshot of the context:
        - user_id, role, client_id
        - permissions, timestamp, source
        """
        pass

    def __repr__(self):
        """
        Developer-friendly string for logging and debug inspection.
        """
        pass

    def log_action(self, module: str, action: str, payload: dict = None, status: str = "ok"):
        """
        Record a structured user action to the audit log system.
        Includes context metadata (role, client, time, permissions).
        """
        pass


# ---------------------------------------------
# Factory: Build a Context From User Registry
# ---------------------------------------------

from users.user_registry import load_user_registry
from utils.config_loader import load_client_registry

def build_request_context(user_id: str) -> RequestContext:
    """
    System entry point: given a user_id, build their full session context.

    Resolves:
    - Role and permission set (via PermissionsManager)
    - Visible clients (from user registry)
    - Activation status and default active client

    Returns:
        RequestContext: governance-aware runtime session
    """
    pass


