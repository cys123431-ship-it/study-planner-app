# Study Planner Refactor Plan

## Goal
Turn the current single-file Flet prototype into a maintainable Android planner app with clear module boundaries, safer persistence, and test coverage.

## External Reference
Repository: `tasks/tasks`  
Why this reference:
- separates concerns into dedicated modules (`app`, `data`, `wear`, `kmp`)
- keeps CI and release automation as first-class parts of the project
- treats migration and reliability as product features, not afterthoughts

## Current Baseline (This Repo)
- UI and orchestration are concentrated in `mobile_app/main.py`.
- Persistence is file-based JSON in `mobile_app/data_handler.py`.
- Week/month/day keys were previously generated with ad-hoc logic in the UI layer.
- No test suite existed for storage/date behavior.

## Target Architecture
1. `mobile_app/domain/`
   - entities: `Task`, `WeeklyTask`, `MonthlyGoal`, `Memo`
   - policies: completion-rate calculations, key-generation interfaces
2. `mobile_app/data/`
   - `json_store.py`: atomic read/write, backup/restore, schema migration
   - `repositories.py`: daily/weekly/monthly abstractions
3. `mobile_app/presentation/`
   - UI builders per screen (`daily_view.py`, `weekly_view.py`, `monthly_view.py`, `dashboard_view.py`)
   - no direct file IO in view code
4. `mobile_app/services/`
   - date/time key service (already started with `date_utils.py`)

## Incremental Migration Steps
1. Stabilize data layer
   - done: atomic write, backup recovery, schema normalization
   - next: explicit schema version in JSON
2. Isolate date policy
   - done: `date_utils.py` with ISO week key support
   - next: inject clock provider for deterministic tests
3. Split `main.py`
   - extract each view builder into separate module
   - keep a thin navigation shell in `main.py`
4. Introduce repository interfaces
   - `TaskRepository`, `GoalRepository`, `MemoRepository`
   - keep JSON implementation first, add Room/SQLite option later
5. Expand tests
   - unit tests for repositories and date service
   - smoke tests for critical UI flows

## Testing and CI Strategy
- Keep fast unit tests in `tests/` and run them on every push.
- Gate APK build with test pass (already wired in workflow).
- Add migration regression fixtures once schema versioning starts.

## Definition of Done for Refactor
- `main.py` reduced to navigation/wiring only.
- storage logic fully outside UI layer.
- deterministic tests cover key persistence and date-boundary behavior.
- build pipeline runs tests before packaging artifacts.
