from flask import Flask, jsonify, request, render_template_string, Response
from app.scheduler import start_scheduler
from app.metrics_fetcher import fetch_metrics
from app.database import save_metrics, get_all_metrics
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Metrics fetching service is running!"

@app.route('/fetch_now')
def fetch_now():
    metrics = fetch_metrics()
    if "error" in metrics:
        return jsonify(metrics), 500  # エラーメッセージを含むレスポンスを返す
    save_metrics(metrics)
    return jsonify(metrics)

@app.route('/metrics')
def metrics():
    since = request.args.get('since')
    until = request.args.get('until')
    metrics_data = get_all_metrics(since, until)
    return jsonify(metrics_data)

@app.route('/upload_metrics', methods=['GET', 'POST'])
def upload_metrics():
    if request.method == 'POST':
        if request.is_json:
            metrics = request.get_json()
        else:
            metrics = request.form.get('metrics')
            if metrics:
                metrics = json.loads(metrics)
            else:
                return jsonify({"error": "Invalid input"}), 400
        save_metrics(metrics)
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
    <form action="/upload_metrics" method="post" enctype="multipart/form-data">
        <label for="metrics">Metrics JSON:</label><br>
        <textarea id="metrics" name="metrics" rows="20" cols="100"></textarea><br><br>
        <input type="submit" value="Upload">
    </form>
</body>
</html>
"""
@app.route('/prometheus_metrics')
def prometheus_metrics():
    metrics_data = get_all_metrics(None, None)
    prometheus_format = convert_to_prometheus_format(metrics_data)
    return Response(prometheus_format, mimetype='text/plain')

def convert_to_prometheus_format(metrics_data):
    lines = []
    for metric in metrics_data:
        date = metric['date']
        total_active_users = metric['total_active_users']
        total_engaged_users = metric['total_engaged_users']
        lines.append(f'total_active_users{{date="{date}"}} {total_active_users}')
        lines.append(f'total_engaged_users{{date="{date}"}} {total_engaged_users}')
        
        # Copilot IDE Code Completions
        for editor in metric['copilot_ide_code_completions']['editors']:
            editor_name = editor['name']
            for model in editor['models']:
                model_name = model['name']
                for language in model['languages']:
                    language_name = language['name']
                    total_code_suggestions = language['total_code_suggestions']
                    total_code_acceptances = language['total_code_acceptances']
                    lines.append(f'total_code_suggestions{{date="{date}", editor="{editor_name}", model="{model_name}", language="{language_name}"}} {total_code_suggestions}')
                    lines.append(f'total_code_acceptances{{date="{date}", editor="{editor_name}", model="{model_name}", language="{language_name}"}} {total_code_acceptances}')
        
        # Copilot IDE Chat
        for editor in metric['copilot_ide_chat']['editors']:
            editor_name = editor['name']
            for model in editor['models']:
                model_name = model['name']
                total_chats = model['total_chats']
                total_chat_insertion_events = model['total_chat_insertion_events']
                total_chat_copy_events = model['total_chat_copy_events']
                lines.append(f'total_chats{{date="{date}", editor="{editor_name}", model="{model_name}"}} {total_chats}')
                lines.append(f'total_chat_insertion_events{{date="{date}", editor="{editor_name}", model="{model_name}"}} {total_chat_insertion_events}')
                lines.append(f'total_chat_copy_events{{date="{date}", editor="{editor_name}", model="{model_name}"}} {total_chat_copy_events}')
        
        # Copilot Dotcom Chat
        for model in metric['copilot_dotcom_chat']['models']:
            model_name = model['name']
            total_chats = model['total_chats']
            lines.append(f'total_dotcom_chats{{date="{date}", model="{model_name}"}} {total_chats}')
        
        # Copilot Dotcom Pull Requests
        for repo in metric['copilot_dotcom_pull_requests']['repositories']:
            repo_name = repo['name']
            for model in repo['models']:
                model_name = model['name']
                total_pr_summaries_created = model['total_pr_summaries_created']
                lines.append(f'total_pr_summaries_created{{date="{date}", repo="{repo_name}", model="{model_name}"}} {total_pr_summaries_created}')
    
    return "\n".join(lines)

if __name__ == '__main__':
    start_scheduler()
    app.run(host='0.0.0.0', port=5000)