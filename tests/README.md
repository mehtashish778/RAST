# HAZOP Analysis Tool Tests

This directory contains automated tests for the HAZOP Analysis Tool application.

## Test Structure

- `test_consequence.py`: Tests for the consequence analysis functionality
- `test_data_access.py`: Tests for the data access layer (DAOs)
- `test_database.py`: Tests for the database manager
- `test_app.py`: Tests for the main app functionality
- `conftest.py`: Shared test fixtures and configuration

## Running Tests

### Prerequisites

Install test dependencies:

```bash
pip install -r tests/requirements-test.txt
```

### Running All Tests

To run all tests with coverage reporting:

```bash
python -m pytest --cov=app
```

Or for a more detailed view:

```bash
python -m pytest --cov=app -v
```

### Running Specific Tests

To run specific test files:

```bash
python -m pytest tests/test_consequence.py -v
```

To run specific test classes or methods:

```bash
python -m pytest tests/test_consequence.py::TestConsequenceCalculator -v
python -m pytest tests/test_consequence.py::TestConsequenceCalculator::test_calculate_risk_score -v
```

## Test Coverage

Current test coverage is at 13% of the codebase, with individual module coverage as follows:

| Module                    | Coverage |
|---------------------------|----------|
| app.core.consequence.py   | 88%      |
| app.utils.data_access.py  | 53%      |
| app.utils.database.py     | 45%      |
| app/__init__.py           | 100%     |
| app.core/__init__.py      | 100%     |
| app.data/__init__.py      | 100%     |
| app.pages/__init__.py     | 100%     |
| app.utils/__init__.py     | 100%     |

Other modules currently have 0% coverage and are planned for future test development.

## Coverage Reports

After running tests with the `--cov` option, a coverage report will be generated:

- Terminal report (default)
- HTML report (generated with `--cov-report=html`)

```bash
python -m pytest --cov=app --cov-report=html
```

To view the HTML coverage report, open `htmlcov/index.html` in your web browser.

## Mocking

The test suite uses pytest-mock to mock external dependencies:

- SQLAlchemy is mocked to avoid actual database connections
- OS functions are mocked to prevent file system operations
- Streamlit components are mocked for UI testing

## Continuous Testing

To run tests automatically during development, you can use pytest-watch:

```bash
pip install pytest-watch
ptw
```

This will monitor file changes and run tests automatically when files are modified. 