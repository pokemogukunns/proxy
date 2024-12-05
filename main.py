import os
import requests
import shutil
from flask import Flask, request, send_file, Response, render_template_string
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

app = Flask(__name__)

# 一時ディレクトリの作成
TEMP_DIR = "./tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@app.route("/home", methods=["GET"])
def home():
    html_form = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Proxy Input</title>
    </head>
    <body>
      <h1>URLを入力してください</h1>
      <form action="/proxy" method="get">
        <label for="url">URL:</label>
        <input type="text" id="url" name="url" placeholder="https://example.com" required>
        <button type="submit">送信</button>
      </form>
    </body>
    </html>
    """
    return render_template_string(html_form)

@app.route("/proxy", methods=["GET"])
def proxy():
    target_url = request.args.get("url")
    if not target_url:
        return "<h1>エラー: URLパラメータが必要です。</h1>", 400

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        return "<h1>エラー: URLはhttp://またはhttps://で始まる必要があります。</h1>", 400

    try:
        # リソースの取得
        response = requests.get(target_url, stream=True)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if "text/html" in content_type:  # HTMLの場合
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # リソースのダウンロードとパス修正
            for tag in soup.find_all(["img", "link", "script"]):
                attr = "href" if tag.name in ["link"] else "src"
                if tag.has_attr(attr):
                    resource_url = urljoin(target_url, tag[attr])
                    resource_path = download_resource(resource_url)
                    if resource_path:
                        tag[attr] = f"/static/{resource_path}"

            return str(soup)

        else:  # バイナリリソースの場合
            filename = os.path.basename(urlparse(target_url).path)
            if not filename:
                filename = "downloaded_file"

            file_path = os.path.join(TEMP_DIR, filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)

            return send_file(file_path, mimetype=content_type)

    except Exception as e:
        return f"<h1>エラーが発生しました。</h1><p>{str(e)}</p>", 500

def download_resource(url):
    """指定されたURLのリソースをダウンロードし、一時ディレクトリに保存する"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # ファイル名を決定
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = "index.html"

        # ファイルパスを設定
        file_path = os.path.join(TEMP_DIR, filename)

        # バイナリデータを保存
        with open(file_path, "wb") as f:
            shutil.copyfileobj(response.raw, f)

        return f"tmp/{filename}"

    except Exception as e:
        print(f"リソースのダウンロードに失敗しました: {e}")
        return None

@app.route("/static/tmp/<path:filename>", methods=["GET"])
def serve_tmp_file(filename):
    """一時ディレクトリ内のファイルを提供"""
    return send_file(os.path.join(TEMP_DIR, filename))

if __name__ == "__main__":
    app.run(debug=True)
