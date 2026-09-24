# OpsMind-AI — Execution Plan

## Phase 1 — Existing System Audit

**Objective:** establish the code baseline. **Existing Components:** integrations, tools, agents, graph, FastAPI. **Required Changes:** documentation only. **Dependencies:** none. **Implementation Tasks:** inspect source, tests, configuration presence, and docs. **Validation:** source audit. **Expected Output:** this plan folder. **Completion Criteria:** ✅ baseline documented.

## Phase 2 — Backend Stabilization

**Objective:** keep FastAPI thin and safe. **Existing Components:** `app.main`. **Required Changes:** route modules and safe errors. **Dependencies:** schemas. **Implementation Tasks:** add routers. **Validation:** TestClient checks. **Expected Output:** organized API. **Completion Criteria:** 🟡 pending implementation.

## Phase 3 — Tool API Validation

**Objective:** expose read-only development endpoints. **Existing Components:** tools/integrations. **Required Changes:** tools router. **Dependencies:** integrations. **Implementation Tasks:** wrap existing clients. **Validation:** mocked route tests. **Expected Output:** documented Swagger endpoints. **Completion Criteria:** 🟡 pending implementation.

## Phase 4 — Agent Validation

**Objective:** test factories and tool runtime without live services. **Existing Components:** agents/runtime. **Required Changes:** mock tests. **Dependencies:** LangChain. **Implementation Tasks:** isolate LLM/tool calls. **Validation:** pytest. **Expected Output:** reliable unit tests. **Completion Criteria:** 🟡 pending implementation.

## Phase 5 — Supervisor + Planner Workflow

**Objective:** retain Planner as a workflow step. **Existing Components:** LangGraph. **Required Changes:** structured plan metadata and multi-source routing. **Dependencies:** agent factories. **Implementation Tasks:** update state/nodes/edges. **Validation:** graph unit tests. **Expected Output:** planner-led execution. **Completion Criteria:** 🟡 pending implementation.

## Phase 6 — Multi-source Data Aggregation

**Objective:** gather dashboard-safe data. **Existing Components:** integration clients. **Required Changes:** aggregator. **Dependencies:** schemas. **Implementation Tasks:** normalize read models. **Validation:** mocked aggregation tests. **Expected Output:** factual source payload. **Completion Criteria:** 🟡 pending implementation.

## Phase 7 — Analytical Data Layer

**Objective:** compute deterministic metrics and attention items. **Existing Components:** source schemas. **Required Changes:** analytics modules. **Dependencies:** aggregation. **Implementation Tasks:** derive counts and due-date/priority signals. **Validation:** fixture tests. **Expected Output:** facts separate from LLM insight. **Completion Criteria:** 🟡 pending implementation.

## Phase 8 — Dashboard APIs

**Objective:** provide structured dashboard data. **Existing Components:** FastAPI. **Required Changes:** dashboard router. **Dependencies:** analytics. **Implementation Tasks:** summary, attention, activity, workload, trends, insights, agents endpoints. **Validation:** API tests. **Expected Output:** frontend contract. **Completion Criteria:** 🟡 pending implementation.

## Phase 9 — Streamlit Dashboard

**Objective:** render dashboard data from FastAPI. **Existing Components:** empty frontend file. **Required Changes:** functional UI. **Dependencies:** dashboard API. **Implementation Tasks:** sidebar, metrics, attention/activity views. **Validation:** startup/import test. **Expected Output:** runnable Streamlit app. **Completion Criteria:** 🟡 pending implementation.

## Phase 10 — Agentic Chat Interface

**Objective:** call real `/chat`. **Existing Components:** `/chat`. **Required Changes:** Streamlit chat view. **Dependencies:** backend. **Implementation Tasks:** message history and safe workflow metadata. **Validation:** mocked HTTP test. **Expected Output:** agent chat. **Completion Criteria:** 🟡 pending implementation.

## Phase 11 — Critic + Guardrails

**Objective:** preserve human approval boundary. **Existing Components:** guardrails. **Required Changes:** document unconnected critic as planned. **Dependencies:** action APIs. **Implementation Tasks:** no write routes. **Validation:** policy tests. **Expected Output:** no unapproved writes. **Completion Criteria:** 🟡 partial.

## Phase 12 — End-to-End Testing

**Objective:** validate API and process starts. **Dependencies:** all prior phases. **Tasks:** compile, pytest, FastAPI and Streamlit smoke tests. **Completion Criteria:** 🟡 pending final validation.

## Phase 13 — Documentation & Final Cleanup

**Objective:** keep documents factual. **Tasks:** update statuses and startup instructions. **Completion Criteria:** ✅ documentation updated after validation.
