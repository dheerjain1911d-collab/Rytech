# Fix Login after MongoDB Addition

## Steps
- [x] 1. Create plan and get approval
- [x] 2. Fix `auth_callback()` in `app.py` — robust userinfo + MongoDB error handling
- [x] 3. Fix `otp_setup()` in `app.py` — upsert=True + proper error handling + flash messages
- [x] 4. Fix `load_user()` in `app.py` — wrap MongoDB in try/except
- [x] 5. Fix `history()` in `app.py` — wrap MongoDB in try/except
- [x] 6. Update `templates/base.html` — add flash messages container
- [x] 7. Verify/edits as needed

