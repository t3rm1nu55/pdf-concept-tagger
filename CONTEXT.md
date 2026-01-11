# PDF Concept Tagger - Project Context

## 1. Project Overview
**Name:** PDF Concept Tagger (Ontology Engine v6.0)
**Description:** A regulatory analysis tool that ingests PDFs, performs OCR/Visual analysis via AI, and constructs a live knowledge graph of concepts, relationships, and hypotheses.
**Metaphor:** "Agent Council" (Harvester, Curator, Architect, Critic, Observer) working together to structure data.

## 2. Technical Stack
- **Framework:** Angular v20+ (Zoneless, Standalone Components, Signals).
- **Styling:** Tailwind CSS (via CDN).
- **Visualization:** D3.js (Force-directed graph).
- **PDF Handling:** PDF.js (v3.11.174 via CDN).
- **AI/LLM:** Google Gemini API (`gemini-2.5-flash`) via `@google/genai`.
- **Persistence:** IndexedDB (via `StorageService`).
- **Build System:** In-browser transpilation (requires specific entry point handling).

## 3. System Architecture

### Components
- **AppComponent (Orchestrator):** Manages global state (`processingState`, `activeAgents`), PDF loading, and coordinates data flow between services.
- **LockerComponent:** Sidebar list view. Organizes concepts into folders based on `ui_group`.
- **InspectorComponent:** Detail view for selected nodes.
- **GraphService:** Manages the D3 simulation. Handles rendering nodes/edges and click events.

### Services
- **GeminiService:**
  - Handles streaming responses from Gemini.
  - Implements a custom JSON parser (`extractNextJsonObject`) to handle fragmented JSON streams.
  - Enforces `AgentPacket` protocol.
- **StorageService:** Asynchronous IndexedDB wrapper for persisting nodes/edges/hypotheses.
- **LogService:** detailed system logging and "Deep Log" download capability.

## 4. Key Data Structures
**AgentPacket:**
```typescript
{
  sender: 'SYSTEM' | 'HARVESTER' | ...;
  intent: 'GRAPH_UPDATE' | 'HYPOTHESIS' | ...;
  content: {
    concept?: { id, term, type, ui_group, ... };
    relationship?: { source, target, predicate, ... };
    // ...
  }
}
```

**GraphNode (D3) vs Concept Entity:**
- **Design Intent:** Originally designed as a wrapper `GraphNode { x, y, conceptRef: Concept }`.
- **Actual Implementation:** To simplify state management, the App now merges D3 simulation properties (`x`, `y`, `vx`, `vy`) directly onto the `Concept` object.
- **Implication:** UI components (Locker/Inspector) must access properties like `node.id` or `node.term` directly. They should NOT look for `node.conceptRef.id` unless dealing with legacy data structures.

## 5. Critical Debugging History & Fixes

### A. The "CORS / 301 Redirect" Error
**Symptoms:**
- Error: `Access to script at 'https://ai.studio/index.tsx' ... blocked by CORS`.
- Network Tab: `GET index.tsx` returns status `301 Moved Permanently`.
**Root Cause:**
- The browser environment intercepts requests to `.tsx` files to transpile them.
- Using `src="index.tsx"` caused the browser to resolve against the root domain (`ai.studio`), which redirects or blocks cross-origin requests from the sandbox.
**Fix:**
- **Mandatory:** Use explicit relative path `<script type="module" src="./index.tsx"></script>`. The `./` forces resolution within the current sandbox context.

### B. The "Undefined 'id'" Crash
**Symptoms:**
- Application crashes immediately upon clicking a node or rendering the Locker list.
- Stack Trace: `TypeError: Cannot read properties of undefined (reading 'id')` inside `AppComponent.selectConcept` or `LockerComponent`.
**Root Cause:**
- `LockerComponent` and `GraphService` were written expecting a nested structure: `node.conceptRef.id`.
- The `GeminiService` and `StorageService` were passing flat objects where the concept data was at the root level.
**Fix:**
- Updated `LockerComponent` to read `node.id` and `node.ui_group` directly.
- Updated `GraphService` click handlers to fallback: `this.nodeClicked$.next(d.conceptRef || d)`.

### C. PDF.js "Fake Worker" & Performance
**Symptoms:**
- Console warning: `Setting up fake worker`.
- PDF rendering blocks the main thread (UI freezes during load).
**Root Cause:**
- PDF.js defaults to a main-thread worker if the external worker script is not explicitly configured or fails to load.
**Fix:**
- Added explicit configuration in `AppComponent` constructor:
  ```typescript
  pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdn.jsdelivr.net/npm/pdfjs-dist@3.11.174/build/pdf.worker.min.js';
  ```
- **Constraint:** The version in the worker URL (`3.11.174`) MUST match the version of the main library script in `index.html`.

## 6. Current Implementation Status
- **PDF Rendering:** Functional (Canvas based, CMaps configured for better font support).
- **AI Streaming:** Functional (Stream parsing implemented, robust to chunking).
- **Graph Visualization:** Functional (D3 Force layout, auto-centering).
- **Interactive Parsing:** Users can click nodes to see details; bounding boxes overlay on source PDF.
- **Persistence:** Nodes are saved to IndexedDB to persist across reloads.

## 7. Future/Pending Tasks
- **Error Handling:** Graceful recovery if the JSON stream is malformed (currently logs warning).
- **Graph Refinement:** Prevent text collision on the D3 graph; add zoom/pan capabilities.
- **Agent Interactivity:** Allow user to "Chat" with specific agents (Critic/Architect).
