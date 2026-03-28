---
name: dashpilot
description: >-
  Chrome extension + MCP server for live read-only inspection of the active
  browser tab. Captures HTTP fetch requests with response bodies, WebSocket
  frames, React component props/state/hooks, TanStack React Query cache,
  lightweight-charts candlestick/OHLCV data, and Recharts state. Use this
  skill whenever the user wants to see what a web page is doing, inspect
  browser tab activity, debug dashboard or web app behavior, read API
  response bodies, check what endpoints a page is hitting, examine React
  component props or state, look at query cache staleness, or extract chart
  data points. Also use when the user mentions DashPilot, page snapshot,
  network log, fetch calls, API traffic, websocket messages, CSS computed
  styles, or anything about observing/inspecting a live web page. This skill
  is for observation only — if the user wants to click, navigate, type, or
  take screenshots, use Chrome DevTools MCP instead.
---

# DashPilot — Live Dashboard Intelligence via MCP

Chrome MV3 extension + MCP server that gives Claude read-only access to the active browser tab. Observes network traffic, React internals, query caches, and chart data without modifying the page.

## Setup

The DashPilot MCP server connects via native messaging. Tools are available as `mcp__dashpilot__*`. Use `ToolSearch` with `+dashpilot` to discover and load them.

## Tools Reference

### Debug

| Tool | Purpose | Key Params |
|------|---------|------------|
| `ping` | MCP connectivity check | — |
| `test_roundtrip` | Full round-trip through extension to content script | — |

### React & DOM

| Tool | Purpose | Key Params |
|------|---------|------------|
| `page_snapshot` | URL, title, viewport, console errors, React tree, dashboard counts | `depth` (1-20, default 3) |
| `inspect_component` | Find React component by name, return props/state/hooks/children | `name` (required), `depth` (1-20) |
| `get_styles` | Computed CSS properties and bounding rect for a CSS selector | `selector` (required) |
| `get_query_cache` | TanStack React Query cache entries (keys, status, staleness) | `limit` (1-100), `offset` |
| `get_query_data` | Full cached data for a specific query key | `query_key` (required, JSON array string) |

### Network

| Tool | Purpose | Key Params |
|------|---------|------------|
| `get_network_log` | Captured HTTP requests with response bodies (up to 10KB each) | `url_filter`, `limit` (1-100), `offset` |
| `get_websocket_log` | WebSocket frames with payload (up to 5KB each) | `url_filter`, `limit` (1-100), `offset` |

### Charts

| Tool | Purpose | Key Params |
|------|---------|------------|
| `get_chart_state` | Lightweight-charts series data (OHLCV), time range, options | `max_points` (1-5000, default 200) |
| `get_recharts_state` | Recharts data arrays, axis config, dimensions | `max_points` (1-5000, default 200) |

## Paginated Responses

Network, WebSocket, and query cache tools return paginated envelopes:
```json
{ "entries": [...], "total": 50, "offset": 0, "limit": 20, "hasMore": true }
```
Use `offset` + `limit` to page through results. Default limit is 20, max 100.

## Response Caps

All tool responses are capped at 50KB. Large payloads are truncated with `"truncated": true` and `"hasMore": true` markers. Chart data defaults to 200 most recent data points per series.

## Common Workflows

### See what a page is doing
```
page_snapshot -> get_network_log (limit: 5) -> get_chart_state
```

### Debug API issues
```
get_network_log(url_filter: "/api/") -> inspect specific responses
```

### Check React state
```
page_snapshot (check reactDetected) -> get_query_cache -> get_query_data(query_key)
```

### Inspect a component
```
inspect_component(name: "Button") -> get_styles(selector: ".my-button")
```

## Error Messages

All errors include the tool name in brackets and actionable recovery steps:
- `[action] No extension connected...` -> Chrome not running or extension not loaded
- `[action] Content script timed out...` -> Page needs reload
- `[action] Could not reach content script...` -> Navigate to an http/https page

## Limitations

- **Read-only** — Cannot click, navigate, or modify pages (use Chrome DevTools MCP for that)
- **Active tab only** — Inspects the active tab in the last focused Chrome window
- **Content script required** — Only works on http/https pages (not chrome://, file://, etc.)
- **React DevTools needed** — Component tree and query cache require React DevTools browser extension
- **Chart hooks** — Lightweight-charts must be hooked at load time; charts created before extension loads won't be captured

## Complementary Tools

DashPilot pairs with the Chrome DevTools MCP server:
- **DashPilot** = observe (network, React state, charts, queries)
- **Chrome DevTools** = act (click, navigate, fill forms, take screenshots)

Use both together: DevTools to navigate, DashPilot to inspect what happened.

## Architecture

```
Claude <-stdio-> MCP Server <-Unix socket-> Native Host <-native messaging->
  Service Worker <-chrome.tabs.sendMessage-> Content Script (ISOLATED world)
    <-window.postMessage-> Content-Main Script (MAIN world, hooks fetch/WS/charts)
```

## Source Code

- Extension: `extension/`
- MCP Server: `mcp-server/`
- Install: `bash install.sh`
