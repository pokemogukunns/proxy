import subprocess
from flask import Flask, request, render_template_string

app = Flask(__name__)

# /home エンドポイント (URL入力フォーム)
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

# /proxy エンドポイント (HTML取得・実行)
@app.route("/proxy", methods=["GET"])
def proxy():
    # URLパラメータを取得
    target_url = request.args.get("url")
    if not target_url:
        return "<h1>エラー: URLパラメータが必要です。</h1>", 400

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        return "<h1>エラー: URLはhttp://またはhttps://で始まる必要があります。</h1>", 400

    try:
        # curlコマンドでHTMLを取得
        curl_command = f"curl -s {target_url}"
        result = subprocess.run(curl_command, shell=True, text=True, capture_output=True)

        if result.returncode != 0:
            return f"<h1>エラー: curlコマンドでエラーが発生しました。</h1><p>{result.stderr}</p>", 500

        html = result.stdout

        # 取得したHTMLを直接返す
        return html

    except Exception as e:
        return f"<h1>サーバー側でエラーが発生しました。</h1><p>{str(e)}</p>", 500

if __name__ == "__main__":
    app.run(debug=True)
