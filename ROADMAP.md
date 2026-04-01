# Roadmap

This roadmap focuses on what is still worth doing now that the project already has:

- broad stock, shopping, recipe, chore, location, task, meal-plan, and entity coverage
- both MCP and CLI interfaces
- CI, changelog, contributing docs, and better GitHub polish

The remaining work is less about "add more commands" and more about turning `grocy-mcp` into the version people can trust as their default Grocy interface.

## Coverage reality check

Based on Grocy's public site and official OpenAPI surface, `grocy-mcp` already covers a meaningful core of Grocy:

- stock operations
- shopping list workflows
- recipes
- chores
- tasks
- locations
- meal plan
- generic entity CRUD for exposed entities

However, Grocy's API and UI also expose additional surfaces that are not yet first-class in this project and should shape the next roadmap:

- batteries
- equipment
- calendar-oriented views
- files and attachments
- print/export workflows
- shopping list metadata such as shopping lists and shopping locations
- quantity units and quantity-unit conversions
- task categories
- meal-plan sections
- recipe nestings
- product groups and price-history/last-purchased views
- stock-current-location and richer stock journal/reporting data
- user/current-user and assignment-aware flows
- advanced generic entities such as userfields, userentities, and userobjects

## North Star

An excellent `grocy-mcp` should feel like:

- the best Grocy MCP server for AI agents
- a CLI that is pleasant for daily human use and robust for scripting
- a project where docs, behavior, tests, and release quality stay aligned
- a tool that covers the Grocy workflows people actually do every week

## Priority 1: Reliability and consistency

- [ ] Audit every CLI command and MCP tool so equivalent operations behave consistently across both surfaces.
- [ ] Standardize output shapes for JSON mode where similar commands currently return differently structured payloads.
- [ ] Add regression tests for every command/tool that accepts JSON input or optional flags with non-obvious behavior.
- [ ] Add stronger integration coverage against a real Grocy instance for the highest-risk flows:
  stock add/consume/transfer, shopping updates, recipe creation/editing, chores execution, tasks, and meal-plan shopping.
- [ ] Add explicit compatibility notes for supported Grocy versions and document any known API quirks by version.

## Priority 2: Best-in-class MCP ergonomics

- [ ] Review all tool names and descriptions from an AI-agent perspective and simplify any confusing or overly technical wording.
- [ ] Decide where MCP should return richer structured data instead of formatted strings, especially for search, detail, fulfillment, and journal-style tools.
- [ ] Add safer low-level entity tooling guidance so agents know when to prefer domain-specific tools over generic CRUD.
- [ ] Add examples of agent workflows that chain tools together for common household tasks:
  weekly restock, cook-from-stock, meal-plan-to-shopping, overdue-chore sweep, and pantry audit.
- [ ] Consider separating "read" tools from "mutating" tools more clearly in naming and docs to reduce accidental writes.

## Priority 3: Excellent CLI experience

- [ ] Make JSON mode fully intentional and documented: define which commands support it, what shape they return, and where stability is guaranteed.
- [ ] Add shell-friendly examples for `jq`, PowerShell, and simple automation scripts.
- [ ] Improve help text for commands with JSON arguments by showing one realistic example per command.
- [ ] Add validation for user-facing inputs such as dates, entity actions, and enum-like arguments before the request reaches Grocy.
- [ ] Review whether a few carefully chosen aliases would improve ergonomics without creating ambiguity.

## Priority 4: Fill the highest-value Grocy domain gaps

The project is already broad. The next domain work should be selected based on real day-to-day usefulness:

- [ ] Batteries as a first-class domain:
  list, details, charge/replacement tracking, cycle history, and overdue battery views.
- [ ] Equipment as a first-class domain:
  list, create/update flows, linked batteries, manuals/files, and maintenance-oriented workflows.
- [ ] Shopping metadata support:
  shopping lists, shopping locations, and better multi-list workflows.
- [ ] Product groups, quantity units, and quantity-unit conversions as dedicated tools/commands.
- [ ] Better purchase and price-history workflows using Grocy's last-purchased and average-price data.
- [ ] More complete recipe editing and recipe-position metadata support, including recipe nestings where useful.
- [ ] Richer meal-plan operations:
  bulk planning, date-range inspection, replace/move entries, section support, and plan previews.
- [ ] Task categories and assignment-aware task/chore workflows where Grocy supports them.
- [ ] Calendar-oriented views that combine chores, batteries, meal-plan items, and tasks into one planning surface.

## Priority 5: Files, print, and companion surfaces

- [ ] Support Grocy file groups where they add real value:
  recipe pictures, product pictures, equipment manuals, and user files.
- [ ] Evaluate whether print/export endpoints are useful enough to expose through MCP and CLI.
- [ ] Add document- and attachment-aware workflows where they reduce context switching from Grocy's UI.

## Priority 6: Search, resolution, and discoverability

- [ ] Make name resolution smarter while staying predictable:
  better ambiguity messages, optional stricter matching modes, and clearer suggestions.
- [ ] Add richer search outputs for products, recipes, chores, locations, and tasks.
- [ ] Improve barcode flows so users can move naturally between barcode lookup, product info, and stock actions.
- [ ] Add a "describe this entity type" or "discover fields" capability for safer generic entity usage.
- [ ] Add API-backed discovery helpers for supported Grocy entities, tags, and field shapes so agents can reason safely about generic CRUD.

## Priority 7: Documentation that stays true

- [ ] Keep one clearly current design/implementation doc pair and explicitly mark older specs as historical.
- [ ] Add a short "Which interface should I use?" section comparing MCP, CLI, and generic entity tools.
- [ ] Add a "common workflows" guide that shows the same task done through CLI and MCP.
- [ ] Add troubleshooting for Grocy-specific issues:
  reverse proxies, API permissions, object-field mismatches, and version differences.
- [ ] Add contributor guidance for keeping docs aligned whenever commands or tool behavior change.
- [ ] Add a coverage matrix showing:
  current first-class support, generic-entity-only support, and not-yet-covered Grocy surfaces.

## Priority 8: Release and maintenance maturity

- [ ] Define a stable pre-1.0 compatibility promise for command names, tool names, and JSON output expectations.
- [ ] Add release checklists covering docs, changelog, tests, packaging, and MCP/CLI parity review.
- [ ] Publish example configs for Claude Desktop, Claude Code, and generic MCP HTTP clients.
- [ ] Add a lightweight support policy for bug reports:
  what environment details to include, which Grocy versions are expected, and how to provide reproducible payloads.

## What "complete enough for 1.0" looks like

The project is ready for a confident `1.0` when all of the following feel true:

- command and tool behavior is predictable and well-tested
- JSON mode is documented and stable enough for scripting
- the most common Grocy household workflows are covered without needing generic CRUD as a fallback
- MCP docs help agents choose the right tool on the first try
- contributor docs make it hard for implementation and docs to drift apart

## Suggested execution order

If we want the highest payoff path from here, the best order is:

1. reliability and consistency
2. MCP ergonomics plus JSON/output stability
3. CLI usability and validation
4. highest-value Grocy domain gaps from the official API surface
5. search/discovery and coverage matrix work
6. documentation discipline and 1.0 release readiness
