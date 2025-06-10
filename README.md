# XQRiskCore

> **A governance-grade risk control engine for trading** — with unified trade approval, structured audit logging, role-based access control, and multi-layer enforcement.

> ⚠️ Tired of projects that ask you to install before you understand?  
> XQRiskCore flips the script: **Try it first — then see how deep the governance goes.**

---

🚀 Jump in as an admin, trader, or auditor — no setup required.  
🎯 Live Demo → [xqriskcore-production.up.railway.app](https://xqriskcore-production.up.railway.app)

<p align="center">
  <img src="assets/xq_login.png" width="600" />
</p>

*Deployed on Railway. Optimized for responsiveness, audit visibility, and governance transparency.*

---

## ⚙️ Built to Govern, Not Just Execute

**XQRiskCore** enforces policy before trades happen — not after they go wrong.

Every trade is routed through a structured lifecycle:
- ⛓️ From submission to approval  
- 🧾 From scoring to audit logging  
- 🛡️ From detection to multi-layer safeguards

Whether triggered by a trader, a strategy, or a rebalance engine —  
**every action is accountable, every override is recorded, and every permission is scoped.**

> **This is not order routing. It’s responsibility routing.**

---

## 📑 Table of Contents

- [🧭 System Origins & Design Philosophy](#-system-origins--design-philosophy)
- [📚 Institutional Inspirations](#-institutional-inspirations)
- [✅ Core Capabilities](#-core-capabilities)
  - [🔁 Unified Trade Flow](#-unified-trade-flow)
  - [🧠 Dual-Path Risk Control](#-dual-path-risk-control)
  - [🧱 Role-Based Governance (RBAC)](#-role-based-governance-rbac)
  - [🧾 Structured Behavioral Logging](#-structured-behavioral-logging)
- [🛡️ Emergency Guard Layer](#-emergency-guard-layer)
- [🧩 System Architecture](#-system-architecture)
- [🔌 Service Interface Abstraction](#-service-interface-abstraction)
- [🧮 Functional Overview](#-functional-overview)
- [📌 Use Cases](#-use-cases)
- [🚧 Roadmap & Evolution](#-roadmap--evolution)
- [🌱 Evolution by Design](#-evolution-by-design)
- [🧬 Who Am I?](#-who-am-i)
- [🤝 Collaboration & Opportunities](#-collaboration--opportunities)
- [🙏 Acknowledgments](#-acknowledgments)
- [📄 License](#-license)
- [📬 Contact](#-contact)

---

## 🧭 System Origins & Design Philosophy

**XQRiskCore wasn’t built to imitate trading tools — it was architected to enforce institutional-grade governance.**

Its design foundations are:

- To **embed compliance** directly into the trading process  
- To **log structured decisions**, not just outcomes  
- To **restrict permissions** based on role and scope  
- To **monitor risk continuously**, not retroactively

What sets XQRiskCore apart is clarity: every decision is traceable, every rule is testable, and every action is governed by policy.

---

🎧 **Want to hear what a system of discipline sounds like?**  
Listen to the official theme track — composed by AI, inspired by structure:

> 🔊 [Watch: The Core — Theme of XQRiskCore](https://youtu.be/OsUe84mkLhg)

Let the music carry the logic.  
**Structured. Watchful. Unyielding.**

---

## 📚 Institutional Inspirations

While XQRiskCore is independently built, its architecture is inspired by world-class risk systems:

✅ *Landed in v1.0 (beta):*  
- **BlackRock Aladdin** — Unified trade flow + Role-based governance and audit attribution  
- **J.P. Morgan Vega / RaaS** — Dual-path risk enforcement (pre/post trade)  
- **Goldman Sachs Marquee** — Structured action logging and behavioral traceability  

🧪 *Planned in future iterations:*  
- **Beacon / Vega** — Rule hot-swapping, version control for risk policies  
- **Bridgewater / Two Sigma** — Adaptive scoring and self-tuning risk logic

---

## ✅ Core Capabilities

### 1. 🔁 Unified Trade Flow — One Pipe for All Trades

Unlike most systems that separate manual, strategy, and rebalance trades,  
**XQRiskCore unifies them into a single pipeline** — one that enforces **the same approval logic**, **risk checks**, and **audit trace**.

No trade escapes the flow.  
Every source — whether it’s a button click, a strategy trigger, or a scheduled rebalance — must go through:

→ Intent → Risk Signal → Approval → Execution → Audit → Post-Trade Monitoring

#### 📊 Figure 1: XQRiskCore Risk-Controlled Trade Lifecycle
![Trade Flow](assets/xq_tradeflow.png)

🧩 Want to understand how this unified trade pipeline actually works under the hood?

📄 [See `01_unified_trade_flow.md`](01_unified_trade_flow.md)

Included:

- 🎯 The philosophy behind `TradeIntent` — “a trade is a trade, regardless of source”
- 📦 Side-by-side examples of manual vs strategy-generated intents
- 🔒 How pre-block mechanisms (Kill Switch, Silent Mode) intercept trades before execution
- ✅ How the Risk Approval Engine evaluates score, volatility, and VaR
- 📊 Full trade lifecycle from intent → approval → execution → audit
- 🧠 How this structure ensures **policy consistency**, **traceability**, and **enforceable compliance**

---

### 2. 🧠 Dual-Path Risk Control Architecture

XQRiskCore enforces risk across two complementary paths:

#### 1️⃣ Pre-Trade Approval

Every trade — whether triggered manually, algorithmically, or via rebalancing — must pass a unified approval gate  
before it is executed. This is the core of XQRiskCore’s institutional-grade risk governance.

##### 🔁 Approval Flow Diagram

```text
          ┌──────────────────┐
          │ TradeIntent      │
          └────────┬─────────┘
                   ▼
        ┌────────────────────────────┐
        │ Is this a SELL action?     │
        └───────┬─────────────▲──────┘
                ▼             │
      ┌────────────────┐      │
      │ Check holdings │      │
      └─────┬──────────┘      │
            ▼                 │
   ┌──────────────┐     ┌──────────────┐
   │ Enough shares│     │ Not enough   │
   │ → Approve    │     │ → Reject     │
   └──────────────┘     └──────────────┘

                   ▼ (If BUY)
       ┌────────────────────────────┐
       │ Fetch price + estimate cost│
       └───────┬────────────────────┘
               ▼
       ┌────────────────────────────┐
       │ Enough cash?               │
       └───────┬───────────────┬────┘
               ▼               ▼
          Fetch signals     Reject trade

               ▼
         Evaluate:
         - score
         - volatility
         - VaR

               ▼
          Decision:
          APPROVE / LIMIT / REJECT

               ▼
       Generate approval response
```

Try it:
- 👉 [**Login as `trader1` (Role: Trader)**](https://xqriskcore-production.up.railway.app)  
  → Go to **`Trader: Manual Trade Submit`**
![Audit Screenshot](assets/xq_submit_trade.png)  
  → Select a client and submit a trade form to trigger the full risk approval flow.
- 👉 [**Login as `quant_researcher` (Role: Quant Researcher)**](https://xqriskcore-production.up.railway.app)  
  → Activate a strategy and observe how it routes through the same unified trade lifecycle.


- 👉 [**Login as `auditor` (Role: Auditor)**](https://xqriskcore-production.up.railway.app)  
  → Go to **`Audit: Decision Records`**  
  → Review detailed decision records, including approvals, rejections, risk scores, and override flags.
![Audit Detail](assets/xq_decision_logs.png)

---

#### 🧯 2️⃣ Post-Trade Monitoring — Risk Trigger System

After a trade is approved and executed, XQRiskCore continuously monitors live positions using two layered engines:

- ⚡ **IntradayTriggerEngine** — Real-time monitoring during market hours  
- 🌙 **SilentTriggerEngine** — End-of-day (EOD) review to enforce lockouts or cooldowns

If any predefined **account-level** or **asset-level** thresholds are breached, the system will trigger **Silent Mode** (cooldown) or a full **Kill Switch** (lockdown) — ensuring risk is reined in before it spirals.

##### 🧮 Account-Level Risk Triggers

| 🔍 Condition                         | 🧾 Metric Used                  | ⚠️ Action              | 🛠️ Module               |
|-------------------------------------|---------------------------------|-------------------------|--------------------------|
| Intraday drawdown ≤ **-5%**         | `drawdown` vs. `peak_value`     | Silent Mode (2 days)    | IntradayTriggerEngine    |
| Daily return ≤ **-5%**              | `daily_return`                  | Silent Mode (2 days)    | SilentTriggerEngine      |
| Monthly return ≤ **-10%**           | `monthly_return`                | Silent Mode (until EOM) | SilentTriggerEngine      |
| Consecutive losing days ≥ **3**     | `consecutive_losses`            | Silent Mode (1 day)     | SilentTriggerEngine      |

> 💡 These rules act as **portfolio-level brakes**, especially when trader behavior, exposure concentration, or market turmoil cause repeated or compounding losses.

##### 📦 Asset-Level Risk Triggers

| 🔍 Condition                               | 🧾 Metric Used                | 📉 Threshold   | 🧊 Lock Duration | 🛠️ Trigger Module(s)                         |
|-------------------------------------------|-------------------------------|----------------|------------------|------------------------------------------------|
| Position drawdown ≤ **-7%**               | `pos_drawdown`                | -7%            | 3 days           | IntradayTriggerEngine                          |
| 3-day cumulative drawdown ≤ **-10%**      | `drawdown_3d`                 | -10%           | 7 days           | SilentTriggerEngine                            |
| Live drawdown ≤ **-15%**                  | `drawdown_pct`                | -15%           | 7 days           | SilentTriggerEngine                            |
| Consecutive down days ≥ **3**             | `consecutive_down_days`       | 3              | 7 days           | Intraday + SilentTriggerEngine                 |
| Single-day move ≥ **±8%**                 | `(cur - prev) / prev`         | 8%             | 7 days           | Intraday + SilentTriggerEngine                 |
| Most recent slippage ≥ **0.5%**           | `last_slippage_pct`           | 0.5%           | 7 days           | Intraday + SilentTriggerEngine                 |

> 📌 These asset-specific rules prevent **repeat exposure to stressed instruments**, and build in slippage-sensitive protection.

📄 [See `02_intray&&daily_trigger.md`](02_intray&&daily_trigger.md)  
Includes:

- 🛰️ How `IntradayTriggerEngine` detects and blocks live risks during market hours  
- 🌙 How `SilentTriggerEngine` enforces cooldowns and slippage rules after market close  
- 🚦 Dual-stage enforcement design for round-the-clock protection  
- ⚡ Thresholds for drawdown, volatility, slippage, and behavioral anomalies  
- 🔁 Integration with audit logs, manual override, and per-client scan frequency  

##### 🧠 Future Enhancements (Planned)

- **Black Swan Handling**: e.g., S&P500 drops > 5% in one day → system-wide KillSwitch  
- **Slow Burn Alerting**: 5 small losing days without major drops → cumulative risk lockdown  

#### 🧬 Closed-Loop Monitoring Philosophy

> Approve only what deserves to go through.  
> Monitor everything that actually did.

XQRiskCore’s post-trade system turns **reactive logging** into **proactive governance** —  
ensuring that high-risk behavior is not just flagged, but automatically countered with structural circuit breakers.

---

### 3. 🧱 Role-Based Governance (RBAC)

| Functional Domain                            | Assigned Role         | Status         |
|---------------------------------------------|------------------------|----------------|
| ✅ System Configuration & Access Control     | `admin`                | ✅ Implemented |
| ✅ Manual Trade Execution                    | `trader`               | ✅ Implemented |
| ✅ Risk Approval & Rule Enforcement          | `risker`               | ✅ Implemented |
| ✅ Log Auditing & Behavioral Traceability    | `auditor`              | ✅ Implemented |
| ✅ Strategy Research & Factor Optimization   | `quant_researcher`     | ✅ Implemented |
| 🟡 Report Generation & Performance Analysis  | `reporter`             | 🔧 Coming Soon |
| 🟡 Compliance & Manual Risk Intervention     | `compliance_officer`   | 🔧 Coming Soon |
| 🟡 Strategy Signal Execution Agent           | `strategy_agent`       | 🔧 Coming Soon |

Each role is **permission-scoped**, **identity-linked**, and **behavior-tracked**, ensuring clean separation of duties and full accountability.

#### 🔐 Core Principles of Permission & Governance Design

- ✅ **Who can see what** — controls **information leakage risk**  
- ✅ **Who can click which button** — acts as the **final defense** against unauthorized operations  
- ✅ **Who ran a strategy or modified a threshold** — becomes the **accountability chain** when risks surface later  
- ✅ **Permission logs + Action logs** — form the **foundation for compliance reporting** and regulatory clarity  

This governance design ensures that every operation is **traceable, auditable, and justifiable**, reflecting institutional-level discipline in a modular, developer-owned system.

#### 🧑‍💼 Admin Console Highlights

- 👉 [**Login as `admin` (Role: Admin)**](https://xqriskcore-production.up.railway.app)  
  → Go to **`Admin → User & Role Manager`**  
  → Manage clients, assign roles, and activate/deactivate users in a secure, controlled interface.

⬇️ **Client & User Management Interface**  
<img width="1304" alt="Client/User Management" src="assets/xq_user_manager.png" />

- 👉 [**Still as `admin`**](https://xqriskcore-production.up.railway.app)  
  → Go to **`Admin → Role Permission Matrix`**  
  → Review and configure role-specific access rights with full visibility.

⬇️ **Permission Control Matrix View**  
<img width="1321" alt="Permission Matrix" src="assets/xq_role_permission.png" />

📄 [See `03_rbac.md`](03_rbac.md)  
Includes:

- 🛡️ Core principles for Wall Street-grade access control: auditability, flexibility, and compliance  
- 👤 How admins manage users and dynamically assign or revoke roles in real time  
- 🧩 Support for per-client segmentation and granular permission scoping  
- 🔄 Hot-swappable permission changes without system restarts  
- 🧾 Immutable audit logging of all user actions and temporary privilege elevations  
- 🔍 Real-time permission checks during every interface interaction
---

### 4. 🧾 Structured Behavioral Logging

XQRiskCore logs **every user and system action** as structured metadata — enabling traceability, compliance, and post-trade forensics.

#### 🧩 Action Types

| Type     | Description                      | Example                                |
|----------|----------------------------------|----------------------------------------|
| `view`   | Passive interactions             | Opened a dashboard                     |
| `action` | User-initiated operations        | Submitted a trade                      |
| `system` | Automated system behavior        | Triggered Silent Mode                  |

#### 🗂️ File Format & Storage

Logs are saved in newline-delimited JSON (`.jsonl`), partitioned by role, user, and date:

```
audit/user_action_logs/{role}/{user_id}/{YYYY-MM-DD}/events.jsonl
```


Each file captures timestamped, structured records.

#### 🔍 Admin Log Viewer

- 👉 [Login as `admin1`](https://xqriskcore-production.up.railway.app) → `Admin → User Action Logs`  
  → Filter by user or role to view actions: **viewed**, **submitted**, **overrode**, or **rejected** — all immutably stored.

⬇️ UI Preview  
<img width="1304" alt="User Action Log Viewer" src="assets/xq_user_logs.png" />

#### 🧠 Why It Matters

Risk officers don’t log for vanity — they log for **moments that matter**:

- 🕵️ Regulatory investigations  
- 🧾 Internal audits  
- ⚖️ Disputes & legal defense  
- 💼 Board accountability

Logs aren’t debugging tools — they’re **compliance weapons**.

#### 📌 Logged Fields

Each action includes:

- `user_id` – who did it  
- `timestamp` – when  
- `module` – where  
- `action` – what  
- `status`, `override_flag` – approved, rejected, bypassed  
- `trace_path` – who was involved  

These feed:

- 🔍 Anomaly detection  
- 📊 Risk reporting  
- 🧠 Strategy attribution  
- 🧾 Compliance tracebacks

---

## 🛡️ Emergency Guard Layer

XQRiskCore’s final line of defense — enforcing **stability**, **audit integrity**, and **strategy discipline**, even under failure or attack.

It’s designed to **fail safe**, not fail silently.

### ✅ Active Safeguards

| Module                | Function                                                        | Status    |
|-----------------------|------------------------------------------------------------------|-----------|
| `SystemGuard`         | Blocks execution if core services (API/data) go down            | ✅ Active |
| `StrategyThrottler`   | Suspends overly frequent or failing strategies                  | ✅ Active |
| `TradeAuditFailSafe`  | Cancels trades if audit logs cannot persist                     | ✅ Active |
| `KillSwitchManager`   | Locks accounts/assets on risk breach                            | ✅ Active |
| `runtime_controls.py` | UI trigger for emergency lockdowns                              | ✅ Active |

These guards keep the system **governable, observable, and survivable** — even when strategies break or infrastructure degrades.

📄 [See `04_emergency_guard_layer.md`](04_emergency_guard_layer.md)  
Covers:

- 🛡️ Failure containment: audit loss, system outages, runaway logic  
- ⚙️ Modules: `SystemGuard`, `KillSwitchManager`, `AuditFailSafe`  
- 🔁 Lifecycle hooks: pre-trade, post-trade, override-stage  
- 🔍 Full-traceability across manual, strategy, and auto execution  
- 🔒 Planned: circuit breakers, alerting, privileged override audits

---

## 🧩 System Architecture

The system follows a four-layer design:

| Layer Name                   | Role Description                                                                 | Key Modules & Files                                                                                  |
|-----------------------------|-----------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| **1. Data & Signal Layer**  | Market data ingestion, portfolio metrics, risk signal generation                 | `market_data/`, `utils/`, `risk_engine/signals/`, `clients/*/snapshots/portfolio_state.json`         |
| **2. Risk Engine & Approval Layer** | Risk scoring, rule enforcement, trade blocking via KillSwitch/Silent Mode        | `risk_engine/`, `risk_engine/signals/`, `clients/*/config/asset_config.yaml`                         |
| **3. Strategy Module Layer**| Trade idea generation via strategies or manual input                             | `strategy/`, `frontend/roles/trader/pages/trade_form.py`, `scheduler/rebalance_scheduler.py`         |
| **4. Execution & Audit Layer** | Trade execution, audit logging, lifecycle traceability                           | `services/trade_flow.py`, `core/execution/`, `audit/`, `clients/*/audit/`, `frontend/roles/auditor/` |


Three context containers coordinate logic:

| Context Object   | Scope of Responsibility                     | Primary Role                                                                  | Where It's Instantiated                         | Represents                          |
|------------------|----------------------------------------------|-------------------------------------------------------------------------------|--------------------------------------------------|-------------------------------------|
| `ClientContext`  | Portfolio state, risk settings, intraday metrics | Encapsulates account-level risk exposure, holdings, drawdowns, constraints    | During every trade intent submission            | **Account’s Real-Time Risk Profile** |
| `ExecutionContext` | Full trade lifecycle (intent → audit)       | Tracks trade from intent, approval, execution, post-trade update to audit log | Central to the `trade_flow.py` pipeline         | **Trade Trace & Audit Container**   |
| `RequestContext` | User identity, permissions, UI session state | Governs user access, page visibility, and logs interactions                   | On login; stored in Streamlit `session_state`   | **UI Session & Access Authority**   |


                 ┌────────────────────────────┐
                 │      RequestContext        │
                 │────────────────────────────│
                 │ user_id                    │
                 │ role → RBAC permissions    │
                 │ session_token              │
                 └────────────▲───────────────┘
                              │
                            Login
                              │
                              ▼
                    ┌──────────────────┐
                    │   TradeIntent     │  ← Manual / Strategy / Auto-Rebalancer
                    └───────┬───────────┘
                            ▼
          ┌────────────────────────────────────┐
          │           ClientContext            │  ← Per-client container
          │────────────────────────────────────│
          │ portfolio_state                    │
          │ risk_profile (from config)         │
          │ intraday risk metrics & triggers   │
          └───────────────┬────────────────────┘
                          ▼
          ┌────────────────────────────────────┐
          │         ExecutionContext           │  ← Full trade lifecycle container
          │────────────────────────────────────│
          │ trade_intent                       │
          │ risk_signals + approval_score      │
          │ execution_result                   │
          │ audit_log (for structured tracking)│
          └────────────────────────────────────┘

---

## 🧩 Service Interface Abstraction

To demonstrate modular engineering capability and support SDK-like integration, core services in **XQRiskCore** have been refactored into interface classes. These interfaces decouple logic from orchestration, enabling independent testing, service injection, and future API exposure.

### ✅ Implemented Service Interfaces

| Interface Class            | Role Description                                  |
|----------------------------|----------------------------------------------------|
| `TradeFlowService`         | Unified trade lifecycle execution interface       |
| `RiskEvaluatorService`     | Risk signal generation and approval logic         |
| `StrategySignalService`    | Strategy-based trade intent generation            |
| `MarketDataService`        | Market price and history access abstraction       |

These classes can be imported and invoked independently, allowing for flexible integration and precise control over each layer:

```python
svc = TradeFlowService(ctx)
result = svc.submit(intent)

risk = RiskEvaluatorService(ctx)
signals = risk.evaluate(intent)

market = MarketDataService()
price = market.get_latest_price("AAPL")
```

---

## 🧮 Functional Overview

**XQRiskCore** unifies trade routing, approval, control, and audit into a single, enforceable lifecycle.  
Every trade — regardless of origin — must pass through the same discipline.

### 🔒 Integrated Risk Coverage

Controls span all three major financial risk classes:

- **Market Risk** — volatility, VaR breaches, drawdowns  
  → Mitigated via scoring, KillSwitches, and asset-level lockdowns

- **Operational Risk** — execution errors, unauthorized behavior, audit gaps  
  → Controlled through intent approvals, Silent Mode, and structured logging

- **Governance Risk** — role overreach, invisible actions, policy bypass  
  → Enforced via RBAC, permission scoping, audit chains, and cooling-off

### ⚙️ Core System Capabilities

- ✅ **Unified trade flow** — All sources pass through one approval pipeline  
- ✅ **Built-in risk control** — VaR limits, KillSwitches, and Silent Mode  
- ✅ **Structured audit logs** — Action metadata: `user_id`, `timestamp`, `action`, `status`, trace path  
- ✅ **Client-specific config** — Per-client assets, strategies, and risk rules  
- ✅ **Role-based governance** — RBAC with behavioral logging and scope control

---

## 📌 Use Cases

XQRiskCore solves a simple but critical problem:  
🧠 *How do we ensure every trade — regardless of origin — is reviewed, executed, and recorded under a defensible system?*

It answers governance-level questions most systems avoid:

- **Who approves — and under what logic?**  
- **Can biased decisions be structurally blocked?**  
- **Are risk outcomes traceable by design?**  
- **Can strategy failures be traced to their source?**

Built for:

- ✅ **Multi-strategy fund desks** needing unified, explainable risk control  
- ✅ **Asset managers** seeking auditable governance without enterprise overhead  
- ✅ **Quant teams** requiring lifecycle tracking and approval scoring  
- ✅ **Compliance-focused firms** needing logs, overrides, and policy enforcement  
- ✅ **Risk officers and auditors** demanding traceable decision chains

Because risk isn’t just about limits — it’s about **structure, traceability, and responsibility**.

---

## 🚧 Roadmap & Evolution Overview

XQRiskCore is live with full trade lifecycle coverage, risk gating, and audit logging.  
Next: production-grade scalability, microservice refactor, and institutional readiness.

| **Area**              | **Current**                                | **Next**                                                  |
|-----------------------|--------------------------------------------|------------------------------------------------------------|
| Governance Logic      | YAML rules, modular signal engine          | Runtime hot-swap, version control                          |
| Risk Scoring          | HMM, GARCH, VaR, CVaR                      | Plug-in engines, feedback loop                             |
| Access Control        | RBAC roles + UI/module scoping             | Token auth, permission templates                           |
| Execution Layer       | Broker-agnostic API (Alpaca)               | Upgrade to FIX-ready architecture                          |
| Data Layer            | YAML + JSONL audit logs                    | PostgreSQL or MongoDB                                      |
| Services              | Interface-based logic (e.g., `TradeFlow`)  | Flask/FastAPI microservices                                |
| Scheduling            | Sync lifecycle engine                      | Celery / Airflow orchestration                             |
| Deployment            | Cloud via Railway                          | EC2 / GCP + scalable infra                                 |
| Long-Term Refactor    | Python (modular, fast dev)                 | Rebuild in Java/C++ for low-latency trading                |

---

## 🌱 Evolution by Design

Every module is built for upgrades — not hard rewrites.

- New rules? Add via YAML.  
- New scores? Extend plug-ins.  
- New roles? RBAC handles it.  
- New audits? Log and trace.

**Governance evolves. So does XQRiskCore.**

---

## 🧬 Who Am I?

I’m a graduating PhD in statistical genetics, where I specialized in modeling complex systems and risk behavior.  
**XQ** is my name.

While preparing for the **FRM Part 1** exam, I set myself a challenge:  
To use my skills in statistics and programming — not just to study financial risk, but to **build** it.

The result is **XQRiskCore** — my first project in financial risk.  

---

## 🤝 Collaboration & Opportunities

I'm open to:

- ✅ Partnering with funds, quant teams, or compliance leads building auditable risk infrastructure  
- ✅ Projects involving governance-driven strategy execution or automated trade control  
- ✅ Roles in **quant/risk engineering**, **approval architecture**, or **institutional risk governance**

If you're building something serious — or looking for someone who does — feel free to reach out:

- 📧 [x.qian@uq.edu.au](mailto:x.qian@uq.edu.au)  
- 📧 [qianxiaoyu19@gmail.com](mailto:qianxiaoyu19@gmail.com)  
- 🔗 [LinkedIn](https://www.linkedin.com/in/xiaoyu-qian-003882212)

---

## 🙏 Acknowledgments

I built XQRiskCore with help from large language models — not just as tools, but as thinking partners.  
**ChatGPT** helped architect logic, **DeepSeek** visualized workflows, and **Gemini** challenged the structure.

I’m deeply grateful to my PhD advisors, **Allan McRae** and **Fleur Garton**, whose modeling discipline shaped much of the system’s architecture.

Two ideas guided this project from the ground up:

- **Charlie Munger’s latticework thinking**, which taught me to cross-pollinate abstractions from genetics to finance.  
- **Warren Buffett’s lesson from LTCM** — that “you can’t survive a margin call even if you’re right” — which defined my priority: discipline over brilliance.

Without those principles, this system would not exist — at least not in this form.

---

## 📄 License

Selected modules of XQRiskCore are released under the MIT License.  
See [LICESNSE](LICENSE) for details on what is open and what remains proprietary.
