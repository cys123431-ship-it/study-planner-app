# Mobile Timetable Menu Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a new timetable menu to the existing mobile app while keeping current menus, with subject add/delete, period grid rendering, and same-subject color reuse.

**Architecture:** Extend `DataHandler` with timetable storage and validation (including overlap detection and subject color persistence). Add a new timetable view in `mobile_app/main.py` and wire it into both mobile and desktop navigation. Render a period/day grid (`월~토`, `0~14교시`) with time labels (`1교시 09:00~09:50` onward) and colored blocks.

**Tech Stack:** Python, Flet, pytest

---

### Task 1: Add Failing Data Layer Tests (TDD Red)

**Files:**
- Modify: `tests/test_data_handler.py`
- Test: `tests/test_data_handler.py`

**Step 1: Write the failing test**

Add tests for:
- same-subject color reuse
- timetable overlap rejection
- timetable entry deletion

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_data_handler.py -q`
Expected: FAIL due to missing timetable APIs.

### Task 2: Implement Timetable APIs in DataHandler (TDD Green)

**Files:**
- Modify: `mobile_app/data_handler.py`
- Test: `tests/test_data_handler.py`

**Step 1: Write minimal implementation**

Add:
- default and normalized keys for timetable data
- `get_timetable_entries()`
- `get_subject_colors()`
- `add_timetable_entry(...)` with overlap check and color reuse
- `delete_timetable_entry(entry_id)`

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_data_handler.py -q`
Expected: PASS for timetable tests.

### Task 3: Add Timetable Menu and UI Rendering

**Files:**
- Modify: `mobile_app/main.py`
- Test: `tests/test_data_handler.py`

**Step 1: Add timetable view builder**

Implement:
- form for subject/day/start/end/color
- grid renderer (`월~토`, `0~14교시`)
- period labels and time text (`0교시` only label, `1교시` onward `HH:00~HH:50`)
- entry list with delete button

**Step 2: Wire navigation**

Add `시간표` destination:
- mobile `NavigationBar`
- desktop `NavigationRail`
- `show_view()` index handling

**Step 3: Run checks**

Run:
- `pytest tests/test_data_handler.py -q`
- `pytest tests/test_date_utils.py -q`

Expected: PASS.
