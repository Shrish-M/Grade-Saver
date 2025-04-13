from flask import Flask, jsonify
import threading
import webScrape  # Rename your script file to `your_heavy_script.py` (without running anything at top-level)

app = Flask(__name__)

@app.route('/run-scraper', methods=['GET'])
def run_scraper():
    threading.Thread(target=your_heavy_script.run_main).start()
    return jsonify({"status": "started"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
