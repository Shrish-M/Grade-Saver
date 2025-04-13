import os
from playwright.sync_api import sync_playwright
import time
import re
from bs4 import BeautifulSoup
import json
import fitz

SAVE_DIR = "submission_pdfs"
TRIM_DIR = "trimmed_pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(TRIM_DIR, exist_ok=True)
rubric_by_question = {}

def trim_pdf(input_path, output_path, desired_page_count):
    doc = fitz.open(input_path)
    total_pages = len(doc)

    if desired_page_count >= total_pages:
        print("✅ No need to trim — already within page limit.")
        doc.save(output_path)
        return

    # Calculate how many to remove from the front
    pages_to_remove = total_pages - desired_page_count
    print(f"📄 Total pages: {total_pages}, trimming first {pages_to_remove} pages...")

    # Create a new PDF with only the last `desired_page_count` pages
    new_doc = fitz.open()
    for i in range(pages_to_remove, total_pages):
        new_doc.insert_pdf(doc, from_page=i, to_page=i)

    new_doc.save(output_path)
    print(f"✅ Trimmed PDF saved as: {output_path}")

def run_main(page_url):
    print("main called")
    if not os.path.exists("auth.json"):
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

    # this part extracts the rubrics where student went wrong
    # Dictionary to store rubric data grouped by main question and subquestions

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        # Use one of your Gradescope submission URLs
        #page.goto("https://www.gradescope.com/courses/883458/assignments/5337980/submissions/291925557")
        page.goto(page_url)
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

    # this part extracts number of pages
    # --- Extract Page Count ---
        try:
            print("Attempting to find page count...")
            # Locate the div containing the React props
            viewer_div_locator = page.locator('div[data-react-class="AssignmentSubmissionViewer"]')
            # Wait for the element to be present
            viewer_div_locator.wait_for(state='attached', timeout=10000)
            json_string = viewer_div_locator.get_attribute('data-react-props')

            if json_string:
                react_props = json.loads(json_string)
                # Safely access nested keys using .get()
                pdf_attachment = react_props.get('pdf_attachment')
                if pdf_attachment:
                    page_count_raw = pdf_attachment.get('page_count')
                    if page_count_raw is not None:
                        page_count = int(page_count_raw) # Store as integer
                        print(f"Found page count: {page_count}")
                    else:
                        print("❌ 'page_count' key not found in pdf_attachment.")
                else:
                    print("❌ 'pdf_attachment' key not found in JSON props.")
            else:
                print("❌ Could not retrieve data-react-props attribute.")

        except json.JSONDecodeError:
            print("❌ Error decoding JSON data from data-react-props.")
        except Exception as e:
            print(f"❌ Could not extract page count: {e}")
            # page.screenshot(path="error_screenshot_pages.png")


    # this part extracts the submission pdf and trims it
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

    # this part trims the PDF
    trim_pdf("submission_pdfs/graded_submission.pdf", "trimmed_pdfs/trimmed_submission.pdf", page_count)

# function to print nested structure (for debugging)
def printRubrics():
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
