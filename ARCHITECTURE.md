# Architecture

## Context

The Obsidian Flask is a two-part local game application:

- `Backend/` is a FastAPI service. It owns session lifecycle, event persistence, deterministic world state, memory retrieval, prompt assembly, LLM calls, validation, and WebSocket updates.
- `Frontend/` is a Vite React application. It owns routing, UI state, HTTP calls, WebSocket connection state, and presentation.

The repository uses a layered modular monolith. One backend process and one static frontend are enough for the current workload: a single-player game with at most `MAX_CONCURRENT_SESSIONS` (50) in-memory sessions. Each layer is a package with a single responsibility, so it could be extracted later without rewriting callers.

## Backend module map

| Package      | Responsibility                                                              | May import                        |
| ------------ | --------------------------------------------------------------------------- | --------------------------------- |
| `schemas/`   | Canonical Pydantic models: world state, events, LLM output                  | standard library, Pydantic        |
| `core/`      | Event store, reducer, snapshots. Deterministic, no ML or network            | `schemas`                         |
| `game/`      | World seed loading and validation of proposed world updates                 | `schemas`, `core`                 |
| `memory/`    | Embedder with SQLite cache, FAISS index, short-term buffer                  | `config`                          |
| `llm/`       | Groq client and prompt construction                                         | `schemas`, `memory`, `config`     |
| `graph/`     | One turn: retrieve, prompt, generate, validate, commit, remember            | all of the above                  |
| `session/`   | Session lifecycle, save files on disk, dialogue history, turn orchestration | all of the above                  |
| `api/`       | HTTP and WebSocket transport, API DTOs, presenters, dependencies            | everything                        |
| `config`     | Environment-driven settings, validated at import                            | standard library, `python-dotenv` |
| `log_config` | Log format, request and session context variables, quiet dependencies       | standard library                  |

Inside `api/`:

- `app.py` is the application factory. It owns the `SessionManager` on `app.state`, middleware, and the exception handler.
- `dependencies.py` resolves the session manager and returns 404 for unknown sessions. Routes never look sessions up themselves.
- `routes/sessions.py`, `routes/gameplay.py`, `routes/world.py`, and `routes/websocket.py` each hold one route group.
- `presenters.py` maps internal state to response DTOs, and `realtime.py` builds and broadcasts WebSocket messages.

Inside `session/`:

- `manager.py` holds `SessionManager`, which creates, loads, saves, and destroys sessions, commits player-driven events, and runs turns.
- `game_session.py` holds the per-session runtime state.
- `save_files.py` is the only place that knows the on-disk save layout: session directories, manual and auto snapshots, and dialogue files.
- `dialogue.py` builds the display dialogue entries.

Logging: every module uses `logging.getLogger(__name__)` and passes structured fields with `extra=`. Only `server.py` calls `log_config.configure_logging`. The request middleware in `api/app.py` binds `req`, `api/dependencies.get_session` and the WebSocket route bind `session`, and blocking work runs through `asyncio.to_thread`, which carries both into worker threads. Do not use `loop.run_in_executor` for request work; it drops that context.

Dependency rules are enforced by [Backend/tests/test_architecture.py](Backend/tests/test_architecture.py), which fails when a lower layer imports a higher one.

## Frontend module map

| Folder                            | Responsibility                                             | Must not import                            |
| --------------------------------- | ---------------------------------------------------------- | ------------------------------------------ |
| `contracts/`, `types/`, `config/` | Backend DTOs (snake case), UI domain types, constants      | React, stores, services, pages, components |
| `services/`                       | REST client (`httpClient.ts`), WebSocket lifecycle, facade | React, stores, pages, components           |
| `stores/`                         | Zustand state; `mappers.ts` converts DTOs to UI types      | pages, components, hooks                   |
| `hooks/`, `lib/`, `components/`   | Shared hooks, formatting, reusable UI                      | pages                                      |
| `pages/`                          | Route-level composition                                    | (top layer)                                |

