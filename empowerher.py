import streamlit as st
from openai import OpenAI
from deep_translator import GoogleTranslator
import random
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# === Configuration ===
GROQ_API_KEY = "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"
TWILIO_SID = "ACd97c4f7cc7d298eef2561ce80596aa2d"
TWILIO_AUTH_TOKEN = "2e238ee8394eb81d6b80a2481ecbc959"
TWILIO_PHONE = "+15075754287"  # Your Twilio verified number

MODEL_NAME = "llama3-8b-8192"

# === Initialize Groq Client ===
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# === Translate Text ===
def translate(text, dest="en"):
    try:
        return GoogleTranslator(source='auto', target=dest).translate(text)
    except Exception as e:
        return f"Translation Error: {e}"

# === Send SOS SMS ===
def send_sos_sms(latitude, longitude, emergency_contacts):
    try:
        sms_client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
        message_body = f"🚨 EMERGENCY! A woman needs help. Location: {latitude}, {longitude}. https://maps.google.com/?q={latitude},{longitude}"

        for contact in emergency_contacts:
            try:
                message = sms_client.messages.create(
                    body=message_body,
                    from_=TWILIO_PHONE,
                    to=contact
                )
                print(f"✅ SMS sent to {contact}: SID {message.sid}")
                st.success(f"✅ SMS sent to {contact}")
            except TwilioRestException as e:
                print(f"❌ Error sending to {contact}: {e}")
                st.error(f"❌ Could not send SMS to {contact}: {e.msg}")
    except Exception as e:
        print(f"General SMS Error: {e}")
        st.error("❌ Failed to send SMS alert. Please check credentials or phone numbers.")

# === Get Groq AI Response ===
def get_response(prompt):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": (
                    "You are EmpowerHer, an empathetic AI supporting women. You provide guidance on legal rights (Indian context), self-defense, mental health, period wellness, career advice, and safety."
                )},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=512
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"🤖 Error: {e}"

# === UI Setup ===
st.set_page_config(page_title="EmpowerHer (Groq-powered)")
st.title("💬 EmpowerHer: AI Chat for Women Support")
st.markdown("👩‍💼 Voice & Multilingual | Legal, Health, Career, Safety & More")

language = st.selectbox("🌐 Choose your language:", ["English", "Hindi", "Spanish", "French", "Arabic"])

# === SOS Alert Button ===
if st.button("🚨 SOS Alert"):
    latitude = round(random.uniform(12.90, 12.99), 6)
    longitude = round(random.uniform(77.50, 77.70), 6)
    maps_url = f"https://maps.google.com/?q={latitude},{longitude}"

    # ✅ Ensure these numbers are VERIFIED on Twilio dashboard
    emergency_contacts = ['+919380830984', '+918105667274']
    
    send_sos_sms(latitude, longitude, emergency_contacts)

    st.error(f"🚨 EMERGENCY! Your coordinates: {latitude}, {longitude}\n\n[🔗 Live Location]({maps_url})")

# === Help Topics UI ===
st.markdown("---")
st.subheader("⚡ Quick Help Topics")
colA, colB, colC = st.columns(3)
with colA:
    if st.button("📜 Legal Rights"):
        st.session_state.topic = "legal_rights"
    if st.button("🛡 Self Defense"):
        st.session_state.topic = "self_defense"
with colB:
    if st.button("🧠 Mental Health"):
        st.session_state.topic = "mental_health"
    if st.button("🚺 Period & Wellness"):
        st.session_state.topic = "period_wellness"
with colC:
    if st.button("🎓 Career & Edu"):
        st.session_state.topic = "career_education"
    if st.button("💖 Self-Love Tips"):
        st.session_state.topic = "self_love"

# === Input & Chat Logic ===
if 'topic' in st.session_state:
    topic = st.session_state.topic
    st.subheader(f"Ask a question about {topic.replace('_', ' ').title()}:")
    user_question = st.text_input(f"💬 Type your {topic.replace('_', ' ')} question here:")

    if user_question:
        st.markdown("🧠 Processing...")
        input_en = translate(user_question, "en") if language != "English" else user_question
        response_en = get_response(input_en)
        response_translated = translate(response_en, language.lower()) if language != "English" else response_en

        st.markdown(f"🤖 EmpowerHer: {response_translated}")
else:
    st.markdown("❓ Please choose a topic to get started.")