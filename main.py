import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def proxy():
    # URLを取得
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
