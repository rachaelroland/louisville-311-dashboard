# Running Tests

## Quick Test

Run the full test suite:

```bash
uv run pytest test_dashboard.py -v
```

## Test with Coverage

```bash
uv run pytest test_dashboard.py -v --tb=short
```

## Run Specific Test Category

```bash
# Test only endpoints
uv run pytest test_dashboard.py::TestEndpoints -v

# Test only data loading
uv run pytest test_dashboard.py::TestDataLoading -v

# Test only home page content
uv run pytest test_dashboard.py::TestHomePageContent -v
```

## Run Single Test

```bash
uv run pytest test_dashboard.py::TestEndpoints::test_home_endpoint -v
```

## Integration Test (Manual)

Start the dashboard and test all endpoints:

```bash
# Terminal 1: Start dashboard
uv run python dashboard_app.py

# Terminal 2: Test endpoints
for endpoint in "/" "/call-center" "/topics" "/sentiment" "/urgency" "/business"; do
  echo -n "Testing $endpoint: "
  curl -s -o /dev/null -w "%{http_code}\n" "http://localhost:5002$endpoint"
done
```

Expected output: All endpoints return `200`

## Test Results

See `TEST_RESULTS.md` for complete test verification report.

Last test run: 43/43 tests passed (100% success rate)
