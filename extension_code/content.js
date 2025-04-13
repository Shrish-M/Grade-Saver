// Store regrade text when we receive it from popup
let regradeTextStore = {};

// Listen for messages from the popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "openQuestion") {
    const questionNumber = request.question;
    const regradeText = request.regradeText || "";
    
    // Store the regrade text for this question
    if (regradeText) {
      regradeTextStore[questionNumber] = regradeText;
    }
    
    console.log(`Attempting to expand Q${questionNumber} and request regrade`);
    
    // First find the question on the page
    const questionElements = findQuestionElements(questionNumber);
    
    if (questionElements.length > 0) {
      console.log(`Found ${questionElements.length} elements for Question ${questionNumber}`);
      
      // Expand the question if needed
      expandQuestion(questionElements);
      
      // After expanding, look for regrade button and click it
      setTimeout(() => {
        clickRegradeButton(questionNumber);
        
        // After clicking regrade button, wait for the regrade form to appear
        setTimeout(() => {
          fillRegradeForm(questionNumber);
        }, 1000); // Wait a second for the form to open
      }, 500); // Wait for expansion to complete
      
      sendResponse({
        success: true,
        message: `Found Question ${questionNumber} and attempting to open regrade request`
      });
    } else {
      console.log(`Could not find Question ${questionNumber}`);
      sendResponse({
        success: false,
        message: `Could not find Question ${questionNumber} on the page`
      });
    }
    
    return true; // Keep message channel open for async response
  }
});

// Find elements related to the specific question
function findQuestionElements(questionNumber) {
  const result = [];
  
  // Look for various element types that might contain question info
  const allElements = [
    ...document.querySelectorAll('h2, h3, h4, div, li, section, button'),
  ];
  
  for (const element of allElements) {
    // Match various formats - "Question X", "Q X", "Question Number X"
    if (element.textContent.match(new RegExp(`(Question|Q)\\s*${questionNumber}\\b`, 'i'))) {
      result.push(element);
    }
  }
  
  return result;
}

// Try to expand the question by clicking appropriate elements
function expandQuestion(elements) {
  for (const element of elements) {
    // Try to find expandable elements
    const expandables = findExpandableElements(element);
    
    if (expandables.length > 0) {
      console.log(`Found ${expandables.length} expandable elements`);
      expandables.forEach(el => {
        console.log('Clicking to expand:', el);
        el.click();
      });
    } else {
      // If no obvious expandable elements, try clicking the element itself
      element.click();
    }
    
    // Scroll to the element
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}

// Find elements that can be clicked to expand the question
function findExpandableElements(baseElement) {
  const result = [];
  
  // Try to find the closest question container
  const container = baseElement.closest('.question, .question-container') || 
                    baseElement.parentElement;
  
  if (!container) return result;
  
  // Look for clickable elements
  const clickables = container.querySelectorAll('a, button, .expander, .show-hide');
  clickables.forEach(el => {
    if (el.textContent.match(/show|expand|view|toggle|open|no title/i)) {
      result.push(el);
    }
  });
  
  // If nothing specific found, add any links or buttons
  if (result.length === 0) {
    container.querySelectorAll('a, button').forEach(el => result.push(el));
  }
  
  return result;
}

// Find and click the regrade request button
function clickRegradeButton(questionNumber) {
  console.log("Looking for regrade button...");
  
  // Look for regrade buttons with different approaches
  
  // Approach 1: Direct button with "Request Regrade" text
  const regradeButtons = Array.from(document.querySelectorAll('button, a')).filter(el => {
    return el.textContent.match(/request(\s+a)?\s+regrade/i);
  });
  
  // Approach 2: Button specific to this question
  const questionSpecificButtons = regradeButtons.filter(button => {
    return button.textContent.includes(`Question ${questionNumber}`) || 
           button.textContent.includes(`Q${questionNumber}`);
  });
  
  // Approach 3: If we're already on a specific question page, any regrade button
  const anyRegradeButton = document.querySelector('.regrade-button, button[aria-label*="regrade"], a[aria-label*="regrade"]');
  
  // Approach 4: Button with class or attribute containing regrade
  const classButtons = document.querySelectorAll('[class*="regrade"], [id*="regrade"], [data-qa*="regrade"]');
  
  // Approach 5: Button with specific styles similar to the ones in the screenshot
  const styledButtons = document.querySelectorAll('.tiiBtn.tiiBtn-secondary');
  
  // Try clicking the most specific button first
  if (questionSpecificButtons.length > 0) {
    console.log("Found question-specific regrade button");
    questionSpecificButtons[0].click();
    return true;
  } else if (regradeButtons.length > 0) {
    console.log("Found general regrade button");
    regradeButtons[0].click();
    return true;
  } else if (anyRegradeButton) {
    console.log("Found regrade button by role/label");
    anyRegradeButton.click();
    return true;
  } else if (classButtons.length > 0) {
    console.log("Found regrade button by class/id");
    classButtons[0].click();
    return true;
  } else if (styledButtons.length > 0) {
    console.log("Found styled button that might be regrade");
    // Look for buttons that have regrade-related text
    for (const btn of styledButtons) {
      if (btn.textContent.toLowerCase().includes('regrade') || 
          btn.getAttribute('label')?.toLowerCase().includes('regrade') ||
          btn.getAttribute('aria-label')?.toLowerCase().includes('regrade')) {
        console.log("Clicking styled regrade button:", btn.textContent);
        btn.click();
        return true;
      }
    }
  }
  
  console.log("No regrade button found");
  return false;
}

// Fill the regrade form with the stored text
function fillRegradeForm(questionNumber) {
  console.log("Looking for regrade form to fill...");
  const regradeText = regradeTextStore[questionNumber] || "";
  
  if (!regradeText) {
    console.log("No regrade text found for this question");
    return;
  }
  
  // Various selectors to find the textarea
  const textareaSelectors = [
    'textarea.form--textArea',
    'textarea[aria-label*="regrade"]',
    'textarea.mathForm--input',
    'textarea',
    '[role="textbox"]',
    '[contenteditable="true"]'
  ];
  
  // Try each selector
  for (const selector of textareaSelectors) {
    const textareas = document.querySelectorAll(selector);
    console.log(`Found ${textareas.length} textareas with selector: ${selector}`);
    
    if (textareas.length > 0) {
      // Try to find the visible one or the one in a dialog
      let targetTextarea = Array.from(textareas).find(ta => {
        const style = window.getComputedStyle(ta);
        return style.display !== 'none' && style.visibility !== 'hidden';
      });
      
      // If no visible textarea found, just use the first one
      if (!targetTextarea && textareas.length > 0) {
        targetTextarea = textareas[0];
      }
      
      if (targetTextarea) {
        console.log("Found textarea, filling with regrade text");
        
        // Set the value
        targetTextarea.value = regradeText;
        
        // Dispatch events to ensure Gradescope's JavaScript detects the change
        targetTextarea.dispatchEvent(new Event('input', { bubbles: true }));
        targetTextarea.dispatchEvent(new Event('change', { bubbles: true }));
        
        // Focus and select the textarea
        targetTextarea.focus();
        
        console.log("Successfully filled regrade form");
        return true;
      }
    }
  }
  
  console.log("Could not find a textarea to fill");
  return false;
}

// Log that content script has loaded properly
console.log('Gradescope Regrade Helper content script loaded');
