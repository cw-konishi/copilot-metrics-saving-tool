# Copilot Metrics Saving Tool

このプロジェクトは、GitHub Copilot Metrics APIからデータを取得し、データベースに保存し、PrometheusとGrafanaを使用して可視化するツールです。

Copilot metrics APIの最新GAエンドポイント「metrics」に対応しています。

## 必要な環境

- Docker
- Docker Compose

## セットアップ

### 1. リポジトリをクローンします

```sh
git clone https://github.com/yourusername/copilot-metrics-saving-tool.git
cd copilot-metrics-saving-tool
```

### 2. Organization情報を設定します

backend/config.yamlファイルを編集し、以下の内容を追加します。

```yml
github:
  org: "your_org_name"
  token: "your_github_token"
```

### 3. サービスを起動します

```sh
docker-compose up -d
```

### 4. 動作確認

#### Grafanaダッシュボード

http://YOURHOST:3000

ID/PW:admin/admin

#### Prometheus

http://YOURHOST:9090

#### APIエンドポイントアクセス

http://YOURHOST:5000

##### エンドポイント一覧

###### /fetch_now

即座にGitHub Copilot metrics APIを叩いてデータを取得し、データベースに保存します。

###### /metrics

データベースに保存されているメトリクスデータをJSON形式で返します。クエリパラメータとしてsinceとuntilを指定できます。

###### /prometheus_metrics

Prometheus形式のメトリクスデータを返します。

###### /upload_metrics

過去のJSONデータを手動でアップロードしてデータベースに登録します。GETリクエストでフォームを表示し、POSTリクエストでデータをアップロードします。

## その他

コンテナが起動したら、以下のコマンドでバックエンドのコンテナにアクセスできます。

```sh
docker exec -it backend /bin/bash
```
