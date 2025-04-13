import os
import json
from playwright.sync_api import sync_playwright
import fitz

SAVE_DIR = "submission_pdfs"
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize variables to store extracted data

def get_PDF():
    with sync_playwright() as p:
        # Consider headless=True for actual scraping runs
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        submission_url = "https://www.gradescope.com/courses/596073/assignments/3636941/submissions/211665410"
        print(f"Navigating to: {submission_url}")
        page.goto(submission_url)

        # Wait for the page to likely be fully loaded
        # You might need to adjust the wait condition based on Gradescope's behavior
        page.wait_for_load_state('networkidle', timeout=20000) # Increased timeout
        print("Page loaded.")

        # --- Extract Submitter Name ---
        try:
            print("Attempting to find submitter name...")
            # Locate the heading "Student" and find the list item following it
            name_locator = page.locator('div.submissionOutline--section:has(h2:has-text("Student")) li.submissionOutlineHeader--groupMember')
            # Wait for the element to be visible before getting text
            name_locator.wait_for(state='visible', timeout=10000)
            submitter_name_raw = name_locator.text_content()
            # Clean up whitespace
            submitter_name = submitter_name_raw.strip() if submitter_name_raw else "Not Found"
            print(f"Found submitter name: {submitter_name}")
        except Exception as e:
            print(f"❌ Could not extract submitter name: {e}")
            # Consider taking a screenshot for debugging if errors occur
            # page.screenshot(path="error_screenshot_name.png")

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


        # --- Print Extracted Information ---
        print("\n--- Extracted Information ---")
        print(f"Submitter: {submitter_name}")
        print(f"Number of Pages: {page_count}")
        print("---------------------------\n")
    return submitter_name, page_count


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

submitter_name, page_count = get_PDF()
trim_pdf("submission_pdfs/graded_submission.pdf", "trimmed_pdfs/trimmed_submission.pdf", page_count)