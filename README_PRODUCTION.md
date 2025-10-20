Production deployment checklist for SohojWeb

1) Environment variables (minimum):
   - DJANGO_SECRET_KEY: a strong random secret
   - DJANGO_DEBUG=False
   - ALLOWED_HOSTS=yourdomain.com
   - BKASH_APP_KEY, BKASH_APP_SECRET, BKASH_USERNAME, BKASH_PASSWORD
   - BKASH_WEBHOOK_SECRET: secret for verifying webhook HMAC
   - DEFAULT_FROM_EMAIL
   - DATABASE_URL (or configure DATABASES appropriately)

2) Static & media
   - Run `python manage.py collectstatic --noinput` to collect static files.
   - Configure a production media store (S3 recommended) and update MEDIA_URL and storage backend.
   - Whitenoise is included for serving static files in simple deployments.

3) Web server
   - Use gunicorn/uvicorn with Daphne/ASGI if needed. Example:
     gunicorn SohojBiniyog.wsgi:application --bind 0.0.0.0:8000 --workers 3

4) HTTPS & Security
   - Terminate TLS at a reverse proxy (NGINX, Cloud Run, Load Balancer).
   - Set SECURE_SSL_REDIRECT, SESSION_COOKIE_SECURE, CSRF_COOKIE_SECURE to True.
   - Configure HSTS headers.

5) Webhooks & background jobs
   - Expose `/payments/bkash/webhook/` over HTTPS, ensure webhook secret configured.
   - Run a background worker or scheduled job for `reprocess_webhooks` and reconciliation.

6) Monitoring & Logging
   - Configure Sentry or similar.
   - Send logs to a centralized logging system.

7) Database migrations
   - Run `python manage.py migrate` during deploy.

8) Backups
   - Schedule database and media backups.

Extra recommendations:
 - Use presigned URLs for private media (KYC docs, receipts).
 - Add CI pipeline to run tests and lint on PRs.
 - Rotate secrets and use a secrets manager.
