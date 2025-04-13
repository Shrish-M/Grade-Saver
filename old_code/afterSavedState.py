
# VERSION 2


from playwright.sync_api import sync_playwright
import time
import re
from bs4 import BeautifulSoup
import json

# Dictionary to store rubric data grouped by main question and subquestions
rubric_by_question = {}

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    # Use one of your Gradescope submission URLs
    #page.goto("https://www.gradescope.com/courses/883458/assignments/5337980/submissions/291925557")
    page.goto("https://www.gradescope.com/courses/1011178/assignments/5997159/submissions/320691258#Question_2-rubric")
    page.wait_for_selector('.submissionOutlineQuestion--title')

    # Get all toggles that (might) represent questions and subquestions.
    toggles = page.query_selector_all('.submissionOutlineQuestion--title')
    print(f"Found {len(toggles)} question toggles")

    current_main_key = None  # to track the current main question number
    current_sub_key = None   # to track the current subquestion number

    for toggle in toggles:
        # Get the text from the toggle element
        toggle_text = toggle.inner_text().strip()
        # For debugging, print the toggle's raw text
        # print("Toggle text:", toggle_text)

        # Check if this toggle represents a main question.
        main_match = re.search(r"Question\s*(\d+)", toggle_text, re.IGNORECASE)
        if main_match:
            # This is a main question toggle. Set the current main question key.
            current_main_key = f"Question {main_match.group(1)}"
            # Initialize its structure if not already done.
            if current_main_key not in rubric_by_question:
                rubric_by_question[current_main_key] = {"main": [], "sub": {}}
            # Reset current_sub_key because we're now on a new main question.
            current_sub_key = None
        else:
            # Check if the toggle text starts with a subquestion number like "1.1", "2.3", etc.
            sub_match = re.search(r"^(\d+\.\d+)", toggle_text)
            if sub_match:
                # Use the subquestion number as a key.
                current_sub_key = sub_match.group(1)
                # If no main question has been identified yet (edge case), assign a dummy main question.
                if current_main_key is None:
                    current_main_key = f"Question Unknown"
                    rubric_by_question.setdefault(current_main_key, {"main": [], "sub": {}})
                # Initialize the sub-question group if it doesn't exist.
                if current_sub_key not in rubric_by_question[current_main_key]["sub"]:
                    rubric_by_question[current_main_key]["sub"][current_sub_key] = []
            else:
                # Fallback: if the toggle doesn't match either format, treat it as a main question.
                current_main_key = toggle_text
                if current_main_key not in rubric_by_question:
                    rubric_by_question[current_main_key] = {"main": [], "sub": {}}
                current_sub_key = None

        # Now click the toggle and extract the rubric data.
        try:
            toggle.click()
            time.sleep(1)  # Allow rubric items to load

            rubric_items = page.query_selector_all('.submissionOutlineRubricItem')
            applied_rubrics = []


            for item in rubric_items:
                has_annotation = item.query_selector(".annotationsTally")
                sr_only = item.query_selector('span.sr-only')
                # Check for an "applied" rubric item. (Adjust condition if needed.)
                if sr_only and "unapplied rubric item" in sr_only.inner_text().lower():
                    if not has_annotation:
                        continue  # Skip unapplied items.
                # Otherwise, treat this as an applied rubric item.
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

            # Now, save the extracted rubric items.
            if current_sub_key:
                # We're processing a subquestion toggle.
                rubric_by_question[current_main_key]["sub"][current_sub_key] = applied_rubrics
            else:
                # This is a main question toggle.
                rubric_by_question[current_main_key]["main"] = applied_rubrics

        except Exception as e:
            print(f"Toggle click failed for toggle with text '{toggle_text}': {e}")

    browser.close()

# For debugging, print the nested structure
for main_q, data in rubric_by_question.items():
    print(f"\n{main_q}:")
    if data["main"]:
        print("  Main Rubric:")
        for idx, r in enumerate(data["main"]):
            print(f"    Rubric {idx+1}: {r['points']} — {r['comment']}")
    if data["sub"]:
        for sub_q, rubrics in data["sub"].items():
            print(f"  Subquestion {sub_q}:")
            for idx, r in enumerate(rubrics):
                print(f"    Rubric {idx+1}: {r['points']} — {r['comment']}")

# Write the aggregated rubric data to a JSON file for later use.
output_filename = "rubric_data.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(rubric_by_question, f, indent=4)

print(f"\nRubric data successfully written to {output_filename}")