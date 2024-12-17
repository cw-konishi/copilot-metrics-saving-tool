-- データベースが存在しない場合のみ作成
DO $$ 
BEGIN
   IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'metrics_db') THEN
      PERFORM dblink_exec('dbname=postgres', 'CREATE DATABASE metrics_db');
   END IF;
END
$$;

\c metrics_db;

-- テーブルが存在しない場合のみ作成
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    date DATE,
    total_active_users INT,
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_code_completions (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES metrics(id),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_code_completions_languages (
    id SERIAL PRIMARY KEY,
    completion_id INT REFERENCES copilot_ide_code_completions(id),
    name VARCHAR(50),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_code_completions_editors (
    id SERIAL PRIMARY KEY,
    completion_id INT REFERENCES copilot_ide_code_completions(id),
    name VARCHAR(50),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_code_completions_models (
    id SERIAL PRIMARY KEY,
    editor_id INT REFERENCES copilot_ide_code_completions_editors(id),
    name VARCHAR(50),
    is_custom_model BOOLEAN,
    custom_model_training_date DATE,
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_code_completions_model_languages (
    id SERIAL PRIMARY KEY,
    model_id INT REFERENCES copilot_ide_code_completions_models(id),
    name VARCHAR(50),
    total_engaged_users INT,
    total_code_suggestions INT,
    total_code_acceptances INT,
    total_code_lines_suggested INT,
    total_code_lines_accepted INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_chat (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES metrics(id),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_chat_editors (
    id SERIAL PRIMARY KEY,
    chat_id INT REFERENCES copilot_ide_chat(id),
    name VARCHAR(50),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_ide_chat_models (
    id SERIAL PRIMARY KEY,
    editor_id INT REFERENCES copilot_ide_chat_editors(id),
    name VARCHAR(50),
    is_custom_model BOOLEAN,
    custom_model_training_date DATE,
    total_engaged_users INT,
    total_chats INT,
    total_chat_insertion_events INT,
    total_chat_copy_events INT
);

CREATE TABLE IF NOT EXISTS copilot_dotcom_chat (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES metrics(id),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_dotcom_chat_models (
    id SERIAL PRIMARY KEY,
    chat_id INT REFERENCES copilot_dotcom_chat(id),
    name VARCHAR(50),
    is_custom_model BOOLEAN,
    custom_model_training_date DATE,
    total_engaged_users INT,
    total_chats INT
);

CREATE TABLE IF NOT EXISTS copilot_dotcom_pull_requests (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES metrics(id),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_dotcom_pull_requests_repositories (
    id SERIAL PRIMARY KEY,
    pull_request_id INT REFERENCES copilot_dotcom_pull_requests(id),
    name VARCHAR(100),
    total_engaged_users INT
);

CREATE TABLE IF NOT EXISTS copilot_dotcom_pull_requests_models (
    id SERIAL PRIMARY KEY,
    repository_id INT REFERENCES copilot_dotcom_pull_requests_repositories(id),
    name VARCHAR(50),
    is_custom_model BOOLEAN,
    custom_model_training_date DATE,
    total_pr_summaries_created INT,
    total_engaged_users INT
);