# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- ParseJobPropertiesFunction Lambda for centralized AWS Batch job attribute parsing
- Support for multi-container AWS Batch jobs using ecsProperties
- Support for multi-node parallel (MNP) AWS Batch jobs with proper child node filtering
- Comprehensive test suite with real AWS Batch job state change events including MNP examples
- Organized test structure in tests/BatchJobStatesTests/ directory
- Test runners for individual and suite-level test execution
- Documentation for test structure and usage

### Changed
- Simplified JobStatesStateMachineServerless from 8 states to 4 states
- Replaced complex state machine logic with Lambda function for better maintainability
- Centralized all job attribute parsing logic in Python code
- Improved error handling for malformed job state change events
- Enhanced support for single-container, multi-container, and multi-node parallel job definitions
- Added MNP child node detection to prevent duplicate metrics processing

### Fixed
- Proper handling of containerInstanceArn extraction from ecsProperties.taskProperties
- Correct fallback logic for attempts array in multi-container jobs
- Parent array job detection using arrayProperties.size
- MNP child node filtering using nodeDetails.isMainNode to process only main node events

## [1.0.0] - 2021-04-30
### Added
- Initial Release
