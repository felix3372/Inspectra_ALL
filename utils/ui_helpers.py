import json
import streamlit as st
import time
from streamlit_lottie import st_lottie

def load_lottiefile(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def show_splash(lottie_path, sleep_time=3):
    lottie_robot = load_lottiefile(lottie_path)
    if "splash_done" not in st.session_state:
        st.session_state.splash_done = False

    if not st.session_state.splash_done:
        st.markdown("""
        <br>
            <div class="welcome-container">
                <div class="welcome-message">
                    Inspectra QA Automation
                </div>
            </div>
        """, unsafe_allow_html=True)

        st_lottie(
            lottie_robot,
            speed=1,
            reverse=False,
            loop=True,
            quality="medium",
            height=320,
            key="robot-lottie",
        )

        st.markdown("""
            <div style='text-align:center; margin-top:0.39rem; font-size:1.05rem; color:#106d85; font-weight:600; letter-spacing:0.02em;'>
                Powered by Inspectra V1.0
            </div>
        """, unsafe_allow_html=True)

        time.sleep(sleep_time)
        st.session_state.splash_done = True
        st.rerun()
