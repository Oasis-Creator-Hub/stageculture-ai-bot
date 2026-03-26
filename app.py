import os
import hmac
import hashlib
import time
import re
import requests
from flask import Flask, request, jsonify
import anthropic

app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Track processed event IDs to avoid duplicates
processed_events = set()

# Fetch bot's own user ID at startup so we can filter our own messages
def get_bot_user_id():
    resp = requests.post(
        "https://slack.com/api/auth.test",
        headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
    )
    data = resp.json()
    return data.get("user_id")

BOT_USER_ID = get_bot_user_id()

SYSTEM_PROMPT = """You are a helpful AI assistant for the Stageculture team. \
You help with writing, research, analysis, brainstorming, strategy, \
summarizing, drafting communications, answering questions, and general \
productivity tasks. Be concise, professional, and direct. \
Format your responses clearly using plain text suitable for Slack. \
Do not use markdown headers — use short paragraphs or bullet points instead."""


def verify_slack_signature(req):
    """Verify the request actually came from Slack."""
    timestamp = req.headers.get("X-Slack-Request-Timestamp", "")
    try:
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
    except ValueError:
        return False
    sig_basestring = f"v0:{timestamp}:{req.get_data(as_text=True)}"
    my_signature = "v0=" + hmac.new(
        SLACK_SIGNING_SECRET.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()
    slack_signature = req.headers.get("X-Slack-Signature", "")
    return hmac.compare_digest(my_signature, slack_signature)


def post_message(channel, text, thread_ts=None):
    """Post a message to a Slack channel."""
    payload = {"channel": channel, "text": text}
    if thread_ts:
        payload["thread_ts"] = thread_ts
    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
        json=payload,
    )
    return response.json()


def ask_claude(user_message):
    """Send a message to Claude and return the response."""
    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )
    return message.content[0].text


@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json

    # Handle Slack URL verification challenge
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data["challenge"]})

    # Verify request came from Slack
    if not verify_slack_signature(request):
        return jsonify({"error": "Invalid signature"}), 403

    event = data.get("event", {})
    event_id = data.get("event_id", "")

    # Deduplicate (Slack may deliver the same event more than once)
    if event_id in processed_events:
        return jsonify({"ok": True})
    processed_events.add(event_id)
    if len(processed_events) > 1000:
        processed_events.clear()

    event_type = event.get("type")
    subtype = event.get("subtype")
    user_id = event.get("user")

    # Ignore bot messages (our own replies and other bots) to prevent loops
    if event.get("bot_id"):
        return jsonify({"ok": True})
    if subtype in ("bot_message", "channel_join", "channel_leave", "message_deleted",
                   "message_changed", "file_share"):
        return jsonify({"ok": True})
    # Filter our own user ID as a fallback
    if user_id and user_id == BOT_USER_ID:
        return jsonify({"ok": True})

    user_text = event.get("text", "").strip()
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")

    if not user_text or not channel:
        return jsonify({"ok": True})

    # Respond to all messages in channels (message) and @mentions (app_mention)
    if event_type in ("message", "app_mention"):
        # Strip any @mention prefixes so Claude sees clean text
        clean_text = re.sub(r"<@[A-Z0-9]+>", "", user_text).strip()
        if not clean_text:
            return jsonify({"ok": True})

        try:
            reply = ask_claude(clean_text)
        except Exception as e:
            reply = f"Something went wrong on my end — please try again. ({e})"

        post_message(channel, reply, thread_ts=thread_ts)

    return jsonify({"ok": True})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "stageculture-ai-bot"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
