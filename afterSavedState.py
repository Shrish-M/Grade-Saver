from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    page.goto("https://www.gradescope.com/courses/1011178/assignments/5997159/submissions/320675452")
    page.wait_for_selector('.submissionOutlineQuestion--title')

    toggles = page.query_selector_all('.submissionOutlineQuestion--title')
    print(f"Found {len(toggles)} questions")

    rubric_by_question = {}

    for idx, toggle in enumerate(toggles):
        try:
            toggle.click()
            time.sleep(1)  # Wait for rubric items to load

            rubric_items = page.query_selector_all('.submissionOutlineRubricItem')
            applied_rubrics = []

            for item in rubric_items:
                sr_only = item.query_selector('span.sr-only')
                if not sr_only or "unapplied rubric item" not in sr_only.inner_text().lower():
                    # ✅ This is an applied rubric
                    points_el = item.query_selector('[aria-label]')
                    points = points_el.get_attribute('aria-label').strip() if points_el else "No points info"

                    desc_el = item.query_selector('.submissionOutlineRubricItem--description')
                    if desc_el:
                        raw_html = desc_el.inner_html()
                        clean_text = BeautifulSoup(raw_html, "html.parser").get_text().strip()
                        applied_rubrics.append({
                            "points": points,
                            "comment": clean_text
                        })

            if applied_rubrics:
                rubric_by_question[f"Question {idx+1}"] = applied_rubrics

        except Exception as e:
            print(f"Toggle click failed for Question {idx+1}: {e}")

    browser.close()

    # ✅ Display applied rubrics only
    for q, rubrics in rubric_by_question.items():
        print(f"\n {q}:")
        for i, r in enumerate(rubrics):
            print(f" Rubric {i+1}: {r['points']} — {r['comment']}")
