import re
import requests
import streamlit as st
from deep_translator import GoogleTranslator

st.set_page_config(page_title="EmpowerHER", page_icon="💜", layout="wide")

MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
SYSTEM = ("You are EmpowerHER, a warm, practical assistant supporting women. You give clear guidance on "
          "legal rights (Indian context), self-defense, mental health, period wellness, career and "
          "education, and personal safety. Keep answers short, kind and actionable.")
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


def ask(prompt):
    key = secret("GEMINI_API_KEY") or st.session_state.get("ai_key")
    if not key:
        st.info("Add a Gemini key in the sidebar to chat.")
        return ""
    last = None
    for m in MODELS:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
            headers={"x-goog-api-key": key},
            json={"systemInstruction": {"parts": [{"text": SYSTEM}]},
                  "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                  "generationConfig": {"temperature": 0.7, "maxOutputTokens": 700}}, timeout=60)
        if r.status_code == 200:
            try:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            except Exception:
                last = "empty"
                continue
        last = r.status_code
        if last in (400, 401, 403):
            break
    st.error(f"The AI service returned status {last}. Check the key and try again.")
    return ""


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
            code = LANGS[lang_name]
            with st.spinner("Thinking..."):
                ans = ask(f"Topic: {topic}. Question: {translate(q, 'en')}")
            if ans:
                st.markdown("**EmpowerHER:** " + translate(ans, code))
    else:
        st.write("Pick a topic to get started.")

with tab_sos:
    st.write("Send your location to people you trust. Everything you enter stays in this session.")
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
