# XQRiskCore - RBAC (Role-Based Access Control) User Guide

XQRiskCore's RBAC system is engineered to meet the stringent demands of the financial industry, prioritizing **institutional-grade security, flexibility, and auditability.**

---

## Core Principles: Building Wall Street-Grade Access Control

XQRiskCore's RBAC system is built upon four foundational principles, ensuring superior access management in complex and highly regulated financial environments:

### 1. Extreme Auditability & Immutability
The system ensures all user actions are meticulously recorded and cannot be altered. This provides an irrefutable audit trail for internal risk control, external regulatory compliance, and post-incident accountability. Every operation, regardless of privilege level, leaves a clear and traceable record.

### 2. Flexible & Real-time Permission Management
In the fast-paced financial markets, the system supports dynamic, hot-swappable roles and permissions. This allows for immediate adjustments without downtime or service restarts, ensuring rapid response to evolving business and regulatory requirements.

### 3. Granular Control & Client Segmentation
With precise, operation-level permission control and sophisticated management of users, roles, and clients, the system strictly adheres to the principles of Separation of Duties and Least Privilege, safeguarding data integrity and maintaining clear operational boundaries.

### 4. Comprehensive Compliance Readiness
Every aspect of the system's design is underpinned by the need to meet global financial regulations (e.g., SOX, MiFID II, GDPR). This ensures financial institutions can unequivocally demonstrate the compliance of every single operation.

---

## RBAC Features & Examples

### 1. User & Role Management

The system supports user activation, deactivation, and comprehensive management, strictly adhering to role assignment principles.

* **Admin Can Activate/Deactivate Users:** Administrators have the authority to set users as `inactive` or reactivate them. This provides essential account lifecycle management and security control.

    <img width="1026" alt="Inactive user managed by admin" src="assets/03/user_inactive.png" />

* **System User List:** The system clearly displays the status and assigned roles for all users.

    <img width="553" alt="System view of user status" src="assets/03/login_fail.png" />

---

### 2. Role Modifiability

The system empowers administrators with the flexibility to adjust roles, adapting to evolving business needs.

* **Dynamic Role Permission Adjustment:** Existing roles (e.g., `Risker`, `Trader`, `Auditor`) can have their names and associated permissions modified dynamically, without requiring redeployment.

    <img width="873" alt="Roles are modifiable" src="assets/03/role_adjust.png" />

---

### 3. Fine-Grained Client Segmentation

The RBAC system supports linking specific clients to authorized roles, ensuring robust data isolation and clear segregation of duties.

* **Admin-Set Client Permissions:** Only clients configured by an administrator (e.g., `JerryY` in the example) can be assigned to a specific account manager role.

    <img width="1279" alt="Screenshot 2025-06-09 at 10 14 44 PM" src="assets/03/client_permit.png" />

* **Selectable Clients Under Current Account:** Users can only view and select clients pre-configured by an administrator, within the scope of their currently authorized account.

    <img width="316" alt="Clients selectable under current account" src="assets/03/select_client.png" />

---

### 4. Real-time Permissions & Immutable Audits

This is a cornerstone of our RBAC system, ensuring both extreme flexibility and rigorous audit trails.

* **Hot-Swappable Role Permissions:** Permission changes take effect **in real-time**, eliminating the need for service restarts and ensuring system agility in response to market shifts.
  
    <img width="927" alt="Screenshot 2025-06-08 at 5 17 43 PM" src="assets/03/role_permit.png" />

* **Flexible Permission Assignment:** `admin` or any other role can be granted any combination of permissions, including all permissions, to meet specific operational requirements.

    <img width="296" alt="Admin and any role can have all permissions" src="assets/03/all_permissons.png" />

* **Mandatory Audit Logging:** All user actions and view operations are **faithfully and immutably recorded** by the system. This is critical for post-facto traceability and accountability, meeting the highest audit standards in the financial industry.

    <img width="968" alt="Screenshot 2025-06-08 at 4 26 49 PM" src="assets/03/user_logs.png" />
    
* **Precise Attribution for Temporary Permissions:** Even if an `admin` or another role temporarily gains permission to `place order`, the `trader` field within the `intent` will **faithfully record the actual operating username** (e.g., `admin`) and cannot be modified. This resolves accountability issues for elevated privileges and prevents "invisible" operations.

    <img width="428" alt="Admin or any role can temporarily place order, logged faithfully" src="assets/03/buy_intent.png" />

---

### 5. Continuous Activity & Permission Review

The system performs permission checks and records actions at every critical point within the user's operational path.

* **Permission Review on UI Navigation:** Each time a user navigates between interfaces, the system conducts a real-time permission review and logs the activity. This ensures immediate permission validity and provides a comprehensive audit trail for every user interaction.

    <img width="375" alt="Permissions checked on every interface switch" src="assets/03/permit_check.png" />

---

