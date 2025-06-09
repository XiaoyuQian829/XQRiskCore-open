# core/permissions_manager.py

import yaml
import os

# Default file path for the role-permission matrix
DEFAULT_PATH = "users/role_permissions.yaml"


class PermissionsManager:
    """
    PermissionsManager loads, manages, and persists role-based access control (RBAC)
    configurations. It provides CRUD operations for role-permission pairs and ensures
    backward compatibility with legacy list-based YAML formats.

    This class powers the frontend visibility and feature access across all user roles.
    """

    def __init__(self, path: str = DEFAULT_PATH):
        # YAML file path containing role-permission mappings
        self.path = path

        # Internal permission dictionary: role → {permission_key: bool}
        self.permissions = {}

        # Load permissions on initialization
        self.load()

    def load(self):
        """
        Load the permission matrix from YAML file.
        If the file does not exist or is empty, fall back to an empty structure.
        """
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                self.permissions = yaml.safe_load(f) or {}
        else:
            self.permissions = {}

    def reload(self):
        """
        Force a reload from disk, discarding any in-memory changes.
        Useful if permissions were modified externally.
        """
        self.load()

    def save(self):
        """
        Save the current permission matrix to disk in YAML format.
        This will overwrite the existing file at self.path.
        """
        with open(self.path, "w") as f:
            yaml.dump(self.permissions, f, sort_keys=False)

    def get_all_roles(self):
        """
        Return a list of all defined roles in the current permission matrix.
        """
        return list(self.permissions.keys())

    def get_role_permissions(self, role: str) -> dict:
        """
        Return the permission map for a given role.

        Supports backward compatibility:
        - If the stored format is a list, convert to dict with True values.
        - If already a dict, return as-is.

        Args:
            role (str): Role name

        Returns:
            dict: Permission key → boolean flag
        """
        raw = self.permissions.get(role, {})
        if isinstance(raw, list):
            return {p: True for p in raw}
        if isinstance(raw, dict):
            return raw
        return {}

    def set_role_permissions(self, role: str, perms: dict):
        """
        Overwrite all permissions for a given role.

        Args:
            role (str): Role name
            perms (dict): Full permission set (key → bool)
        """
        self.permissions[role] = perms

    def update_permission(self, role: str, key: str, value: bool):
        """
        Update or add a single permission entry for a given role.

        Args:
            role (str): Role name
            key (str): Permission key
            value (bool): Permission granted or denied
        """
        if role not in self.permissions:
            self.permissions[role] = {}
        elif isinstance(self.permissions[role], list):
            # Upgrade legacy list structure to dict format
            self.permissions[role] = {p: True for p in self.permissions[role]}
        self.permissions[role][key] = value

    def delete_permission(self, role: str, key: str):
        """
        Remove a specific permission key from a given role.

        Args:
            role (str): Role name
            key (str): Permission key to remove
        """
        perms = self.get_role_permissions(role)
        if key in perms:
            del perms[key]
            self.permissions[role] = perms

    def has_permission(self, role: str, key: str) -> bool:
        """
        Check whether a given role has permission for a specific key.

        Args:
            role (str): Role name
            key (str): Permission key

        Returns:
            bool: True if allowed, False otherwise
        """
        return self.get_role_permissions(role).get(key, False)

    def export(self) -> dict:
        """
        Export the current permission matrix in-memory (without writing to disk).

        Returns:
            dict: Full role → permission map
        """
        return self.permissions

    def import_permissions(self, new_data: dict):
        """
        Replace the current permission structure with a new one,
        and persist it to disk.

        Args:
            new_data (dict): New permission matrix
        """
        self.permissions = new_data
        self.save()
