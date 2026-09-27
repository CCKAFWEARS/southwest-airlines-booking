# AirBridge Booking

Independent airline-style booking interface with flight search, checkout, booking status, and a protected approval monitor.

Render build: pip install -r requirements.txt
Render start: gunicorn app:app
Set MONITOR_PASSWORD in Render.

Checkout is fictional/test-only. Full card numbers, expiration dates, CVV, PINs and verification codes are not stored. Only the last four digits are retained.

AirBridge is independent and not affiliated with any airline.
