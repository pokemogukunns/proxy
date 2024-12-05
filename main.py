import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
import subprocess
from io import BytesIO

def fetch_html_and_images():
    url = url_entry.get()
    if not url.startswith("http://") and not url.startswith("https://"):
        output_text.insert(tk.END, "URLはhttp://またはhttps://で始まる必要があります。\n")
        return
    try:
        # cURLコマンドでHTMLを取得
        curl_command = f"curl -s {url}"
        result = subprocess.run(curl_command, shell=True, text=True, capture_output=True)
        if result.returncode != 0:
            output_text.insert(tk.END, f"エラー: {result.stderr}\n")
            return

        html = result.stdout
        output_text.delete("1.0", tk.END)  # テキストボックスをクリア
        output_text.insert(tk.END, html)

        # HTML解析して画像URLを抽出
        soup = BeautifulSoup(html, "html.parser")
        img_tags = soup.find_all("img")
        img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]

        # 最初の画像を表示
        if img_urls:
            img_url = img_urls[0]
            if not img_url.startswith("http"):
                img_url = url + img_url  # 相対URLを処理

            response = requests.get(img_url)
            image_data = BytesIO(response.content)
            img = Image.open(image_data)
            img.thumbnail((300, 300))  # サイズ調整
            photo = ImageTk.PhotoImage(img)

            image_label.config(image=photo)
            image_label.image = photo
        else:
            output_text.insert(tk.END, "\n画像が見つかりませんでした。\n")
            image_label.config(image=None)
            image_label.image = None

    except Exception as e:
        output_text.insert(tk.END, f"エラーが発生しました: {e}\n")

# GUIの作成
root = tk.Tk()
root.title("HTML & Image Fetcher")

# URL入力用のテキストボックス
url_label = tk.Label(root, text="URLを入力してください:")
url_label.pack(pady=5)

url_entry = tk.Entry(root, width=50)
url_entry.pack(pady=5)

# 実行ボタン
fetch_button = tk.Button(root, text="HTMLと画像を取得", command=fetch_html_and_images)
fetch_button.pack(pady=5)

# 結果表示用のスクロール可能なテキストボックス
output_text = scrolledtext.ScrolledText(root, width=80, height=20)
output_text.pack(pady=10)

# 画像表示用のラベル
image_label = tk.Label(root)
image_label.pack(pady=10)

# メインループ
root.mainloop()
