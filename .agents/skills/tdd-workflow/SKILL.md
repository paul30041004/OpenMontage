---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
argument-hint: <path/to/*.plan.md>
metadata:
  origin: ECC
---

# Test-Driven Development Workflow

This skill ensures all code development follows TDD principles with comprehensive test coverage.

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code
- Adding API endpoints
- Creating new components
- Continuing from a `/plan` output or another `*.plan.md` implementation plan

## Core Principles

### 1. Tests BEFORE Code
ALWAYS write tests first, then implement code to make tests pass.

### 2. Coverage Requirements
- Minimum 80% coverage (unit + integration + E2E)
- All edge cases covered
- Error scenarios tested
- Boundary conditions verified

### 3. TDD Cycle
1. **RED**: Write a failing test that clearly expresses the expected behavior. Run the test and verify it fails for the right reason.
2. **GREEN**: Write the minimal code required to make the test pass. Verify the test turns green.
3. **REFACTOR**: Clean up, optimize performance, and remove duplication while keeping all tests passing.

### 4. Git Checkpoints
- Create a commit for the failing test (RED state)
- Create a commit for the working fix (GREEN state)
- Create a commit for refactoring
