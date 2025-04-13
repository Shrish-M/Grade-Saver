from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import webScrape  # Rename your script file to `your_heavy_script.py` (without running anything at top-level)

app = Flask(__name__)
CORS(app)

@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    print("✅ Received request to /run-scraper")
    data = request.json
    stored_url = data.get("url")
    # threading.Thread(target=webScrape.run_main, args=(stored_url,)).start()
    result, regrade_request = webScrape.run_main(stored_url)  # Make this return rubric_by_question

    return jsonify({
        "status": "success",
        "rubrics": result,  # Dictionary expected by the extension
        "regrade-request": regrade_request
    })
    # return jsonify({"status": "started"})

if __name__ == '__main__':
    app.run(port=5001)
