# CCGenTool2 Web Contribution Guide

## Front-End Stack and Key Libraries
- **Vue 3 + `<script setup>` composition API** for building single-file components.
- **Pinia** (`createPinia`) for global state readiness (currently minimal but installed in `main.ts`).
- **Vue Router** (`createRouter`, `createWebHistory`) for page navigation.
- **Axios** for REST calls to the FastAPI backend (`src/services/api.ts`).
- **TipTap** editor extensions (`@tiptap/*`) powering the rich text editor component.
- **docx-preview** renders DOCX blobs returned by the API inside modals.
- **Playwright** (`@playwright/test`) drives end-to-end smoke tests under `tests/` and must be used to validate UI flows.
- **Vite** handles development and build tooling with TypeScript support.

## Workflow Guardrails
Contributors must preserve the established workflow so that `/final-preview` can compile a complete Common Criteria package:
1. **Sidebar-driven flow** – every functional section exposed in the sidebar must have a corresponding view with fully wired save/load actions. If you add a new feature, make sure the sidebar exposes it and the view implements the necessary handlers.
2. **Shared WYSIWYG behaviour** – all modules that display rich text must embed the shared `RichTextEditor` component. Do not fork the editor; extend its props or emitted events instead so table sizing, text formatting, and orientation metadata remain identical across sections.
3. **HTML outputs only** – every module/view that communicates with the backend should persist HTML strings (originating from TipTap) so the preview builders can concatenate the fragments. Avoid introducing plain-text fallbacks.
4. **JSON save/load contract** – all client-side persistence goes through `sessionService` and must serialize to JSON. When adding new modules, extend `sessionService` with matching `save*`/`load*`/`clear*` helpers before using them in a component.
5. **Respect WYSIWYG formatting** – never strip or reformat HTML returned from the editor. When sanitising or transforming content, ensure table widths, text styles, and orientation attributes survive so generated DOCX and previews stay faithful.
6. **Section status propagation** – each module must report whether its required forms are filled so that `/final-preview` can show `Completed` or `Missing`. Extend the relevant API calls and client-side checks whenever you add new fields.
7. **New implementations must comply** – if you introduce a brand-new view, ensure it adheres to all rules above before shipping. Update this document with the new module’s responsibilities so future contributors understand how it integrates.

## Module Map and Function Responsibilities
### Application Shell
- `src/main.ts` bootstraps the Vue app, installs Pinia and the router, then mounts `App.vue`.
- `src/App.vue`
  - Imports the sidebar layout and polls `/health` via `poll()` every 5 seconds, updating the `health` badge.
  - Uses the router outlet to render view components.

### Routing
- `src/router/index.ts` enumerates routes for home, generator, settings, ST introduction steps, and security requirements pages. Each route maps to a view component exported from `src/views`.

### Services
- `src/services/api.ts`
  - `resolveBaseURL()` checks Vite env vars, dev mode, and `window.location` to determine the REST base URL.
  - Exports a configured Axios instance reused across views.
- `src/services/sessionService.ts`
  - `SessionService` class encapsulates localStorage persistence keyed by a generated user token (`getOrCreateUserToken()`).
  - Exposes methods grouped by workflow segment:
    - SFR: `saveSfrData()`, `loadSfrData()`, `clearSfrData()`, `clearAllSfrData()`, `hasSessionData()`.
    - SAR: `saveSarData()`, `loadSarData()`, `clearSarData()`, `clearAllSarData()`.
    - Cover: `saveCoverData()`, `loadCoverData()`, `clearCoverData()`.
    - ST reference: `saveStReferenceData()`, `loadStReferenceData()`, `clearStReferenceData()`.
    - TOE reference: `saveToeReferenceData()`, `loadToeReferenceData()`, `clearToeReferenceData()`.
    - TOE overview: `saveToeOverviewData()`, `loadToeOverviewData()`, `clearToeOverviewData()`.
    - TOE description: `saveToeDescriptionData()`, `loadToeDescriptionData()`, `clearToeDescriptionData()`.
  - Helpers such as `getNamespacedKey()` maintain per-user storage isolation. The singleton export `sessionService` is reused across views.
  - When adding new workflow sections, extend this class with JSON-based helpers first, then connect your component logic.

