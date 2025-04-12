import os
from playwright.sync_api import sync_playwright

SAVE_DIR = "submission_pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    # Open the submission page
    page.goto("https://www.gradescope.com/courses/596073/assignments/3636941/submissions/211665410")

    # Wait and get the href from the "Download Graded Copy" button
    page.wait_for_selector("a:has-text('Download Graded Copy')", timeout=10000)
    pdf_element = page.query_selector("a:has-text('Download Graded Copy')")
    relative_href = pdf_element.get_attribute("href")

    if not relative_href:
        print("❌ Could not find the PDF link.")
    else:
        full_url = "https://www.gradescope.com" + relative_href
        print(f"📎 PDF URL: {full_url}")

        # Use Playwright's request context to download with auth
        request_context = context.request
        response = request_context.get(full_url)

        if response.status == 200:
            file_path = os.path.join(SAVE_DIR, "graded_submission.pdf")
            with open(file_path, "wb") as f:
                f.write(response.body())
            print(f"✅ Downloaded graded PDF to: {file_path}")
        else:
            print(f"❌ Failed to download PDF. Status: {response.status}")

    browser.close()
