from flask import Flask, jsonify, request
from app.scheduler import start_scheduler
from app.metrics_fetcher import fetch_metrics
from app.database import save_metrics, get_all_metrics

app = Flask(__name__)

@app.route('/')
def index():
    return "Metrics fetching service is running!"

@app.route('/fetch_now')
def fetch_now():
    metrics = fetch_metrics()
    save_metrics(metrics)
    return "Metrics fetched and saved successfully!"

@app.route('/metrics')
def metrics():
    since = request.args.get('since')
    until = request.args.get('until')
    metrics_data = get_all_metrics(since, until)
    return jsonify(metrics_data)

@app.route('/upload_metrics', methods=['GET', 'POST'])
def upload_metrics():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({"error": "Invalid input"}), 400
        metrics = request.get_json()
        save_metrics_from_json(metrics)
        return "Metrics uploaded and saved successfully!"
    else:
        return render_template_string(upload_form)

upload_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Upload Metrics</title>
</head>
<body>
    <h1>Upload Metrics</h1>
    <form action="/upload_metrics" method="post" enctype="application/json">
        <label for="metrics">Metrics JSON:</label><br>
        <textarea id="metrics" name="metrics" rows="20" cols="100"></textarea><br><br>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    start_scheduler()
    app.run(host='0.0.0.0', port=5000)