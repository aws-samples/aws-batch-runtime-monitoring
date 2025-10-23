# Change Log
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- ParseJobPropertiesFunction Lambda for centralized AWS Batch job attribute parsing
- Support for multi-container AWS Batch jobs using ecsProperties
- Support for multi-node parallel (MNP) AWS Batch jobs with intelligent child node processing
- **NEW**: Smart MNP child node failure handling - when an MNP child job fails, the system queries the main node status and uses that instead
- Comprehensive test suite with real AWS Batch job state change events including MNP examples
- Organized test structure in tests/BatchJobStatesTests/ directory
- Test runners for individual and suite-level test execution
- Documentation for test structure and usage
- Verification command in README to check enabled ASG metrics

### Changed
- Simplified JobStatesStateMachineServerless from 8 states to 4 states
- Replaced complex state machine logic with Lambda function for better maintainability
- Centralized all job attribute parsing logic in Python code
- **IMPORTANT**: MNP child nodes are now processed instead of skipped since they run on separate EC2 instances and provide valuable metrics
- Enhanced MNP child node logic to query main node status when child nodes fail, preventing false failure alerts
- Improved error handling for malformed job state change events
- Enhanced support for single-container, multi-container, and multi-node parallel job definitions
- Updated README documentation with clearer explanations and improved ASG monitoring instructions

### Fixed
- Proper handling of containerInstanceArn extraction from ecsProperties.taskProperties
- Correct fallback logic for attempts array in multi-container jobs
- Parent array job detection using arrayProperties.size
- Smart MNP child node processing that queries main node status on child failures
- **CRITICAL**: Fixed ASG monitoring command in README that failed when ASGs lacked MixedInstancesPolicy fields
- Improved ASG detection to handle different AWS Batch ASG configurations (Mixed Instance Policies, regular Launch Templates, etc.)
- Updated ASG search pattern from "Batch-lt" to "Batch" to catch more AWS Batch Auto-Scaling Groups

## [1.0.0] - 2021-04-30
### Added
- Initial Release
