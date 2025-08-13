# AI Vtuber on AWS EC2

This project provides a simple AI-powered Vtuber that streams a daily news digest to YouTube Live.  
Every morning at **7:00 JST** the bot fetches world news from the previous day, summarizes and translates each article into Japanese using OpenAI's ChatGPT API and narrates the summaries in a radio style. The broadcast finishes after five articles or one hour, whichever comes first.

## Components

- `main.py` – logic for fetching articles, generating narration, and streaming audio to YouTube.
- `scheduler.py` – APScheduler setup that triggers the broadcast every day at 07:00 Asia/Tokyo time.
- `requirements.txt` – Python dependencies.

## Environment Variables

The following variables must be configured (e.g. in `.env`).

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | API key for the OpenAI ChatGPT API |
| `NEWSAPI_KEY` | API key for [NewsAPI](https://newsapi.org/) |
| `YOUTUBE_RTMP_URL` | RTMP endpoint including the stream key for your YouTube Live broadcast |

## Running on EC2

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Export the environment variables above or place them in a `.env` file and `source` it.
3. To start the scheduler service:
   ```bash
   python scheduler.py
   ```

For production, register `scheduler.py` with `systemd` or a process manager so that it keeps running. The scheduler will automatically trigger the broadcast daily.

## Notes

- `gTTS` is used for text-to-speech and requires network access to Google's TTS service.
- Streaming relies on `ffmpeg` being installed on the EC2 instance.
- The project is a minimal example and may need further work (e.g., error handling, richer visuals) for a full-featured Vtuber.