Inside `components/`:

- `ui/` holds the custom primitives: `Button`, `IconButton`, `Tooltip`, `Modal` (dialog and side sheet with focus trap), `ChoiceGroup` (radio pills and cards), `Field`, `Stepper`, `EmptyState` and `SectionLabel`, and the themed `sonner` toaster. No browser-native pickers, selects, tooltips, or validation bubbles are used.
- `layout/` holds the game shell (`GameLayout`, `GameNavigation`), `BootGate`, and `MasterDetail`, which the Map and People pages share.
- `game/` holds the transcript (`DialoguePanel`), the composer (`PlayerInputDock`), `TrustScale`, `PauseMenu`, and `scene/`, the room panel split into place, people, objects, and player sections.

Design tokens live once, as CSS variables in `src/index.css`, and are exposed as Tailwind colours in `tailwind.config.ts` by role: `ground`, `surface`, `raised`, `line`, `text`, `muted`, `faint`, `gilt` (the player and primary actions), `arcane` (NPC voices and trust), and `ember` (danger and errors).

The document never scrolls (`html` and `body` are `overflow: hidden`). Each screen is `h-dvh` or fills the game shell, and scrolls inside elements with the `scroll-area` utility from `src/index.css`, which is positioned so screen-reader-only text and tooltips cannot stretch the page. New scrolling panels must use `scroll-area`, not `overflow-y-auto`. Motion also has one home there: `press` for compact controls, `animate-fade` for screen and subject changes, and `animate-in` for new list items; all respect reduced motion.

`components/game/emotionStyles.ts` is the single emotion label and colour table. `lib/format.ts` holds display formatting. `hooks/useSavedSessions.ts` fetches the save list, and `hooks/useLocations.ts` fetches every place for the Map page and the Scene panel's exit names. `stores/uiStore.ts` holds the open dialog and who the player is addressing.

These rules are enforced by `no-restricted-imports` blocks in [Frontend/eslint.config.js](Frontend/eslint.config.js).

## Where new code goes

- New event type: add it to `schemas/events.py`, validate it in `game/validator.py`, reduce it in `core/reducer.py`, and expose any new shape in `api/schemas.py` and `api/presenters.py`. Add tests.
- New player-driven state change (like move or pickup): add a route to the matching `api/routes/*.py` group that validates input and calls `SessionManager.commit_event`.
- New route group: add a module under `api/routes/` and include it in `api/routes/__init__.py`.
- New save artefact: extend `session/save_files.py` only.
- New backend DTO: add it to `api/schemas.py` and mirror it in `Frontend/src/contracts/api.ts`.
- New frontend workflow: server calls go in `services/`, DTO mapping in `stores/mappers.ts`, state transitions in `stores/`, route composition in `pages/`, and repeated UI in `components/`.
- New prompt input: format it in `llm/prompt_builder.py`. Keep enforcement in code (`game/validator.py`), not only in the prompt.

## Data flow

1. The UI calls `useGameStore.sendAction`, which posts to `POST /api/game/action/{session_id}`.
2. `routes/gameplay.py` resolves the session through `get_session` and calls `SessionManager.process_action`.
3. Under the session lock, the manager invokes the session's LangGraph pipeline. The pipeline retrieves memories, builds the prompt, calls Groq, parses the JSON, validates updates, commits events, and updates memory and periodic snapshots.
4. The route appends display dialogue (`session/dialogue.py`), broadcasts over WebSocket, auto-saves, and returns `ActionResponse`.
5. The frontend refreshes state and maps DTOs through `stores/mappers.ts`.

Move, clue link, pickup, and drop build an explicit event, and `SessionManager.commit_event` appends, reduces, and auto-saves it.

Persistence is per session under `Backend/data/sessions/{session_id}/`: `events.db`, manual and auto snapshots with their dialogue files, and the FAISS index and metadata. The embedding cache is shared in `Backend/data/embed_cache.db`.

