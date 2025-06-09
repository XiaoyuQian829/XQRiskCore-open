# frontend/roles/admin/pages/user_manager.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
import os
import yaml
import pandas as pd
from admin.user_registry import add_user, delete_user, list_users
from core.request_context import RequestContext
from utils.config_loader import load_client_registry
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

DEFAULT_PROTECTED_USERS = {"admin", "trader1", "risker", "auditor"}

def render(ctx: RequestContext):
    if not ctx.has_permission("admin.manage_users"):
        st.error("Access denied: insufficient permissions.")
        return

    record_user_view(ctx, module="user_manager", action=UserAction.VIEW_USER_MANAGER)

    st.markdown("""
        <h3 style='margin-bottom: 1rem; font-size: 1.7rem;'>🧑‍💼 User Access Control</h3>
        <div style='font-size: 0.9rem; color: #bbb;'>Manage platform users, assign roles, and control account access status.</div>
    """, unsafe_allow_html=True)

    # === View & Edit Users ===
    with st.expander("🔎 Registered Users", expanded=True):
        users = list_users()

        if users:
            styled_data = []
            for i, (u, info) in enumerate(users.items(), start=1):
                active_icon = "✅" if info.get("active", True) else "❌"
                styled_data.append({
                    "#": i,
                    "Username": f"**{u}**",
                    "Role": info.get("role"),
                    "Email": info.get("email"),
                    "Client": info.get("client_id"),
                    "Active": active_icon
                })

            df = pd.DataFrame(styled_data)
            st.dataframe(df.set_index("#"), use_container_width=True)

            selected_user = st.selectbox("Select user to edit", list(users.keys()), key="edit_user_selectbox")
            user_data = users[selected_user]

            st.markdown(f"**Editing user:** `{selected_user}`")

            email = st.text_input("Email", value=user_data.get("email", ""), key="edit_user_email")
            phone = st.text_input("Phone", value=user_data.get("phone", ""), key="edit_user_phone")
            timezone = st.text_input("Timezone", value=user_data.get("timezone", "UTC"), key="edit_user_timezone")

            if selected_user in DEFAULT_PROTECTED_USERS:
                st.selectbox(
                    "Role",
                    ["trader", "risker", "auditor", "admin"],
                    index=["trader", "risker", "auditor", "admin"].index(user_data["role"]),
                    disabled=True,
                    key="edit_user_role_locked"
                )
                new_role = user_data["role"]

                st.checkbox("Active", value=user_data.get("active", True), disabled=True, key="edit_user_active_locked")

                client_registry = load_client_registry()
                client_options = ["__ALL__"] + list(client_registry.keys())
                current_client = user_data.get("client_id", "__ALL__")
                st.selectbox(
                    "Client ID",
                    client_options,
                    index=client_options.index(current_client),
                    key="edit_user_client_id_locked",
                    disabled=True
                )

                st.warning("System default users are protected and cannot have their access configuration modified.")
                is_active = user_data.get("active", True)
                client_id = user_data.get("client_id", "__ALL__")
            else:
                new_role = st.selectbox(
                    "Role",
                    ["trader", "risker", "auditor", "admin"],
                    index=["trader", "risker", "auditor", "admin"].index(user_data["role"]),
                    key="edit_user_role"
                )
                st.info("You may assign or change the role for this user.")

                is_active = st.checkbox("Active", value=user_data.get("active", True), key="edit_user_active")

                client_registry = load_client_registry()
                client_options = ["__ALL__"] + list(client_registry.keys())
                current_client = user_data.get("client_id", "__ALL__")

                client_id = st.selectbox(
                    "Client ID",
                    client_options,
                    index=client_options.index(current_client),
                    key="edit_user_client_id"
                )

            if st.button("💾 Update User Info", key="update_user_button"):
                users[selected_user]["role"] = new_role
                users[selected_user]["email"] = email
                users[selected_user]["phone"] = phone
                users[selected_user]["timezone"] = timezone

                if selected_user not in DEFAULT_PROTECTED_USERS:
                    users[selected_user]["active"] = is_active
                    users[selected_user]["client_id"] = client_id

                with open("users/user_registry.yaml", "w") as f:
                    yaml.dump(users, f)

                record_user_action(ctx, module="user_manager", action="update_user", payload={
                    "username": selected_user,
                    "role": new_role,
                    "client_id": client_id,
                    "active": is_active
                })

                st.success(f"User '{selected_user}' updated.")
                st.rerun()
        else:
            st.info("No users found in the registry.")

    # === Add New User ===
    with st.expander("➕ Add New User"):
        username = st.text_input("Username *", key="add_user_username")
        password = st.text_input("Password *", type="password", key="add_user_password")
        role = st.selectbox("Role *", ["trader", "risker", "auditor", "admin"], key="add_user_role")

        client_registry = load_client_registry()
        client_options = ["__ALL__"] + list(client_registry.keys())

        client_id = st.selectbox("Client ID", client_options, index=0, key="add_user_client_id")

        st.markdown("Optional Details")
        email = st.text_input("Email", key="add_user_email")
        phone = st.text_input("Phone", key="add_user_phone")
        language = st.selectbox("Preferred Language", ["en", "zh"], key="add_user_language")
        timezone = st.text_input("Timezone", value="UTC", key="add_user_timezone")

        if st.button("✅ Create User", key="add_user_button"):
            if not username or not password:
                st.warning("Username and password are required.")
                return

            success = add_user(
                username=username,
                password=password,
                role=role,
                email=email,
                phone=phone,
                client_id=client_id,
                preferred_language=language,
                timezone=timezone
            )

            record_user_action(ctx, module="user_manager", action="create_user", payload={
                "username": username,
                "role": role,
                "client_id": client_id,
                "success": success
            })

            if success:
                st.success(f"User '{username}' created with role '{role}'.")
                st.rerun()
            else:
                st.warning(f"User '{username}' already exists.")

    # === Delete User (View Only Mode) ===
    with st.expander("🛑 Delete User (View Only)"):
        st.markdown("This section is for demonstration only. Delete functionality is disabled.")
        st.text_input("Username to delete", value="(disabled)", disabled=True, key="delete_user_input")
        st.checkbox("Confirm deletion", value=False, disabled=True, key="delete_user_confirm")
        st.button("Delete User", disabled=True, key="delete_user_button")



"""
    # === Delete User ===
    with st.expander("Delete User"):
        user_to_delete = st.text_input("Username to delete")
        confirm = st.checkbox("Confirm deletion")

        if st.button("Delete User"):
            if not confirm:
                st.warning("You must confirm deletion.")
                return

            success = delete_user(user_to_delete)

            ctx.log_action("admin", "delete_user", {
                "username": user_to_delete,
                "success": success
            })

            if success:
                st.success(f"User '{user_to_delete}' deleted.")
                st.rerun()
            else:
                st.error(f"User '{user_to_delete}' not found.")
"""