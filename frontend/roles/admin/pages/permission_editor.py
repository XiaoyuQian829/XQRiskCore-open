# frontend/roles/admin/pages/permission_editor.py

REQUIRES_CLIENT_CONTEXT = False

import streamlit as st
import yaml
import io
from collections import defaultdict
from core.request_context import RequestContext
from users.role_permissions import PERMISSION_OWNERSHIP
from core.permissions_manager import PermissionsManager
from utils.user_action import UserAction
from audit.action_logger import record_user_action, record_user_view

pm = PermissionsManager()

def render(ctx: RequestContext):
    if not ctx.has_permission("admin.modify_role_permission"):
        st.warning("⚠️ You do not have permission to modify role permissions.")
        return

    record_user_view(ctx, module="permission_editor", action=UserAction.VIEW_PERMISSION_EDITOR)

    st.markdown("""
        <h3 style='font-size: 1.7rem; margin-bottom: 0.3rem;'>🛡️ Role Permission Editor</h3>
        <div style='font-size: 0.9rem; margin-bottom: 1rem; color: #555;'>
            Select a role to review and modify its module-based permissions. <code>🔒</code> marks system-owned permissions and cannot be edited.
        </div>
    """, unsafe_allow_html=True)

    all_roles = pm.get_all_roles()
    selected_role = st.selectbox("Select Role", all_roles, key="selected_role")

    prev_role = st.session_state.get("last_role", None)
    if prev_role != selected_role:
        if st.session_state.get("just_saved_role") != selected_role:
            keys_to_delete = [k for k in st.session_state if k.startswith(f"perm_{prev_role}__")]
            for k in keys_to_delete:
                del st.session_state[k]
        st.session_state.last_role = selected_role

    current_perms = pm.get_role_permissions(selected_role)
    all_permissions = sorted({k for r in all_roles for k in pm.get_role_permissions(r)})

    grouped_permissions = defaultdict(list)
    for perm in all_permissions:
        grouped_permissions[perm.split(".")[0]].append(perm)

    updated = {}
    for module in sorted(grouped_permissions.keys()):
        perms = grouped_permissions[module]
        with st.expander(f"📂 {module.capitalize()} ({len(perms)})", expanded=True):
            for perm in sorted(perms):
                locked = PERMISSION_OWNERSHIP.get(perm) == selected_role
                default_val = current_perms.get(perm, False)
                checked = st.checkbox(
                    label=f"`{perm}`" if not locked else f"`{perm}` 🔒",
                    value=default_val,
                    key=f"perm_{selected_role}__{perm}",
                    disabled=locked,
                    help="This permission is locked and cannot be modified." if locked else None
                )
                updated[perm] = checked

    st.divider()

    col1, col2 = st.columns([0.4, 0.6])
    with col1:
        if st.button("💾 Save Changes", use_container_width=True):
            pm.set_role_permissions(selected_role, updated)
            pm.save()
            record_user_action(ctx, module="permission_editor", action="modify_role_permissions", payload={"role": selected_role})
            st.session_state["just_saved_role"] = selected_role
            st.toast(f"✅ Permissions for '{selected_role}' saved successfully.")

            # ✅ 刷新当前 session 的权限上下文（如果编辑的是自己）
            if "request_ctx" in st.session_state:
                current_user = st.session_state["request_ctx"].user_id
                current_role = st.session_state["request_ctx"].role
                if selected_role == current_role and ctx.user_id == current_user:
                    from core.request_context import build_request_context
                    st.session_state["request_ctx"] = build_request_context(ctx.user_id)
                    st.rerun()

    with col2:
        with st.expander("📤 Export YAML"):
            yaml_export = yaml.dump({selected_role: updated}, sort_keys=True)
            st.download_button(
                "Download Permissions",
                data=io.BytesIO(yaml_export.encode()),
                file_name=f"{selected_role}_permissions.yaml",
                mime="text/yaml"
            )



