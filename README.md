# Test Data Automation
Runs automted tests against Sentry demos on GCP, in order to generate errors and transactions to be sent to Sentry.io

## Components / Moving parts
- `create_job.sh` -> creates GCP cron job which hits Travis requests APIs to trigger build
- `.travis.yml` -> runs automated tests / simulations
- `conftest.py` -> Sauce Labs configuration (browsers) for frontend_tests
- `backend_tests/backend_test.py` -> Hits /handled, /unhandled/, + /checkout backend demo APIs

create_cron_job.sh -> GCP-cron job (runs every 20 min from midnight-6am) -> TravisCI (runs tests)

# Tests

## FrontEnd / Selenium (`frontend_tests` directory)
Pulls up Sentry frontend in various browsers in parallel via selenium scripts.
Test case will add items to cart and then click checkout

```
pip install -r requirements.txt
py.test -s -n 2 frontend_tests
```

## Backend (`backend_tests` directory)
Hits /unhandled, /handled, + /checkout backend demo APIs
```
cd backend_tests
python backend_test.py
```
# Setup
Python2  
SAUCE_USERNAME  
SAUCE_ACCESS_KEY

If you get this error during pip install: `ERROR: Package 'setuptools' requires a different Python: 2.7.12 not in '>=3.5'` then run:
```
pip install -U pip
pip install setuptools==44.0.0

# and re-rerun:
pip install -r requirements.txt
```
# Setup: Setting up cron job to trigger simulations

We can trigger the travis builds on a schedule via Google Cloud Scheduler cron jobs.

To register:
```
./create_cron_job.sh
```

Docs:
- https://cloud.google.com/sdk/gcloud/reference/scheduler/jobs/create/
- https://docs.travis-ci.com/user/triggering-builds/

Sentry docs:
- https://docs.sentry.io/performance/distributed-tracing/
- https://docs.sentry.io/performance/performance-metrics/

# GIF
TODO

# To run "continuously"
`$ while true; do clear && pytest -s -n 10 frontend_tests; done`
