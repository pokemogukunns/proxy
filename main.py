import subprocess
from flask import Flask, request, jsonify, render_template_string

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

# /proxy エンドポイント (HTML取得API)
@app.route("/proxy", methods=["GET"])
def proxy():
    # URLパラメータを取得
    target_url = request.args.get("url")
    if not target_url:
        return jsonify({"error": "URLパラメータが必要です"}), 400

    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        return jsonify({"error": "URLはhttp://またはhttps://で始まる必要があります"}), 400

    try:
        # curlコマンドでHTMLを取得
        curl_command = f"curl -s {target_url}"
        result = subprocess.run(curl_command, shell=True, text=True, capture_output=True)

        if result.returncode != 0:
            return jsonify({"error": "curlコマンドでエラーが発生しました", "details": result.stderr}), 500

        html = result.stdout
        return jsonify({"html": html})

    except Exception as e:
        return jsonify({"error": "サーバー側でエラーが発生しました", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
