# Task: Test Inventory and Coverage Documentation

## Objective

Document the test cases that have already been implemented and/or executed for the specified module or feature.

**Target scope:** `[MODULE / FEATURE / API / COMPONENT]`

Inspect the existing test code, relevant implementation, test configuration, and execution results. Produce a structured test inventory that allows a human reviewer to understand exactly what has and has not been tested.

## Instructions

1. Inspect only the specified scope and its directly relevant dependencies.
2. Identify existing test cases from test files, test functions, test descriptions, assertions, and available execution results.
3. Do not invent test cases, expected results, or execution outcomes.
4. Do not write new tests, modify existing tests, or change production code for this task.
5. Distinguish clearly between:
   - Implemented: the test exists in the codebase.
   - Executed: the test was actually run.
   - Passed / Failed: the execution result confirms the outcome.
   - Not executed / Blocked: the test has not run or could not be executed.
6. If a test exists but its expected behavior or assertions are unclear, explicitly identify the limitation.
7. Do not assume that a requirement is covered merely because related code exists.
8. If possible, reference the exact test file, test function, and relevant line numbers as evidence.

## Required Output

### 1. Scope Summary

Briefly describe:

- The module or feature reviewed.
- The relevant endpoints, functions, or behaviors.
- The test files examined.
- The execution evidence available.

### 2. Test Inventory

Produce a Markdown table with the following columns:

| Test ID | Feature / Component | Test Scenario | Preconditions / Test Data | Test Action / Input | Expected Result / Assertion | Test Type | Test Location | Status |
|---|---|---|---|---|---|---|---|---|

Rules:

- Assign a stable ID to each documented test case, such as `TC-AUTH-001`.
- Describe each scenario precisely enough for another developer to reproduce it.
- Use the expected result actually specified or asserted in the test. If it cannot be established, write `Unspecified`.
- Include the exact file path and test function name whenever available.
- Use separate rows for distinct scenarios, even when they belong to the same test function.
- Do not claim that a test passed based only on reading its code.

### 3. Execution Summary

Report the available results:

- Total documented test cases.
- Number implemented.
- Number executed.
- Number passed.
- Number failed.
- Number skipped, blocked, or not executed.

Do not treat missing execution evidence as a pass.

### 4. Coverage Gaps and Limitations

List:

- Relevant behaviors for which no existing test was found.
- Existing tests with insufficient assertions.
- Scenarios whose expected behavior is ambiguous.
- Test cases that exist but have not been executed.

Clearly distinguish verified gaps from areas that could not be inspected.

### 5. Exporting

Exporting this report as .md file, in `PROJECT_ROOT/backend_rag/docs`. The name of this reporting file will be `<module/feature>-SPEC-TESTS.md`

### 6. Final Constraints

This task is documentation and test inventory only.

Do not implement additional tests, refactor code, fix unrelated issues, or change the system's behavior. Wait for a separate instruction before implementing or executing a new, user-provided test case matrix.