## Decisions

| Decision                                                      | Reason                                                                                                    |
| ------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Modular monolith, no service split                            | One user-facing workload with shared in-process ML models; no independent scaling or ownership need yet   |
| Session orchestration moved from `api/` into `session/`       | Lifecycle and persistence are application logic, not transport; routes stay thin and testable             |
| `SessionManager` on `app.state` plus FastAPI dependencies     | Replaces a module global and ten copies of the "session not found" check                                  |
| `GameMetadataResponse` is `schemas.world_state.WorldMetadata` | One schema for seed metadata instead of two identical models                                              |
| Frontend DTO mapping in `stores/mappers.ts`                   | Pure, testable, and removes the mapping code that was inline in the store                                 |
| Single Node launcher (`scripts/dev.mjs`) replacing PowerShell | Cross-platform, one entry point, lockfile-hash setup skip, fail-fast ports, crash and Ctrl+C teardown     |
| `black` in `requirements-dev.txt`                             | Keeps a development tool out of the runtime and Docker image                                              |
| One logging setup in `log_config.py`, Uvicorn access log off  | One format and one line per request; request and session IDs on every line, including in turn threads     |
| Groq SDK retries off; `GroqClient` retries transient errors   | Two stacked retry loops could make nine calls; auth and bad-request errors now fail at once as `LLMError` |
| `/session` route outside the session-guarded layout           | Load game must work from the title screen, before any session exists                                      |
| `MasterDetail` shared by Map and People                       | Both pages were rebuilt, so the list-and-detail structure now has one home instead of a tolerated copy    |

## Allowed duplication

The clone detector (`jscpd`, run by `npm run check`) fails when duplicated code exceeds 1%. These known exceptions are kept on purpose:

- `Backend/memory/faiss_index.py`: the `MemoryEntry` constructor and `FAISSMemory.add` share a parameter list. `add` builds the entry, and merging the two would couple the index API to the storage record.
- `Frontend/src/contracts/api.ts` mirrors `Backend/api/schemas.py` by hand. The DTOs are a small, stable contract, and code generation would add a build step. Revisit if contract drift becomes a problem.
- Literal expected values in tests.

## Production notes

- Configuration comes from the environment (`Backend/config.py`, `Backend/.env.example`).
- Unhandled backend exceptions are logged, and clients get a generic error; `DEBUG_ERRORS=true` exposes details. Expected errors are `HTTPException`s.
- Groq calls have a timeout. Only transient failures (429, 5xx, connection, timeout) are retried with exponential backoff. The LLM health ping runs off the event loop.
- Logs are structured (`LOG_FORMAT=text` or `json`, `LOG_LEVEL`), carry `req` and `session` IDs, and every response returns `X-Request-ID`.
- Player input and LLM output are untrusted, and world mutations must pass `game/validator.py`.
- There is no authentication, authorisation, or rate limiting. Do not expose the backend on an untrusted network as is.

## Operations

- `npm run dev`: first-run setup, then both services. See the README.
- `npm run check`: setup, clone detection, `black --check`, backend tests, and the frontend format check, typecheck, lint, tests, and build.
- `GET /health` reports readiness. `GET /api/game/health` reports active sessions and LLM reachability; it makes a real Groq call, so do not poll it frequently.

## Growth signals

Revisit this architecture when any of these become true:

- More than one backend process is needed, for load or availability. Sessions, locks, and WebSocket connections live in process memory, so state must move to a shared store (for example Redis) and sessions would need sticky routing.
- LLM turns queue behind each other. Move turn processing to a background worker and stream results over WebSocket.
- A second game or world is added. Split `game/` per world and load seeds by id.
- A `api/routes/*.py` module passes about 250 lines, or `SessionManager` gains another responsibility. Split by feature.
- The hand-mirrored DTOs drift. Generate `contracts/api.ts` from the FastAPI OpenAPI schema.