### Reusable Components
- `src/components/Sidebar.vue` toggles accordion sections for ST Introduction and Security Requirements using `ref` booleans `stIntroOpen` and `securityOpen`.
- `src/components/XMLTreeNode.vue`
  - Accepts `node` + `level` props.
  - `toggleExpanded()` collapses/expands children; `getNodeClass()` returns CSS classes based on XML node types.
- `src/components/RichTextEditor.vue`
  - Wraps TipTap editor configuration via `useEditor()`.
  - Provides toolbar handlers (`toggleInline`, `applyHeading`, `applyList`, `applyHighlight`, `toggleSuperscript`, `toggleSubscript`, `setAlignment`, `insertImage`, `insertTable`, `handleTableAction`) that update the `editor` instance and emit `update:modelValue`.
  - Watches the bound `modelValue` prop to keep external state and the editor instance synchronised and disposes of resources in `onBeforeUnmount`.
  - All new views with rich text must consume this component instead of recreating editors.

### Views
- `Home.vue` presents navigation CTAs only.
- `Cover.vue`
  - Manages file drag/drop via `handleDrop()`, `triggerFileDialog()`, and `handleFileSelection()`.
  - Validates uploads with `validateImage()`, posts to `/cover/upload` through `uploadFile()`, and caches responses in `sessionService` (`saveSessionData()`, `loadSessionData()`).
  - Preview handling uses `openPreview()`, `closePreview()`, and `renderPreview()` (after the API call in `generatePreview()`) to display DOCX content with `docx-preview`.
  - Cleans up in `onBeforeUnmount` by calling backend cleanup endpoints.
- `Generator.vue` contains placeholder text for the upcoming generator module.
- `Settings.vue` wires to session storage and backend endpoints for listing/importing projects (see table actions such as `fetchProjects()` and modal toggles).
- `SecurityFunctionalRequirements.vue`
  - Provides CRUD-like operations for SFR lists: `fetchFamilies()`, `searchFamilies()`, `selectComponent()`, `addRequirement()`, `duplicateRequirement()`, `updateRequirement()`, `removeRequirement()`, `exportDocxPreview()`.
  - Persists selections through the session service and triggers backend preview endpoints.
- `SecurityAssuranceRequirements.vue`
  - Similar session-driven workflows for SAR data: `fetchSarFamilies()`, `selectSarComponent()`, `addSarRequirement()`, `duplicateSarRequirement()`, `removeSarRequirement()`, `exportSarPreview()`.
- `STReference.vue`, `TOEReference.vue`, `TOEOverview.vue`, `TOEDescription.vue`
  - Each view uses the rich text editor to capture HTML, persists the data via the session service (`saveStReference()`, `saveToeReference()`, etc.), and posts to preview endpoints when requested.
  - They must validate that required fields are filled before allowing navigation so the status checker can mark the section as `Completed`.
- `STIntroPreview.vue` aggregates stored cover/reference/TOE content, calls `/st-intro/preview`, and renders the returned DOCX using the shared preview pattern while reporting completion status to `/final-preview`.

### Types and Config
- `src/env.d.ts` and `src/types/docx-preview.d.ts` provide TypeScript declarations for Vite env variables and the `docx-preview` renderer.
- `vite.config.ts` sets up the Vue plugin and dev server proxy to `/api` (ensuring the Axios base URL strategy works during development).
- `playwright.config.ts` specifies dev server launch commands for UI testing.

### Tests
- `tests/app.spec.ts` contains the baseline Playwright scenario verifying navigation between Home, Cover, Generator, and Settings routes.
- Add or update Playwright specs whenever you touch workflow-critical functionality. Tests should confirm that new modules save data (JSON via `sessionService`), render HTML outputs, and update `/final-preview` statuses as expected.

## Using Playwright for Web Verification
1. Install dependencies: `npm install` (run inside `web/`).
2. Ensure Playwright browsers are available: `npx playwright install --with-deps` (first run only).
3. Start the FastAPI backend (see `server/AGENTS.md`) and launch the Vite dev server with `npm run dev -- --host`.
4. Execute the existing suite or your new scenarios with `npm run test:e2e`. Use `npx playwright test --ui` for interactive debugging if needed.
5. Capture screenshots via Playwright's tracing or `page.screenshot` helpers when diagnosing issues.
6. Provide evidence in PRs (screenshots/logs) that WYSIWYG formatting, HTML persistence, and `/final-preview` section statuses remain intact.

Lastly, please test all your implementation, using your own tool like playwright, and take screenshot as your aid in debugging and for evidence.
