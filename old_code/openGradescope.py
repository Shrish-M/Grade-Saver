
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    # Go to Gradescope login
    page.goto("https://www.gradescope.com")

    print("👉 Please log in manually in the opened browser window.")
    print("👉 Once you're fully logged in, press ENTER here to save your session.")
    input()

    # Save session state
    context.storage_state(path="auth.json")
    print("✅ Session saved as auth.json!")

    browser.close()