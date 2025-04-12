# from playwright.sync_api import sync_playwright
# import time
# from bs4 import BeautifulSoup
#
# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)
#     context = browser.new_context(storage_state="auth.json")
#     page = context.new_page()
#
#     page.goto("https://www.gradescope.com/courses/1011178/assignments/5997159/submissions/320675452")
#     page.wait_for_selector('.submissionOutlineQuestion--title')
#
#     toggles = page.query_selector_all('.submissionOutlineQuestion--title')
#     print(f"Found {len(toggles)} questions")
#
#     rubric_by_question = {}
#
#     for idx, toggle in enumerate(toggles):
#         try:
#             toggle.click()
#             time.sleep(1)  # Wait for content to appear
#             rubric_blocks = page.query_selector_all('.submissionOutlineRubricItem--description')
#             grades = page.query_selector_all('submissionOutlineRubricItem')
#             rubrics = []
#             for block in rubric_blocks:
#                 raw_html = block.inner_html()
#                 clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
#                 rubrics.append(clean_text)
#
#             rubric_by_question[f"Question {idx+1}"] = rubrics
#         except Exception as e:
#             print(f"Toggle click failed for Question {idx+1}: {e}")
#
#     # Print grouped rubric info
#     for q, items in rubric_by_question.items():
#         print(f"\n{q}:")
#         for i, item in enumerate(items):
#             print(f"  Rubric {i+1}: {item}")
#
#     browser.close()


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
            time.sleep(1)  # Wait for content to appear
            rubric_blocks = page.query_selector_all('.submissionOutlineRubricItem--description')
            grades = page.query_selector_all('submissionOutlineRubricItem')
            rubrics = []
            for block in rubric_blocks:
                if "applied rubric item" in rubric_blocks:
                    if points_text contains "-":
                        raw_html = block.inner_html()
                        clean_text = BeautifulSoup(raw_html, "html.parser").get_text()
                        rubrics.append(clean_text)
                    else:
                        continue
                else:
                    continue

            rubric_by_question[f"Question {idx+1}"] = rubrics
        except Exception as e:
            print(f"Toggle click failed for Question {idx+1}: {e}")

    # Print grouped rubric info
    for q, items in rubric_by_question.items():
        print(f"\n{q}:")
        for i, item in enumerate(items):
            print(f"  Rubric {i+1}: {item}")

    browser.close()