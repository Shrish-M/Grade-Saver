from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    page.goto("https://www.gradescope.com/courses/1011178/assignments/5997159/submissions/320673965")

    # Wait for submission outline (accordion panel)
    page.wait_for_selector('.submissionOutlineQuestion--title')

    # Click all collapsed rubric toggles to expand
    toggles = page.query_selector_all('.submissionOutlineQuestion--title')
    print(f"Found {len(toggles)} rubric toggles")

    for toggle in toggles:
        try:
            toggle.click()
            time.sleep(0.5)  # Small delay to allow DOM update
        except Exception as e:
            print(f"Toggle click failed: {e}")

    # Now wait for the rubric details to load
    time.sleep(2)

    # Now extract rubric descriptions
    rubric_blocks = page.query_selector_all('.submissionOutlineRubricItem--description')
    for i, block in enumerate(rubric_blocks):
        raw_html = block.inner_html()
        # Strip tags manually or keep raw HTML
        clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
        print(f"\n🔹 Rubric Item {i+1}:")
        print(clean_text)

    browser.close()