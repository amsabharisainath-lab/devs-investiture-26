# Email and OD PDF Smoke Test

This test covers only the assigned work:

1. Generate and validate the OD PDF.
2. Send a registration-success email.
3. Send an OD email with the generated PDF attached.

It does not require the frontend, PostgreSQL, Redis, Celery, OAuth, or any registration record.

## What changed for testing

The following additions are testing support only:

- `server/scripts/test_email_pdf.py` directly tests PDF creation, registration email, and OD email with attachment.
- `email-pdf-test` is an opt-in Docker Compose service under the `test` profile.
- `PYTHONPATH=/app` is set only on that test service so the script can import the server `app` package.
- `EMAIL_TEST_TO` identifies the mailbox that receives the test messages.

The normal `api` and `worker` services are not started by the test command. Running `docker compose up` without `--profile test` does not run the test service.

The OD worker correction in `server/app/worker/tasks.py` is an application fix, not disposable test code: it uses the real `User` fields (`department`, `roll_no`) and the real PDF function (`create_student_od_task`). Keep that correction when deploying.

## Configuration

Add these values to the repository `.env` file used by Docker Compose:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-sender@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-sender@gmail.com
EMAIL_TEST_TO=your-receiving-address@example.com
```

For Gmail, use an App Password, not the normal account password. Never commit `.env` or credentials.

## Run with Docker

Build and run only the opt-in test service:

```bash
docker compose --profile test run --rm email-pdf-test
```

Expected output:

```text
PASS PDF creation: ... bytes, 1 page(s)
PASS registration email: sent to ...
PASS OD email with PDF attachment: sent to ...
ALL EMAIL/PDF TESTS PASSED
```

The test calls `create_student_od_task` with the exact same values already used by the existing local test in `create_od_pdf.py`: `Computer Science and Engineering`, `Kamlesh`, `CS2026101`, and `3`. It therefore tests the current PDF function without changing its formatting or adding a second template.

The generated PDF is written inside the temporary container at `/tmp/devs_od_request_final.pdf`. To retain it locally:

```bash
docker compose --profile test run --rm -v "${PWD}/test-output:/tmp" email-pdf-test
```

On PowerShell, use `${PWD.Path}/test-output:/tmp` for the volume path.

## Run inside the worker container

If the worker image is already running, the same script can be executed there:

```bash
docker exec devs_investiture_worker python scripts/test_email_pdf.py
```

## Worker integration correction

The OD Celery task now uses the actual `User` fields (`department`, `roll_no`) and the actual PDF pipeline entry point (`create_student_od_task`). The task still requires a real eligible registration with `AttendanceDecision.PRESENT`; the standalone smoke test intentionally avoids that database workflow.

## Failure interpretation

- `Missing environment variables`: SMTP configuration was not passed into the container.
- `wkhtmltopdf is not installed`: rebuild the server image; the Dockerfile installs it.
- SMTP authentication/connection error: verify host, port, App Password, and sender settings.
- PDF validation error: inspect the generated PDF and the image assets under `server/app/dependancies/`.

## Before deployment

1. Do not run `docker compose --profile test run --rm email-pdf-test` in production.
2. Remove `EMAIL_TEST_TO` and any personal SMTP test credentials from the deployment environment.
3. Keep only real production SMTP variables for the worker: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM`.
4. The test service and script may remain in the repository because the test service is profile-gated, but remove the `email-pdf-test` block from `docker-compose.yml` if the production repository must contain no test service.
5. No production code needs a `PYTHONPATH` change. The `/app` path setting is scoped only to the test service.

Normal deployment remains:

```bash
docker compose up -d --build api worker
```