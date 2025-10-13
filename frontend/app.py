# frontend/app.py
import streamlit as st
import requests
from urllib.parse import urlparse

API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(page_title="PhishGuardian", layout="centered")
st.title("🛡️ PhishGuardian")
st.write("Paste a URL below and get a phishing check + suggested official URL (if any).")

col1, col2 = st.columns([2, 3])
with col1:
    url = st.text_input("🔗 Enter URL to check", placeholder="e.g. paypal.com.login.verify-account.ru")
    check = st.button("Check")

with col2:
    st.write("")

if check:
    if not url.strip():
        st.warning("Please enter a URL")
    else:
        try:
            resp = requests.post(API_URL, json={"url": url}, timeout=10)
            if resp.status_code != 200:
                st.error("Backend error: " + resp.text)
            else:
                r = resp.json()
                pred = r.get("prediction")
                conf = r.get("confidence")
                st.markdown("**Result:**")
                if pred == 1:
                    st.success(f"✅ Legitimate (confidence {conf:.2f})")
                else:
                    st.error(f"🚨 Phishing suspected (confidence {conf:.2f})")

                # suggestion
                suggested = r.get("suggested_legit_url")
                sim = r.get("similarity", 0.0)
                suggested_domain = r.get("suggested_domain")
                category = r.get("suggested_category")
                if suggested:
                    st.markdown("---")
                    st.markdown(f"**Suggested official site** ({category}) — similarity {sim:.2f}")
                    # clickable link opening in new tab:
                    st.markdown(f"""<a href="{suggested}" target="_blank">
                                    <button style="background-color:#007bff;color:white;padding:6px 12px;border-radius:6px;border:none;">
                                    Open suggested site
                                    </button></a>""", unsafe_allow_html=True)
                    st.write(f"Domain: {suggested_domain}")
                else:
                    st.info("No close official match found.")

        except Exception as e:
            st.error(f"Could not reach backend: {e}")
