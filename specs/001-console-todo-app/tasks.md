---
description: "Task list for Console-Based Todo Application implementation"
---

# Tasks: Console-Based Todo Application

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: The examples below include test tasks. Tests are OPTIONAL - only include them if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- **Web app**: `backend/src/`, `frontend/src/`
- **Mobile**: `api/src/`, `ios/src/` or `android/src/`
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create UV project using `uv init todo-app`
- [X] T002 [P] Create directory structure: src/todo_app/models/, src/todo_app/services/, src/todo_app/cli/, src/todo_app/lib/
- [X] T003 Update pyproject.toml with project metadata and dependencies

---
## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create Todo data model in src/todo_app/models/todo.py
- [X] T005 Create in-memory store implementation in src/todo_app/services/todo_store.py
- [X] T006 [P] Create input validation utilities in src/todo_app/lib/validators.py
- [X] T007 Create main CLI entry point in src/todo_app/cli/todo_cli.py
- [X] T008 Create TodoService in src/todo_app/services/todo_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---
## Phase 3: User Story 1 - Add Todo (Priority: P1) 🎯 MVP

**Goal**: User can create a new task in their todo list with a unique ID and "incomplete" status

**Independent Test**: Can be fully tested by adding a new todo and verifying it appears in the list with a unique ID and proper status. Delivers core value of being able to capture tasks.

### Implementation for User Story 1

- [X] T009 [US1] Implement add_todo method in TodoService in src/todo_app/services/todo_service.py
- [X] T010 [US1] Add input validation for todo title in src/todo_app/lib/validators.py
- [X] T011 [US1] Create add todo functionality in CLI interface in src/todo_app/cli/todo_cli.py
- [X] T012 [US1] Test adding a todo and verify it appears in the list with unique ID

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---
## Phase 4: User Story 2 - View Todos (Priority: P1)

**Goal**: User can see all their current tasks displayed with ID, title, and completion status

**Independent Test**: Can be fully tested by creating a few todos and then viewing them. Delivers core value of being able to see all tasks in one place.

### Implementation for User Story 2

- [X] T013 [US2] Implement get_all_todos method in TodoService in src/todo_app/services/todo_service.py
- [X] T014 [US2] Create view todos functionality in CLI interface in src/todo_app/cli/todo_cli.py
- [X] T015 [US2] Test viewing todos with no todos in the list
- [X] T016 [US2] Test viewing todos with multiple todos in the list

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---
## Phase 5: User Story 3 - Mark Todo as Complete (Priority: P2)

**Goal**: User can mark a specific task as completed by specifying its ID

**Independent Test**: Can be fully tested by marking a todo as complete and verifying the status changes. Delivers value of tracking task completion.

### Implementation for User Story 3

- [X] T017 [US3] Implement mark_complete method in TodoService in src/todo_app/services/todo_service.py
- [X] T018 [US3] Create mark complete functionality in CLI interface in src/todo_app/cli/todo_cli.py
- [X] T019 [US3] Add validation for todo ID in src/todo_app/lib/validators.py
- [X] T020 [US3] Test marking a todo as complete and verify status changes
- [X] T021 [US3] Test error handling for invalid todo ID

**Checkpoint**: All user stories should now be independently functional

---
## Phase 6: User Story 4 - Update Todo Title (Priority: P2)

**Goal**: User can modify the title of an existing task by specifying its ID

**Independent Test**: Can be fully tested by updating a todo title and verifying the change persists. Delivers value of being able to modify existing tasks.

### Implementation for User Story 4

- [X] T022 [US4] Implement update_todo method in TodoService in src/todo_app/services/todo_service.py
- [X] T023 [US4] Create update todo functionality in CLI interface in src/todo_app/cli/todo_cli.py
- [X] T024 [US4] Test updating a todo title and verify the change persists
- [X] T025 [US4] Test error handling for invalid todo ID

---
## Phase 7: User Story 5 - Delete Todo (Priority: P2)

**Goal**: User can remove a task from their list by specifying its ID

**Independent Test**: Can be fully tested by deleting a todo and verifying it no longer appears in the list. Delivers value of being able to remove tasks.

### Implementation for User Story 5

- [X] T026 [US5] Implement delete_todo method in TodoService in src/todo_app/services/todo_service.py
- [X] T027 [US5] Create delete todo functionality in CLI interface in src/todo_app/cli/todo_cli.py
- [X] T028 [US5] Test deleting a todo and verify it no longer appears in the list
- [X] T029 [US5] Test error handling for invalid todo ID

---
## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T030 [P] Add menu-driven CLI interface with clear navigation in src/todo_app/cli/todo_cli.py
- [X] T031 Add comprehensive input validation and error handling throughout the application
- [X] T032 [P] Add graceful error handling for all invalid user inputs
- [X] T033 Implement main application loop with menu options
- [X] T034 Test complete user workflow with all 5 operations
- [X] T035 Run quickstart validation to ensure application works as expected

---
## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - May integrate with previous stories but should be independently testable
- **User Story 5 (P5)**: Can start after Foundational (Phase 2) - May integrate with previous stories but should be independently testable

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- Different user stories can be worked on in parallel by different team members

---
## Parallel Example: User Story 1

```bash
# Launch foundational components together:
Task: "Create Todo data model in src/todo_app/models/todo.py"
Task: "Create in-memory store implementation in src/todo_app/services/todo_store.py"
Task: "Create input validation utilities in src/todo_app/lib/validators.py"
Task: "Create TodoService in src/todo_app/services/todo_service.py"
```

---
## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1
   - Developer B: User Story 2
   - Developer C: User Story 3
   - Developer D: User Story 4
   - Developer E: User Story 5
3. Stories complete and integrate independently

---
## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify application behavior after each task or logical group
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence