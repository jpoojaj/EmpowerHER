import re
import time
import urllib.parse

import requests
import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="EmpowerHER", page_icon="💜", layout="wide")

MODELS = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
SYSTEM = ("You are EmpowerHER, a warm, practical assistant supporting women. You give clear guidance on "
          "legal rights (Indian context), self-defense, mental health, period wellness, career and "
          "education, and personal safety. Keep answers short, kind and actionable. Always finish every "
          "point and list you start; never stop mid-sentence or mid-list.")
TOPICS = {
    "📜 Legal rights": "legal rights",
    "🛡️ Self defense": "self defense",
    "🧠 Mental health": "mental health",
    "🚺 Period & wellness": "period and wellness",
    "🎓 Career & education": "career and education",
    "💖 Self-love": "self-love",
}
LANGS = {"English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta", "Telugu": "te",
         "Spanish": "es", "French": "fr", "Arabic": "ar"}

YOUTUBE = {
    "legal rights": [
        ("Legal Rights Every Woman in India Must Know - Girl Power Talk", "https://www.youtube.com/watch?v=sTQpuAqMkkM"),
        ("Legal Protections Against Discrimination in India - LawWiser", "https://www.youtube.com/watch?v=BKr8gR0iQhc"),
    ],
    "self defense": [
        ("The 15 Most Important Women's Self-defense Techniques - Gracie Jiu-Jitsu Academy", "https://www.youtube.com/watch?v=ikoUEjb3qP4"),
        ("5 Self-Defense Moves Every Woman Should Know - Joanna Soh", "https://www.youtube.com/watch?v=KVpxP3ZZtAc"),
    ],
    "mental health": [
        ("Under the Surface: Women's Mental Health - BBC StoryWorks", "https://www.youtube.com/watch?v=-d52C1sphVg"),
        ("Women's Mental Health & Supporting Women in Your Life - Tava Health", "https://www.youtube.com/watch?v=_vFc9iy26o8"),
    ],
    "period and wellness": [
        ("Menstruation & Menstrual Hygiene - Medicover Hospitals", "https://www.youtube.com/watch?v=UBhiwkM8MIY"),
        ("Menstrual Hygiene Management - IFRC", "https://www.youtube.com/watch?v=kd_gR_S-rGw"),
    ],
    "career and education": [
        ("Women in Technology & Engineering: Career Insights - National Skills Network", "https://www.youtube.com/watch?v=3xQCHVrKG10"),
        ("Career Gap to Comeback: A Reality Check for Women - Shivangi Shrivastava", "https://www.youtube.com/watch?v=TBKaohIalUM"),
    ],
    "self-love": [
        ("How to Build Self-Confidence - Temi Akinbo", "https://www.youtube.com/watch?v=QHjzdOho-pc"),
        ("The Self-Worth Advice Every Woman Needs to Hear - Lisa Bilyeu", "https://www.youtube.com/watch?v=IbriO6QIxoU"),
    ],
}
HELPLINES = [
    ("Emergency (police, fire, ambulance)", "112"),
    ("Women Helpline", "181"),
    ("NCW Women Helpline", "14490"),
    ("Cyber Crime Helpline", "1930"),
    ("KIRAN Mental Health Helpline", "1800-599-0019"),
]

st.markdown("""<style>
.hero{padding:1.8rem 2rem;border-radius:18px;background:linear-gradient(135deg,#8E44AD,#E84393);color:#fff;margin-bottom:1.2rem}
.hero h1{margin:0;font-size:2.1rem}.hero p{margin:.3rem 0 0;opacity:.95}
</style>
<div class="hero"><h1>💜 EmpowerHER</h1>
<p>Multilingual AI support for women: legal rights, safety, wellness and career, plus a one-tap SOS location alert.</p></div>""",
unsafe_allow_html=True)


def secret(name):
    try:
        return st.secrets.get(name)
    except Exception:
        return None


def translate(text, target):
    if target == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target).translate(text)
    except Exception:
        return text


