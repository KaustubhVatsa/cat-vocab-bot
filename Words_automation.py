import os
import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from google import genai

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
GMAIL_ADDRESS  = os.environ.get("GMAIL_ADDRESS")
GMAIL_APP_PASS = os.environ.get("GMAIL_APP_PASS")

# Add or remove emails from this list freely
RECIPIENTS = [
    os.environ.get("GMAIL_ADDRESS"),   # you (pulled from env)
    "kaustubh26vatsa@gmail.com",
    "tanayasaxena.27august@gmail.com"       # your friend — replace this
]
# ─────────────────────────────────────────────

PROMPT = """
You are a CAT (Common Admission Test) vocabulary coach. Generate exactly 4 advanced English words 
that are frequently tested in CAT exams. These should be high-difficulty words that appear in 
Reading Comprehension and Verbal Ability sections.

Return ONLY a valid JSON array (no markdown, no explanation) in this exact format:
[
  {
    "word": "WORD",
    "pronunciation": "pro-NUN-see-AY-shun",
    "meaning": "Detailed meaning in 2-3 sentences",
    "synonyms": ["syn1", "syn2", "syn3"],
    "antonyms": ["ant1", "ant2", "ant3"],
    "sentences": [
      "First example sentence using the word naturally.",
      "Second example sentence in a different context."
    ],
    "memory_tip": "A short trick or mnemonic to remember this word."
  }
]
Return only the JSON array. No markdown fences. No extra text.
"""

def fetch_words():
    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=PROMPT
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

def build_email(words):
    html = """
    <html><body style="font-family: Georgia, serif; background: #f9f6f1; padding: 0; margin: 0;">
    <div style="max-width: 620px; margin: 30px auto; background: #ffffff; border-radius: 12px;
                overflow: hidden; border: 1px solid #e0d9ce;">

      <!-- Header -->
      <div style="background: #1a1a2e; padding: 28px 32px;">
        <h1 style="color: #f5c842; margin: 0; font-size: 22px; letter-spacing: 1px;">
          CAT VOCAB — Daily 4
        </h1>
        <p style="color: #a0a0c0; margin: 6px 0 0; font-size: 13px;">
          Advanced words for your 99th percentile journey
        </p>
      </div>
    """

    colors  = ["#e8f4fd", "#fdf3e8", "#edf8f0", "#fdf0f8"]
    accents = ["#1a6fa8", "#b06a10", "#1a7a40", "#8a1a6a"]

    for i, w in enumerate(words):
        bg     = colors[i % len(colors)]
        accent = accents[i % len(accents)]
        synonyms  = " · ".join(w.get("synonyms", []))
        antonyms  = " · ".join(w.get("antonyms", []))
        sentences = "".join(
            f'<li style="margin-bottom: 6px; color: #444;">{s}</li>'
            for s in w.get("sentences", [])
        )

        html += f"""
      <div style="padding: 24px 32px; border-bottom: 1px solid #ece6dc; background: {bg};">

        <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 10px;">
          <span style="font-size: 26px; font-weight: bold; color: {accent}; letter-spacing: 0.5px;">
            {w['word']}
          </span>
          <span style="font-size: 13px; color: #888; font-style: italic;">
            / {w['pronunciation']} /
          </span>
        </div>

        <p style="font-size: 15px; color: #222; line-height: 1.6; margin: 0 0 12px;">
          <strong style="color: {accent};">Meaning:</strong> {w['meaning']}
        </p>

        <table style="width: 100%; margin-bottom: 12px;">
          <tr>
            <td style="width: 50%; vertical-align: top;">
              <span style="font-size: 12px; font-weight: bold; color: #2a7a2a;
                           text-transform: uppercase; letter-spacing: 0.5px;">Synonyms</span><br>
              <span style="font-size: 13px; color: #333;">{synonyms}</span>
            </td>
            <td style="width: 50%; vertical-align: top; padding-left: 16px;">
              <span style="font-size: 12px; font-weight: bold; color: #c0392b;
                           text-transform: uppercase; letter-spacing: 0.5px;">Antonyms</span><br>
              <span style="font-size: 13px; color: #333;">{antonyms}</span>
            </td>
          </tr>
        </table>

        <div style="margin-bottom: 10px;">
          <span style="font-size: 12px; font-weight: bold; color: #555;
                       text-transform: uppercase; letter-spacing: 0.5px;">In a sentence</span>
          <ul style="margin: 6px 0 0; padding-left: 18px; font-size: 14px;">
            {sentences}
          </ul>
        </div>

        <div style="background: #fffbe6; border-left: 3px solid #f5c842;
                    padding: 8px 12px; border-radius: 4px;">
          <span style="font-size: 12px; font-weight: bold; color: #7a6000;">Memory Tip:</span>
          <span style="font-size: 13px; color: #555;"> {w.get('memory_tip', '')}</span>
        </div>

      </div>
        """

    html += """
      <div style="padding: 18px 32px; background: #1a1a2e; text-align: center;">
        <p style="color: #6060a0; font-size: 12px; margin: 0;">
          Stay consistent. CAT 2026 is yours. 💪
        </p>
      </div>

    </div></body></html>
    """
    return html

def send_email(html_body):
    # Filter out any None values in case an env var is missing
    recipients = [r for r in RECIPIENTS if r]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "📚 Your Daily CAT Vocab — 4 New Words"
    msg["From"]    = GMAIL_ADDRESS
    msg["To"]      = ", ".join(recipients)   # all recipients visible in To
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASS)
        server.sendmail(GMAIL_ADDRESS, recipients, msg.as_string())

    print(f"✅ Email sent to: {', '.join(recipients)}")

if __name__ == "__main__":
    print("Fetching words from Gemini...")
    words = fetch_words()
    print(f"Got {len(words)} words: {[w['word'] for w in words]}")
    html = build_email(words)
    send_email(html)