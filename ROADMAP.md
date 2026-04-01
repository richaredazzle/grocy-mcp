# Roadmap

This roadmap is a checkpoint ledger, not a feature wishlist.

`grocy-mcp` follows a two-layer model:

- `grocy-mcp` stays the Grocy-facing core: MCP server, CLI, stable workflow contracts
- chat, OCR, and image interpretation stay outside this repo and feed normalized JSON into it

The goal is to ship small, mergeable increments that are easy to test, review, and reason about.

## Operating Model

Every checkpoint is a separate PR and only counts as done when:

- code is implemented
- unit tests and relevant CLI/MCP tests pass
- docs are updated in the same PR
- review feedback is addressed
- the increment is merged

### Standard acceptance gate

Every checkpoint must satisfy this gate before merge:

- unit tests for all new core and workflow logic
- CLI tests for text and JSON modes where applicable
- MCP tests for tool registration, structured output, and malformed JSON/input validation
- opt-in live Grocy integration coverage for mutating checkpoints
- README, roadmap status, command/tool help text, and coverage notes updated in the same PR
- no known doc/code drift left behind

## Coverage Matrix Placeholder

Use this section to keep the project honest as it grows.

### First-class support

- stock
- shopping list
- recipes
- chores
- locations
- tasks
- meal plan
- workflow preview/apply primitives

### Generic-entity-only support

- shopping lists
- shopping locations
- quantity units
- quantity-unit conversions
- product groups
- task categories
- meal-plan sections
- recipe nestings
- batteries
- equipment
- files and print-related surfaces
- userfields, userentities, userobjects

### Not yet covered as first-class workflows

- receipt- and vision-oriented stock intake flows beyond normalized JSON handoff
- shopping reconciliation helpers beyond the current workflow layer
- battery-specific views and lifecycle actions
- equipment-specific views and lifecycle actions
- calendar-oriented combined reporting
- file-group helpers for pictures/manuals
- print/export helpers
- discover-fields and describe-entity helpers

## Track A: Workflow-Enabling Core

### [x] CP01 - Roadmap rewrite

- Goal: replace the priority list with checkpoint IDs and a merge-driven execution model
- Deliverables:
  - checkpoint ledger in `ROADMAP.md`
  - standard acceptance gate
  - coverage matrix placeholder
- Acceptance gate: docs-only review plus roadmap consistency
- PR: fill after merge

### [x] CP02 - Stable workflow JSON policy

- Goal: define the public JSON contracts for preview/apply flows
- Deliverables:
  - one design doc for workflow semantics and contract stability
  - README note describing the two-layer split
  - explicit statement that raw images stay outside this repo
- Acceptance gate: docs align with implemented workflow shapes
- PR: fill after merge

### [x] CP03 - Batch product matching preview

- Goal: add a workflow-oriented product-match preview for chat/image clients
- Deliverables:
  - `workflow_match_products_preview` MCP tool
  - `grocy workflow match-products-preview`
  - stable preview result shape with `matched`, `ambiguous`, `unmatched`
  - matching policy:
    barcode exact match, then exact normalized name, then substring match
- Acceptance gate:
  - exact barcode match test
  - exact name match test
  - ambiguous match test
  - unmatched item test
  - malformed JSON/input validation test
- PR: fill after merge

### [x] CP04 - Bulk stock intake preview/apply

- Goal: support the "I bought these groceries" workflow from normalized external items
- Deliverables:
  - `workflow_stock_intake_preview` MCP tool
  - `workflow_stock_intake_apply` MCP tool
  - CLI parity under `grocy workflow`
  - explicit-IDs-only apply contract
- Acceptance gate:
  - preview contract tests
  - apply uses only explicit `product_id`
  - no implicit name re-resolution during apply
- PR: fill after merge

### [x] CP05 - Shopping reconciliation preview/apply

- Goal: compare confirmed purchases against a shopping list and propose explicit actions
- Deliverables:
  - `workflow_shopping_reconcile_preview` MCP tool
  - `workflow_shopping_reconcile_apply` MCP tool
  - CLI parity under `grocy workflow`
  - explicit shopping item IDs in apply actions
- Acceptance gate:
  - full purchase test
  - partial purchase test
  - unmatched purchased item test
  - apply action test for remove and amount update
- PR: fill after merge

