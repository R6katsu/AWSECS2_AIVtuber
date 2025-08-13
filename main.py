import os
import time
import datetime as dt
import tempfile
import subprocess
from typing import List

import requests
from gtts import gTTS

from openai import OpenAI

# NewsAPI のエンドポイント
NEWS_API_ENDPOINT = "https://newsapi.org/v2/everything"
# 読み上げる記事の件数
ARTICLES_TO_READ = 5
# 配信を続ける最大時間（秒）
STREAM_DURATION_SECONDS = 60 * 60  # 1 hour

# 前日の世界ニュースを NewsAPI から取得する
def fetch_yesterdays_world_news(api_key: str) -> List[dict]:
    """Fetch top world news articles from the previous day."""
    today = dt.date.today()
    yesterday = today - dt.timedelta(days=1)
    params = {
        "q": "world",
        "from": yesterday.isoformat(),
        "to": yesterday.isoformat(),
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": ARTICLES_TO_READ,
        "apiKey": api_key,
    }
    resp = requests.get(NEWS_API_ENDPOINT, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("articles", [])

# ChatGPT を利用して記事を要約し日本語に翻訳する
def summarize_and_translate(client: OpenAI, title: str, content: str) -> str:
    """Use ChatGPT to summarize and translate the article into Japanese."""
    prompt = (
        f"記事タイトル: {title}\n"
        f"内容: {content}\n\n"
        "上記の記事を日本語で200文字程度に要約し、ラジオ風に丁寧に紹介してください。"
    )
    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt,
    )
    return response.output[0].content[0].text

# 要約したテキストを音声ファイルに変換する
def text_to_speech(text: str, outfile: str) -> None:
    """Convert text to speech using gTTS."""
    tts = gTTS(text, lang="ja")
    tts.save(outfile)

# 生成した音声ファイルを YouTube の RTMP に送信する
def stream_audio(file_path: str, rtmp_url: str) -> None:
    """Stream an audio file to a YouTube RTMP endpoint using ffmpeg."""
    cmd = [
        "ffmpeg",
        "-re",
        "-i",
        file_path,
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-f",
        "flv",
        rtmp_url,
    ]
    subprocess.run(cmd, check=True)

# 全体の処理を統括するメイン関数
def run_broadcast() -> None:
    """Main logic for the daily broadcast."""
    openai_key = os.getenv("OPENAI_API_KEY")
    news_api_key = os.getenv("NEWSAPI_KEY")
    rtmp_url = os.getenv("YOUTUBE_RTMP_URL")
    if not all([openai_key, news_api_key, rtmp_url]):
        # 必要な環境変数が設定されていない場合はエラー
        raise ValueError("Required environment variables are missing.")

    client = OpenAI(api_key=openai_key)
    articles = fetch_yesterdays_world_news(news_api_key)

    start_time = time.time()
    for article in articles[:ARTICLES_TO_READ]:
        if time.time() - start_time > STREAM_DURATION_SECONDS:
            # 配信開始から 1 時間経過したら終了
            break
        text = summarize_and_translate(client, article.get("title", ""), article.get("content", ""))
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            text_to_speech(text, tmp.name)
            tmp.flush()
            stream_audio(tmp.name, rtmp_url)
            os.unlink(tmp.name)  # 一時ファイルを削除


if __name__ == "__main__":
    run_broadcast()
