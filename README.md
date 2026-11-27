# 💜 EmpowerHER

**Live demo:** https://pooja-empowerher.streamlit.app/

A multilingual AI companion for women's support, built with Streamlit.

## Features

- **Six help topics**: legal rights (Indian context), self defense, mental health, period and wellness, career and education, self-love
- **8 languages**: ask and read answers in English, Hindi, Kannada, Tamil, Telugu, Spanish, French or Arabic
- **SOS alert**: enter your location and trusted contacts, connect your own Twilio account, and send an SMS alert in one tap
- **Fast answers** from Google Gemini, tuned to always finish every list it starts
- **Curated YouTube videos** for every topic, plus one-tap links to explore more
- **India helplines** (112, 181, NCW 14490, cyber crime 1930, KIRAN mental health) with tap-to-call
- **Private by design**: contacts and location live only in your session

## Run locally

```bash
pip install -r requirements.txt
streamlit run empowerher.py
```

Add your Gemini key in `.streamlit/secrets.toml` (Twilio details can also be entered in the SOS tab):

```toml
GEMINI_API_KEY = "..."
```

## Stack

Python · Streamlit · Gemini API · Twilio · deep-translator

Author: Pooja J