def ask(prompt, lang_name="English"):
    key = secret("GEMINI_API_KEY") or st.session_state.get("ai_key")
    if not key:
        st.info("Add a Gemini key in the sidebar to chat.")
        return ""
    last = None
    tried = []
    for attempt in range(3):
        for m in MODELS:
            try:
                r = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                    headers={"x-goog-api-key": key},
                    json={"systemInstruction": {"parts": [{"text": SYSTEM}]},
                          "contents": [{"role": "user", "parts": [{"text": prompt + f"\n\nReply entirely in {lang_name}. Finish every point."}]}],
                          "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}}, timeout=60)
            except requests.RequestException:
                last = "network error"
                continue
            if r.status_code == 200:
                try:
                    text = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        return text
                except Exception:
                    pass
                last = "empty"
                continue
            last = r.status_code
            tried.append(f"{m}: {last}")
            if last in (401, 403):
                break
        else:
            time.sleep(2 * (attempt + 1))
            continue
        break
    st.error(f"The AI service could not answer ({'; '.join(tried) or last}). Please try again in a moment.")
    return ""


def show_youtube(topic=None):
    topics = [topic] if topic in YOUTUBE else list(YOUTUBE)
    for t in topics:
        st.markdown(f"**{t.capitalize()}**")
        for title, url in YOUTUBE[t]:
            st.markdown(f"- [{title}]({url})")
        more = urllib.parse.quote_plus(f"{t} for women")
        st.markdown(f"- [More {t} videos on YouTube](https://www.youtube.com/results?search_query={more})")


def show_helplines():
    st.markdown("Free 24x7 helplines in India:")
    for name, number in HELPLINES:
        st.markdown(f"- **{name}:** [{number}](tel:{number.replace('-', '')})")


def send_sos(location_text, contacts, sid, token, sender):
    body = f"EMERGENCY: I need help. My location: {location_text}"
    ok = True
    for num in contacts:
        r = requests.post(f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
                          auth=(sid, token), data={"From": sender, "To": num, "Body": body}, timeout=30)
        if r.status_code in (200, 201):
            st.success(f"Alert sent to {num}")
        else:
            ok = False
            st.error(f"Could not send to {num} (status {r.status_code}). Check your Twilio details and that the number is verified on your account.")
    return ok


with st.sidebar:
    st.header("Settings")
    lang_name = st.selectbox("🌐 Language", list(LANGS))
    if not secret("GEMINI_API_KEY"):
        st.text_input("Gemini API key (this session only)", type="password", key="ai_key")
        st.caption("Free key at aistudio.google.com/apikey")
    with st.expander("📞 Helplines (India)"):
        show_helplines()

tab_help, tab_sos = st.tabs(["💬 Get help", "🚨 SOS alert"])

with tab_help:
    cols = st.columns(3)
    for i, (label, topic) in enumerate(TOPICS.items()):
        if cols[i % 3].button(label, use_container_width=True):
            st.session_state.topic = topic
    topic = st.session_state.get("topic")
    if topic:
        st.subheader(f"Ask about {topic}")
        q = st.text_input("Your question")
        if q:
            with st.spinner("Thinking..."):
                ans = ask(f"Topic: {topic}. Question: {q}", lang_name)
            if ans:
                st.markdown("**EmpowerHER:** " + ans)
    else:
        st.write("Pick a topic to get started.")
    with st.expander("📺 Learn more on YouTube", expanded=bool(topic)):
        show_youtube(topic)
    with st.expander("📞 Helplines (India)"):
        show_helplines()

with tab_sos:
    st.write("Send your location to people you trust. Everything you enter stays in this session.")
    with st.expander("📞 Helplines (India)", expanded=False):
        show_helplines()
    loc = st.text_input("Your location (address, landmark or a Google Maps link)")
    raw = st.text_area("Emergency contact numbers, one per line, with country code (e.g. +91XXXXXXXXXX)", height=100)
    contacts = [c.strip() for c in raw.splitlines() if re.fullmatch(r"\+\d{8,15}", c.strip())]
    with st.expander("SMS sending: use your own Twilio account", expanded=True):
        sid = st.text_input("Twilio Account SID", value=secret("TWILIO_SID") or "")
        token = st.text_input("Twilio Auth Token", type="password", value=secret("TWILIO_AUTH_TOKEN") or "")
        sender = st.text_input("Your Twilio phone number (e.g. +1XXXXXXXXXX)", value=secret("TWILIO_PHONE") or "")
        st.caption("Free trial accounts at twilio.com can message numbers verified on that account. Your details are never stored.")
    msg = f"EMERGENCY: I need help. My location: {loc}"
    ready = bool(loc.strip() and contacts)
    if st.button("🚨 Send SOS", type="primary", disabled=not ready):
        if sid and token and sender:
            send_sos(loc, contacts, sid.strip(), token.strip(), sender.strip())
        else:
            st.warning("Add your Twilio details above to send the SMS. Your alert text is ready to copy:")
        st.code(msg)

st.caption("Built by Pooja J with Streamlit, Google Gemini and Twilio.")
