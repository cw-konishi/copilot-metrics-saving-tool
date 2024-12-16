import psycopg2
from datetime import datetime

def save_metrics(metrics):
    conn = psycopg2.connect(
        dbname='metrics_db',
        user='user',
        password='password',
        host='db'
    )
    cursor = conn.cursor()
    for metric in metrics:
        # Check if the metric for the given date already exists
        cursor.execute(
            "SELECT id FROM metrics WHERE date = %s",
            (metric['date'],)
        )
        existing_metric = cursor.fetchone()
        if existing_metric:
            print(f"Metric for date {metric['date']} already exists. Skipping insertion.")
            continue

        cursor.execute(
            "INSERT INTO metrics (date, total_active_users, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
            (metric['date'], metric['total_active_users'], metric['total_engaged_users'])
        )
        metric_id = cursor.fetchone()[0]

        # Insert copilot_ide_code_completions
        completions = metric['copilot_ide_code_completions']
        cursor.execute(
            "INSERT INTO copilot_ide_code_completions (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, completions['total_engaged_users'])
        )
        completion_id = cursor.fetchone()[0]

        # Insert copilot_ide_code_completions_languages
        for language in completions['languages']:
            cursor.execute(
                "INSERT INTO copilot_ide_code_completions_languages (completion_id, name, total_engaged_users) VALUES (%s, %s, %s)",
                (completion_id, language['name'], language['total_engaged_users'])
            )

        # Insert copilot_ide_code_completions_editors and models
        for editor in completions['editors']:
            cursor.execute(
                "INSERT INTO copilot_ide_code_completions_editors (completion_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (completion_id, editor['name'], editor['total_engaged_users'])
            )
            editor_id = cursor.fetchone()[0]

            for model in editor['models']:
                total_engaged_users = model.get('total_engaged_users', 0)
                custom_model_training_date = model.get('custom_model_training_date', None)
                cursor.execute(
                    "INSERT INTO copilot_ide_code_completions_models (editor_id, name, is_custom_model, custom_model_training_date, total_engaged_users) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (editor_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], total_engaged_users)
                )
                model_id = cursor.fetchone()[0]

                for language in model['languages']:
                    cursor.execute(
                        "INSERT INTO copilot_ide_code_completions_model_languages (model_id, name, total_engaged_users, total_code_suggestions, total_code_acceptances, total_code_lines_suggested, total_code_lines_accepted) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (model_id, language['name'], language['total_engaged_users'], language['total_code_suggestions'], language['total_code_acceptances'], language['total_code_lines_suggested'], language['total_code_lines_accepted'])
                    )

        # Insert copilot_ide_chat
        chat = metric['copilot_ide_chat']
        cursor.execute(
            "INSERT INTO copilot_ide_chat (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, chat['total_engaged_users'])
        )
        chat_id = cursor.fetchone()[0]

        # Insert copilot_ide_chat_editors and models
        for editor in chat['editors']:
            cursor.execute(
                "INSERT INTO copilot_ide_chat_editors (chat_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (chat_id, editor['name'], editor['total_engaged_users'])
            )
            editor_id = cursor.fetchone()[0]

            for model in editor['models']:
                cursor.execute(
                    "INSERT INTO copilot_ide_chat_models (editor_id, name, is_custom_model, custom_model_training_date, total_engaged_users, total_chats, total_chat_insertion_events, total_chat_copy_events) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (editor_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_engaged_users'], model['total_chats'], model['total_chat_insertion_events'], model['total_chat_copy_events'])
                )

        # Insert copilot_dotcom_chat
        dotcom_chat = metric['copilot_dotcom_chat']
        cursor.execute(
            "INSERT INTO copilot_dotcom_chat (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, dotcom_chat['total_engaged_users'])
        )
        dotcom_chat_id = cursor.fetchone()[0]

        # Insert copilot_dotcom_chat_models
        for model in dotcom_chat['models']:
            cursor.execute(
                "INSERT INTO copilot_dotcom_chat_models (chat_id, name, is_custom_model, custom_model_training_date, total_engaged_users, total_chats) VALUES (%s, %s, %s, %s, %s, %s)",
                (dotcom_chat_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_engaged_users'], model['total_chats'])
            )

        # Insert copilot_dotcom_pull_requests
        pull_requests = metric['copilot_dotcom_pull_requests']
        cursor.execute(
            "INSERT INTO copilot_dotcom_pull_requests (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, pull_requests['total_engaged_users'])
        )
        pull_request_id = cursor.fetchone()[0]

        # Insert copilot_dotcom_pull_requests_repositories and models
        for repository in pull_requests['repositories']:
            cursor.execute(
                "INSERT INTO copilot_dotcom_pull_requests_repositories (pull_request_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (pull_request_id, repository['name'], repository['total_engaged_users'])
            )
            repository_id = cursor.fetchone()[0]

            for model in repository['models']:
                cursor.execute(
                    "INSERT INTO copilot_dotcom_pull_requests_models (repository_id, name, is_custom_model, custom_model_training_date, total_pr_summaries_created, total_engaged_users) VALUES (%s, %s, %s, %s, %s, %s)",
                    (repository_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_pr_summaries_created'], model['total_engaged_users'])
                )

    conn.commit()
    cursor.close()
    conn.close()

def get_all_metrics(since=None, until=None):
    conn = psycopg2.connect(
        dbname='metrics_db',
        user='user',
        password='password',
        host='db'
    )
    cursor = conn.cursor()

    # Check if since and until are within the valid range
    valid_since = None
    valid_until = None

    if since:
        cursor.execute("SELECT MIN(date) FROM metrics")
        min_date = cursor.fetchone()[0]
        if min_date and since >= min_date:
            valid_since = since

    if until:
        cursor.execute("SELECT MAX(date) FROM metrics")
        max_date = cursor.fetchone()[0]
        if max_date and until <= max_date:
            valid_until = until

    query = "SELECT * FROM metrics WHERE 1=1"
    params = []
    if valid_since:
        query += " AND date >= %s"
        params.append(valid_since)
    if valid_until:
        query += " AND date <= %s"
        params.append(valid_until)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    metrics = []
    for row in rows:
        metric_id = row[0]
        metric = {
            'date':  row[1].strftime("%Y-%m-%d"),
            'total_active_users': row[2],
            'total_engaged_users': row[3],
            'copilot_ide_code_completions': {},
            'copilot_ide_chat': {},
            'copilot_dotcom_chat': {},
            'copilot_dotcom_pull_requests': {}
        }

        # Fetch copilot_ide_code_completions
        cursor.execute("SELECT * FROM copilot_ide_code_completions WHERE metric_id = %s", (metric_id,))
        completion = cursor.fetchone()
        if completion:
            completion_id = completion[0]
            metric['copilot_ide_code_completions'] = {
                'total_engaged_users': completion[2],
                'languages': [],
                'editors': []
            }

            # Fetch copilot_ide_code_completions_languages
            cursor.execute("SELECT * FROM copilot_ide_code_completions_languages WHERE completion_id = %s", (completion_id,))
            languages = cursor.fetchall()
            for language in languages:
                metric['copilot_ide_code_completions']['languages'].append({
                    'name': language[2],
                    'total_engaged_users': language[3]
                })

            # Fetch copilot_ide_code_completions_editors and models
            cursor.execute("SELECT * FROM copilot_ide_code_completions_editors WHERE completion_id = %s", (completion_id,))
            editors = cursor.fetchall()
            for editor in editors:
                editor_id = editor[0]
                editor_data = {
                    'name': editor[2],
                    'total_engaged_users': editor[3],
                    'models': []
                }

                cursor.execute("SELECT * FROM copilot_ide_code_completions_models WHERE editor_id = %s", (editor_id,))
                models = cursor.fetchall()
                for model in models:
                    model_id = model[0]
                    model_data = {
                        'name': model[2],
                        'is_custom_model': model[3],
                        'custom_model_training_date': model[4],
                        'total_engaged_users': model[5],
                        'languages': []
                    }

                    cursor.execute("SELECT * FROM copilot_ide_code_completions_model_languages WHERE model_id = %s", (model_id,))
                    model_languages = cursor.fetchall()
                    for model_language in model_languages:
                        model_data['languages'].append({
                            'name': model_language[2],
                            'total_engaged_users': model_language[3],
                            'total_code_suggestions': model_language[4],
                            'total_code_acceptances': model_language[5],
                            'total_code_lines_suggested': model_language[6],
                            'total_code_lines_accepted': model_language[7]
                        })

                    editor_data['models'].append(model_data)

                metric['copilot_ide_code_completions']['editors'].append(editor_data)

        # Fetch copilot_ide_chat
        cursor.execute("SELECT * FROM copilot_ide_chat WHERE metric_id = %s", (metric_id,))
        chat = cursor.fetchone()
        if (chat):
            chat_id = chat[0]
            metric['copilot_ide_chat'] = {
                'total_engaged_users': chat[2],
                'editors': []
            }

            cursor.execute("SELECT * FROM copilot_ide_chat_editors WHERE chat_id = %s", (chat_id,))
            chat_editors = cursor.fetchall()
            for chat_editor in chat_editors:
                chat_editor_id = chat_editor[0]
                chat_editor_data = {
                    'name': chat_editor[2],
                    'total_engaged_users': chat_editor[3],
                    'models': []
                }

                cursor.execute("SELECT * FROM copilot_ide_chat_models WHERE editor_id = %s", (chat_editor_id,))
                chat_models = cursor.fetchall()
                for chat_model in chat_models:
                    chat_editor_data['models'].append({
                        'name': chat_model[2],
                        'is_custom_model': chat_model[3],
                        'custom_model_training_date': chat_model[4],
                        'total_engaged_users': chat_model[5],
                        'total_chats': chat_model[6],
                        'total_chat_insertion_events': chat_model[7],
                        'total_chat_copy_events': chat_model[8]
                    })

                metric['copilot_ide_chat']['editors'].append(chat_editor_data)

        # Fetch copilot_dotcom_chat
        cursor.execute("SELECT * FROM copilot_dotcom_chat WHERE metric_id = %s", (metric_id,))
        dotcom_chat = cursor.fetchone()
        if dotcom_chat:
            dotcom_chat_id = dotcom_chat[0]
            metric['copilot_dotcom_chat'] = {
                'total_engaged_users': dotcom_chat[2],
                'models': []
            }

            cursor.execute("SELECT * FROM copilot_dotcom_chat_models WHERE chat_id = %s", (dotcom_chat_id,))
            dotcom_chat_models = cursor.fetchall()
            for dotcom_chat_model in dotcom_chat_models:
                metric['copilot_dotcom_chat']['models'].append({
                    'name': dotcom_chat_model[2],
                    'is_custom_model': dotcom_chat_model[3],
                    'custom_model_training_date': dotcom_chat_model[4],
                    'total_engaged_users': dotcom_chat_model[5],
                    'total_chats': dotcom_chat_model[6]
                })

        # Fetch copilot_dotcom_pull_requests
        cursor.execute("SELECT * FROM copilot_dotcom_pull_requests WHERE metric_id = %s", (metric_id,))
        pull_requests = cursor.fetchone()
        if pull_requests:
            pull_request_id = pull_requests[0]
            metric['copilot_dotcom_pull_requests'] = {
                'total_engaged_users': pull_requests[2],
                'repositories': []
            }

            cursor.execute("SELECT * FROM copilot_dotcom_pull_requests_repositories WHERE pull_request_id = %s", (pull_request_id,))
            repositories = cursor.fetchall()
            for repository in repositories:
                repository_id = repository[0]
                repository_data = {
                    'name': repository[2],
                    'total_engaged_users': repository[3],
                    'models': []
                }

                cursor.execute("SELECT * FROM copilot_dotcom_pull_requests_models WHERE repository_id = %s", (repository_id,))
                repository_models = cursor.fetchall()
                for repository_model in repository_models:
                    repository_data['models'].append({
                        'name': repository_model[2],
                        'is_custom_model': repository_model[3],
                        'custom_model_training_date': repository_model[4],
                        'total_pr_summaries_created': repository_model[5],
                        'total_engaged_users': repository_model[6]
                    })

                metric['copilot_dotcom_pull_requests']['repositories'].append(repository_data)

        metrics.append(metric)

    cursor.close()
    conn.close()
    return metrics

def save_metrics_from_json(metrics):
    conn = psycopg2.connect(
        dbname='metrics_db',
        user='user',
        password='password',
        host='db'
    )
    cursor = conn.cursor()
    for metric in metrics:
        cursor.execute(
            "INSERT INTO metrics (date, total_active_users, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
            (metric['date'], metric['total_active_users'], metric['total_engaged_users'])
        )
        metric_id = cursor.fetchone()[0]

        # Save copilot_ide_code_completions
        completions = metric['copilot_ide_code_completions']
        cursor.execute(
            "INSERT INTO copilot_ide_code_completions (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, completions['total_engaged_users'])
        )
        completion_id = cursor.fetchone()[0]

        # Save languages
        for language in completions['languages']:
            cursor.execute(
                "INSERT INTO copilot_ide_code_completions_languages (completion_id, name, total_engaged_users) VALUES (%s, %s, %s)",
                (completion_id, language['name'], language['total_engaged_users'])
            )

        # Save editors
        for editor in completions['editors']:
            cursor.execute(
                "INSERT INTO copilot_ide_code_completions_editors (completion_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (completion_id, editor['name'], editor['total_engaged_users'])
            )
            editor_id = cursor.fetchone()[0]

            # Save models
            for model in editor['models']:
                cursor.execute(
                    "INSERT INTO copilot_ide_code_completions_models (editor_id, name, is_custom_model, custom_model_training_date, total_engaged_users) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                    (editor_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_engaged_users'])
                )
                model_id = cursor.fetchone()[0]

                # Save model languages
                for language in model['languages']:
                    cursor.execute(
                        "INSERT INTO copilot_ide_code_completions_model_languages (model_id, name, total_engaged_users, total_code_suggestions, total_code_acceptances, total_code_lines_suggested, total_code_lines_accepted) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (model_id, language['name'], language['total_engaged_users'], language['total_code_suggestions'], language['total_code_acceptances'], language['total_code_lines_suggested'], language['total_code_lines_accepted'])
                    )

        # Save copilot_ide_chat
        chat = metric['copilot_ide_chat']
        cursor.execute(
            "INSERT INTO copilot_ide_chat (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, chat['total_engaged_users'])
        )
        chat_id = cursor.fetchone()[0]

        # Save chat editors
        for editor in chat['editors']:
            cursor.execute(
                "INSERT INTO copilot_ide_chat_editors (chat_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (chat_id, editor['name'], editor['total_engaged_users'])
            )
            editor_id = cursor.fetchone()[0]

            # Save chat models
            for model in editor['models']:
                cursor.execute(
                    "INSERT INTO copilot_ide_chat_models (editor_id, name, is_custom_model, custom_model_training_date, total_engaged_users, total_chats, total_chat_insertion_events, total_chat_copy_events) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (editor_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_engaged_users'], model['total_chats'], model['total_chat_insertion_events'], model['total_chat_copy_events'])
                )

        # Save copilot_dotcom_chat
        dotcom_chat = metric['copilot_dotcom_chat']
        cursor.execute(
            "INSERT INTO copilot_dotcom_chat (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, dotcom_chat['total_engaged_users'])
        )
        dotcom_chat_id = cursor.fetchone()[0]

        # Save dotcom chat models
        for model in dotcom_chat['models']:
            cursor.execute(
                "INSERT INTO copilot_dotcom_chat_models (chat_id, name, is_custom_model, custom_model_training_date, total_engaged_users, total_chats) VALUES (%s, %s, %s, %s, %s, %s)",
                (dotcom_chat_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_engaged_users'], model['total_chats'])
            )

        # Save copilot_dotcom_pull_requests
        pull_requests = metric['copilot_dotcom_pull_requests']
        cursor.execute(
            "INSERT INTO copilot_dotcom_pull_requests (metric_id, total_engaged_users) VALUES (%s, %s) RETURNING id",
            (metric_id, pull_requests['total_engaged_users'])
        )
        pull_request_id = cursor.fetchone()[0]

        # Save pull request repositories and models
        for repository in pull_requests['repositories']:
            cursor.execute(
                "INSERT INTO copilot_dotcom_pull_requests_repositories (pull_request_id, name, total_engaged_users) VALUES (%s, %s, %s) RETURNING id",
                (pull_request_id, repository['name'], repository['total_engaged_users'])
            )
            repository_id = cursor.fetchone()[0]

            for model in repository['models']:
                cursor.execute(
                    "INSERT INTO copilot_dotcom_pull_requests_models (repository_id, name, is_custom_model, custom_model_training_date, total_pr_summaries_created, total_engaged_users) VALUES (%s, %s, %s, %s, %s, %s)",
                    (repository_id, model['name'], model['is_custom_model'], model['custom_model_training_date'], model['total_pr_summaries_created'], model['total_engaged_users'])
                )

    conn.commit()
    cursor.close()
    conn.close()