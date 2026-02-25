# Figma Light Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the mobile app UI into a bright Figma-like design while preserving existing functionality and making the timetable fully visible without horizontal scrolling.

**Architecture:** Keep `DataHandler` as the state/persistence layer and redesign only view composition in `mobile_app/main.py`. Introduce centralized light-theme tokens and reusable UI helpers (cards/chips/buttons), then migrate each screen to tokenized components. Enforce timetable “all days visible at once” by responsive width calculation instead of horizontal scroll containers.

**Tech Stack:** Python, Flet, pytest

---

### Task 1: Add Failing UI Regression Tests (TDD Red)

**Files:**
- Create: `tests/test_light_ui_regression.py`
- Test: `tests/test_light_ui_regression.py`

**Step 1: Write the failing test**

Add checks for:
- light theme assignment exists
- dark theme assignment removed
- timetable horizontal scroll wrapper removed

```python
def test_main_uses_light_theme():
    source = (ROOT / "mobile_app" / "main.py").read_text(encoding="utf-8")
    assert "page.theme_mode = ft.ThemeMode.LIGHT" in source

def test_timetable_has_no_horizontal_scroll_container():
    source = (ROOT / "mobile_app" / "main.py").read_text(encoding="utf-8")
    assert "ft.Row([timetable_grid], scroll=ft.ScrollMode.AUTO)" not in source
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_light_ui_regression.py -q`  
Expected: FAIL before UI rewrite.

### Task 2: Introduce Bright Theme Tokens + Shared UI Helpers

**Files:**
- Modify: `mobile_app/main.py`
- Test: `tests/test_light_ui_regression.py`

**Step 1: Write minimal implementation**

Add:
- light palette constants
- shared helpers (card, chip, primary button style)
- top-level light page defaults

**Step 2: Run tests**

Run: `python -m pytest tests/test_light_ui_regression.py -q`  
Expected: partial/pass depending on completed checks.

### Task 3: Redesign Home/Today/Add Project/Stats Screens

**Files:**
- Modify: `mobile_app/main.py`
- Test: `tests/test_light_ui_regression.py`

**Step 1: Redesign destination mapping**

Make navigation labels and screen hierarchy aligned with Figma feel:
- Home
- Today
- Add Project
- Timetable
- Stats

**Step 2: Rewrite content blocks with card-first layout**

- Home: greeting + purple hero + in-progress cards + groups
- Today: date strip + status chips + task cards
- Add Project: clean form sections + purple CTA
- Stats: bright card-style metrics

**Step 3: Run tests**

Run: `python -m pytest tests/test_light_ui_regression.py -q`

### Task 4: Timetable “At-a-Glance” Layout (No Horizontal Scroll)

**Files:**
- Modify: `mobile_app/main.py`
- Test: `tests/test_light_ui_regression.py`

**Step 1: Write minimal implementation**

- Calculate day column width from current page width.
- Fit columns for `월~토` within one row.
- Keep vertical scroll only for periods.
- Keep period labels/time format rules:
  - `0교시`
  - `1교시 09:00~09:50`, ...

**Step 2: Verify interactions**

- Add subject
- color reuse
- overlap validation
- delete entry

### Task 5: Full Verification + Release

**Files:**
- Modify: `mobile_app/main.py`
- Create: release tag only (git)
- Test: `tests/test_light_ui_regression.py`, existing tests

**Step 1: Run full test suite**

Run: `python -m pytest -q`  
Expected: PASS.

**Step 2: Compile check**

Run: `python -m py_compile mobile_app/main.py mobile_app/data_handler.py`  
Expected: PASS.

**Step 3: Commit**

```bash
git add mobile_app/main.py tests/test_light_ui_regression.py docs/plans/2026-02-25-figma-light-redesign-design.md docs/plans/2026-02-25-figma-light-redesign-implementation-plan.md
git commit -m "feat: redesign mobile UI with bright figma-inspired theme"
```

**Step 4: Push + APK release**

```bash
git push origin main
git tag -a android-apk-2026-02-25-figma-light1 -m "Android APK release: figma light redesign"
git push origin android-apk-2026-02-25-figma-light1
```
