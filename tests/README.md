# Tests Directory

This directory contains all test suites for the AWS Batch Runtime Monitoring project.

## Structure

```
tests/
├── README.md                           # This file
├── run_all_tests.py                   # Main test runner for all test suites
└── BatchJobStatesTests/               # Tests for Batch Job States functionality
    ├── batch-job-state-change-events/ # Sample AWS Batch events for testing
    │   ├── batch-event-RUNNABLE.json
    │   ├── batch-event-RUNNING.json
    │   ├── batch-event-STARTING.json
    │   └── batch-event-SUCCEEDED.json
    ├── run_tests.py                   # Test runner for BatchJobStates tests
    ├── test_parse_job_attributes.py   # Tests for ParseJobPropertiesFunction
    └── test_state_machine.py          # State machine simulation tests
```

## Running Tests

### Run All Tests
```bash
uv run python tests/run_all_tests.py
```

### Run Specific Test Suite
```bash
uv run python tests/BatchJobStatesTests/run_tests.py
```

### Run Individual Tests
```bash
uv run python tests/BatchJobStatesTests/test_parse_job_attributes.py
uv run python tests/BatchJobStatesTests/test_state_machine.py
```

## Test Suites

### BatchJobStatesTests
Tests for the simplified Batch Job States state machine and Lambda function:

- **test_parse_job_attributes.py**: Tests the ParseJobPropertiesFunction Lambda
  - Tests parsing of different job state events (STARTING, RUNNING, SUCCEEDED)
  - Tests parent array job detection
  - Tests error handling with malformed events
  - Tests both single-container and multi-container job support

- **test_state_machine.py**: Simulates the complete state machine execution
  - Tests the full state machine flow without AWS Step Functions
  - Tests different execution paths (normal flow, parent array job skip, invalid state)
  - Validates state transitions and data flow

## Adding New Test Suites

To add tests for other state machines:

1. Create a new subdirectory under `tests/` (e.g., `tests/OtherStateMachineTests/`)
2. Add your test files and a `run_tests.py` runner
3. Update `tests/run_all_tests.py` to include the new test suite
4. Update this README with documentation for the new tests

## Test Data

Sample AWS Batch job state change events are stored in `BatchJobStatesTests/batch-job-state-change-events/` and include:
- RUNNABLE state event
- RUNNING state event  
- STARTING state event (with ecsProperties for multi-container jobs)
- SUCCEEDED state event

These events are based on real AWS Batch job state changes and include both single-container and multi-container job examples.