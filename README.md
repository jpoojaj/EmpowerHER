# 💜 EmpowerHER

A multilingual AI companion for women's support, built with Streamlit.

## Features

- **Six help topics**: legal rights (Indian context), self defense, mental health, period and wellness, career and education, self-love
- **8 languages**: ask and read answers in English, Hindi, Kannada, Tamil, Telugu, Spanish, French or Arabic
- **SOS alert**: enter your location and trusted contacts, then send an SMS alert in one tap (Twilio)
- **Fast answers** from Llama models served by Groq
- **Private by design**: contacts and location live only in your session

## Run locally

```bash
pip install -r requirements.txt
streamlit run empowerher.py
```

Add keys in `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "..."
TWILIO_SID = "..."
TWILIO_AUTH_TOKEN = "..."
TWILIO_PHONE = "+1..."
```

## Stack

Python · Streamlit · Groq API · Twilio · deep-translator

Author: Pooja J