### [x] CP06 - LLM workflow docs and examples

- Goal: document how ChatGPT/Claude should use the workflow layer
- Deliverables:
  - receipt text -> preview -> confirm -> apply example
  - grocery photo interpreted by an LLM -> preview -> confirm -> apply example
  - pantry photo -> read-only preview example
  - sample prompts that produce normalized item JSON before tool calls
- Acceptance gate: README and design doc examples match real command/tool names
- PR: fill after merge

## Track B: Remaining Grocy Feature Coverage

### [ ] CP07 - Shopping metadata coverage

- Goal: move `shopping_lists` and `shopping_locations` from generic-only to first-class
- Deliverables:
  - first-class MCP/CLI list/create/update flows where the API supports them
  - docs and coverage matrix updates
- Acceptance gate: tests for list and mutation paths where applicable
- PR: fill after merge

### [ ] CP08 - Quantity units, conversions, product groups, price history

- Goal: expose the next highest-value stock metadata surfaces
- Deliverables:
  - first-class support for `quantity_units`, `quantity_unit_conversions`, `product_groups`
  - read-heavy support for `products_last_purchased` and `products_average_price`
  - JSON-mode reporting for these read surfaces
- Acceptance gate: structured output tests plus docs
- PR: fill after merge

### [ ] CP09 - Batteries

- Goal: make batteries a first-class household workflow
- Deliverables:
  - list/details
  - due/overdue charge views
  - charge/replacement/cycle-history support where the Grocy API shape allows it
- Acceptance gate: unit and integration tests for supported mutation paths
- PR: fill after merge

### [ ] CP10 - Equipment

- Goal: make equipment a first-class domain with battery visibility
- Deliverables:
  - list/details/create/update
  - linked battery visibility
  - references to file/manual surfaces where available
- Acceptance gate: first-class CLI/MCP parity plus docs
- PR: fill after merge

### [ ] CP11 - Task categories and assignment-aware flows

- Goal: improve task and chore context for household planning
- Deliverables:
  - first-class support for `task_categories`
  - richer task/chore JSON outputs with assignee context where the API returns it
- Acceptance gate: structured output tests and docs updates
- PR: fill after merge

### [ ] CP12 - Meal-plan sections and richer planning

- Goal: deepen planning support before broader bulk-write tools
- Deliverables:
  - support for `meal_plan_sections`
  - range summary and section-aware planning/reporting tools
- Acceptance gate: read-model tests plus docs
- PR: fill after merge

### [ ] CP13 - Calendar-oriented read models

- Goal: add one planning surface that summarizes chores, batteries, tasks, and meal plans
- Deliverables:
  - read-only combined planning/report tools
  - no calendar mutation model in v1
- Acceptance gate: JSON-contract tests and docs
- PR: fill after merge

### [ ] CP14 - Files and print/export

- Goal: expose only the file/print surfaces that are genuinely useful and automatable
- Deliverables:
  - scoped support for product pictures, recipe pictures, equipment manuals, and user files
  - print/export exposure only if it is cleanly testable
- Acceptance gate: docs, narrow surface area, and explicit limitations
- PR: fill after merge

### [ ] CP15 - Search/discovery helpers

- Goal: make generic CRUD and ambiguous lookups safer for both humans and agents
- Deliverables:
  - richer candidate search across product/recipe/chore/location/task surfaces
  - discover-fields or describe-entity helper for generic CRUD
  - better ambiguity messaging in CLI and MCP
- Acceptance gate: ambiguity and structured-output tests
- PR: fill after merge

## Track C: 1.0 Readiness

### [ ] CP16 - 1.0 readiness

- Goal: define what is stable before calling the project complete enough for 1.0
- Deliverables:
  - compatibility promise for tool names, command names, and workflow JSON contracts
  - release checklist and support policy
  - completed coverage matrix
  - one authoritative current design/implementation doc pair
- Acceptance gate: docs and release policy review
- PR: fill after merge

## What "Complete Enough for 1.0" Looks Like

The project is ready for a confident `1.0` when:

- command and tool behavior is predictable and well-tested
- workflow JSON contracts are documented and stable enough for scripting and LLM orchestration
- common Grocy household flows do not require generic CRUD as the default path
- docs clearly separate first-class support from generic-only support
- contributors can extend the project without creating doc/code drift
