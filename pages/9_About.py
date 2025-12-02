import streamlit as st

st.set_page_config(page_title="About Inspectra", layout="centered")

# --- Custom CSS for hero and card sections (using your homepage style) ---
st.markdown("""
<style>
.inspectra-hero {
    background: linear-gradient(135deg, #00e4d0, #00c3ff);
    padding: 1rem 2rem;
    border-radius: 16px;
    margin-top: -3rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: center;
    animation: fadeInHero 1.2s;
}
@keyframes fadeInHero {
    from { opacity: 0; transform: translateY(-32px);}
    to   { opacity: 1; transform: translateY(0);}
}
.inspectra-inline {
    display: inline-flex;
    align-items: center;
    gap: 1.2rem;
    white-space: nowrap;
}
.inspectra-title {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    color: #fff;
    letter-spacing: -1px;
    text-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.inspectra-divider {
    font-weight: 400;
    color: #004e66;
    opacity: 0.35;
}
.inspectra-tagline {
    font-size: 1rem;
    font-weight: 500;
    margin: 0;
    color: #e3feff;
    opacity: 0.90;
    position: relative;
    top: 2px;
    letter-spacing: 0.5px;
}

.section {
    background: #f6fafd;
    border-radius: 1.1rem;
    padding: 1.4rem 1.5rem 1.1rem 1.5rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 1px 7px 0 rgba(60,95,246,0.07);
    border-left: 5px solid #00c3ff;
    animation: fadeInSection 0.8s;
}
@keyframes fadeInSection {
    from { opacity: 0; transform: translateY(36px);}
    to   { opacity: 1; transform: translateY(0);}
}
.section-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #169bb6;
    margin-bottom: 0.4rem;
    letter-spacing: -1px;
    display: flex;
    align-items: center;
    gap: 8px;
}
ul, ol {
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}
.footer {
    text-align: center;
    font-size: 1.04rem;
    color: #7a849a;
    margin-top: 2.3rem;
    margin-bottom: 0.4rem;
}
a { color: #00b6e4; text-decoration: none; }
a:hover { text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

# --- HERO BAR (your homepage style) ---
st.markdown("""
    <div class="inspectra-hero">
        <div class="inspectra-inline">
            <span class="inspectra-title">Inspectra</span>
            <span class="inspectra-divider">|</span>
            <span class="inspectra-tagline">Where Precision Meets Integrity.</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- All animated section cards, no blank divs, all modern ---
st.markdown("""
<div class="section">
    <div class="section-title">🤖 What is Inspectra?</div>
    <b>Inspectra</b> is a custom-built internal tool designed to automate and streamline QA validation processes at Interlink.<br>
    It reduces manual effort, improves consistency, and enables teams to validate data <b>faster and more accurately</b>.
</div>

<div class="section">
    <div class="section-title">💡 Why it was built</div>
    Inspectra was created to address the challenges of manual QA processes, which often involve:
    <ul>
        <li>⏱️ <b>Time-consuming manual checks</b> of Excel files</li>
        <li>⚠️ <b>High risk of human error</b> in data validation</li>
        <li>🔁 <b>Inconsistent validation logic</b> across different team members</li>
        <li>📈 <b>Difficulty in scaling QA efforts</b> for large campaigns</li>
        <li>👀 <b>Lack of visibility</b> into validation issues and resolutions</li>
    </ul>
</div>

<div class="section">
    <div class="section-title">✨ How it helps</div>
    <ul>
        <li>🚀 <b>Saves time</b> by automating complex Excel validations</li>
        <li>🧠 <b>Reduces manual errors</b> through rule-based logic</li>
        <li>📊 <b>Improves consistency</b> across QA outputs</li>
        <li>🔄 <b>Easily adaptable</b> to future validation scenarios</li>
    </ul>
</div>

<div class="section">
    <div class="section-title">🛠️ Who built it</div>
    This tool was created and developed by
    <a href="https://www.linkedin.com/in/felixmarkaspowerbi/" target="_blank"><b>Felix Markas Salve</b></a>
    as a self-driven internal innovation project under Interlink.<br>
    Felix designed the logic, implemented the automation, and shaped the vision for how QA can be improved company-wide.
</div>

<div class="section">
    <div class="section-title">🚀 What’s Next?</div>
    The vision for Inspectra is simple: upload the client’s ABM list and suppression file — and get instant, reliable QA.<br>
    <b>Here’s what’s coming:</b>
    <ul>
        <li>📥 <b>Support for direct ABM & suppression uploads</b> – no manual mapping needed</li>
        <li>✅ <b>Pre-set rule templates</b> – validations tailored by client or campaign type</li>
        <li>📊 <b>Detailed issue summaries</b> – clear reports you can send or log immediately</li>
        <li>🔗 <b>Optional integration</b> with delivery or QA tools – for faster approvals</li>
    </ul>
</div>

<div class="footer">
    © 2025 Interlink. All rights reserved.<br>
    Built by Felix Markas Salve as an internal innovation project.
</div>
""", unsafe_allow_html=True)

