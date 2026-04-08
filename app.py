import streamlit as st
import requests
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Stock Analyzer",
    page_icon="📊",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif;
    background-color: #0a0e17;
    color: #e2e8f0;
}
.stApp { background-color: #0a0e17; }
h1, h2, h3 { font-family: 'Syne', sans-serif; font-weight: 800; }

.ticker-badge {
    display: inline-block;
    background: #00ff87;
    color: #0a0e17;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    font-size: 1.3rem;
    padding: 6px 18px;
    border-radius: 4px;
    letter-spacing: 2px;
}
.analysis-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-left: 4px solid #00ff87;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 12px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
}
.stButton > button {
    background: transparent !important;
    border: 1px solid #1e293b !important;
    color: #94a3b8 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #00ff87 !important;
    color: #00ff87 !important;
}
.stTextInput > div > div > input {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 1rem !important;
    letter-spacing: 2px !important;
    border-radius: 6px !important;
}
.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1e293b !important;
    color: #e2e8f0 !important;
    font-family: 'Space Mono', monospace !important;
    border-radius: 6px !important;
}
.section-label {
    font-size: 0.65rem;
    letter-spacing: 3px;
    color: #475569;
    text-transform: uppercase;
    font-family: 'Space Mono', monospace;
    margin-bottom: 8px;
}
.tag {
    display: inline-block;
    background: #1e293b;
    color: #94a3b8;
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 3px;
    letter-spacing: 1px;
}
.disclaimer {
    font-size: 0.65rem;
    color: #334155;
    font-family: 'Space Mono', monospace;
    text-align: center;
    margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── API setup ─────────────────────────────────────────────────────────────────
api_key = st.secrets["OPENROUTER_API_KEY"]
MODEL   = "openai/gpt-4o-mini"
TODAY   = datetime.now().strftime("%A, %B %d, %Y")

# ── Analysis types & prompts ──────────────────────────────────────────────────
ANALYSIS_TYPES = {
    "📊 Full Fundamental Analysis": "fundamental",
    "📈 Technical Analysis":        "technical",
    "💰 Valuation Check":           "valuation",
    "⚠️  Risk Assessment":          "risk",
    "🔍 Competitor Comparison":     "compare",
    "📰 Sentiment Snapshot":        "sentiment",
}

SYSTEM_PROMPTS = {
    "fundamental": f"""You are a senior equity research analyst. Today is {TODAY}.
Given a stock ticker or company name, produce a structured FUNDAMENTAL ANALYSIS covering:
1. Business Overview – what the company does, revenue model, competitive moat
2. Key Financial Metrics – Revenue growth, Net Income, EPS, Debt/Equity, ROE, P/E, P/S
3. Strengths & Risks – concise bullet points
4. Analyst Verdict – BUY / HOLD / SELL with a one-line rationale
Use a professional but direct tone. Format cleanly with headers. End with a disclaimer.""",

    "technical": f"""You are a technical analysis expert. Today is {TODAY}.
Given a stock ticker, deliver a TECHNICAL ANALYSIS covering:
1. Trend – current trend direction (up/down/sideways) across multiple timeframes
2. Key Levels – major support and resistance zones
3. Indicators – RSI, MACD, Moving Averages (50/200-day), Bollinger Bands
4. Chart Patterns – any notable formations (cup & handle, H&S, flags, wedges, etc.)
5. Short-term Signal – BULLISH / BEARISH / NEUTRAL with reasoning
Format cleanly with headers. Include disclaimer.""",

    "valuation": f"""You are a valuation analyst. Today is {TODAY}.
For the given stock, produce a VALUATION ANALYSIS covering:
1. Valuation Multiples – P/E, Forward P/E, PEG, P/S, P/B, EV/EBITDA
2. DCF Snapshot – rough intrinsic value estimate and key assumptions
3. Peer Comparison – vs. sector average multiples
4. Verdict – OVERVALUED / FAIRLY VALUED / UNDERVALUED with estimated margin
Be quantitative where possible. Disclaimer at end.""",

    "risk": f"""You are a risk management specialist. Today is {TODAY}.
For the given stock, produce a RISK ASSESSMENT covering:
1. Macro Risks – interest rates, inflation, geopolitical exposure
2. Company-Specific Risks – earnings volatility, debt levels, competition, regulation
3. Beta & Volatility Profile – high/medium/low with reasoning
4. Risk Score per category – LOW / MEDIUM / HIGH
5. Risk-Reward Summary – is the risk worth taking at current levels?
Format as a structured report. Disclaimer at end.""",

    "compare": f"""You are a stock comparison analyst. Today is {TODAY}.
The user will provide 2-3 companies. Produce a COMPETITOR COMPARISON covering:
1. Business Model Differences
2. Financial Metrics Side-by-Side – Revenue, Net Margin, P/E, Market Cap, YoY Growth
3. Competitive Advantages – moat analysis per company
4. Winner Pick – which stock offers the best risk-adjusted return and why
Present as a structured side-by-side report. Disclaimer at end.""",

    "sentiment": f"""You are a market sentiment analyst. Today is {TODAY}.
For the given stock or sector, deliver a SENTIMENT SNAPSHOT covering:
1. News Sentiment – recent headlines tone (positive/negative/mixed)
2. Analyst Ratings – consensus rating and price target range
3. Social & Retail Sentiment – retail investor mood (Reddit/X/options flow)
4. Insider Activity – recent insider buys or sells
5. Overall Sentiment Score – BULLISH / NEUTRAL / BEARISH with confidence level
Keep it punchy and current. Disclaimer at end.""",
}

# ── Session state ─────────────────────────────────────────────────────────────
if "result"      not in st.session_state: st.session_state.result      = ""
if "last_ticker" not in st.session_state: st.session_state.last_ticker = ""
if "history"     not in st.session_state: st.session_state.history     = []

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("## 📊 SMART STOCK ANALYZER")
st.markdown(f'<div class="section-label">AI-Powered Equity Intelligence · {TODAY}</div>', unsafe_allow_html=True)
st.divider()

# ── Main layout ───────────────────────────────────────────────────────────────
col_input, col_result = st.columns([1, 2], gap="large")

with col_input:
    st.markdown('<div class="section-label">01 — Enter Ticker / Company</div>', unsafe_allow_html=True)
    ticker = st.text_input("", placeholder="e.g. AAPL, TSLA, Nvidia...", label_visibility="collapsed").upper().strip()

    st.markdown('<div class="section-label" style="margin-top:20px">02 — Choose Analysis Type</div>', unsafe_allow_html=True)
    analysis_label = st.selectbox("", list(ANALYSIS_TYPES.keys()), label_visibility="collapsed")
    analysis_key   = ANALYSIS_TYPES[analysis_label]

    st.markdown('<div class="section-label" style="margin-top:20px">03 — Additional Context (optional)</div>', unsafe_allow_html=True)
    extra_context = st.text_area(
        "",
        placeholder="e.g. Compare with AMD and Intel / Focus on Q4 earnings / 5-year horizon",
        height=90,
        label_visibility="collapsed"
    )

    run_btn = st.button("⚡ RUN ANALYSIS", use_container_width=True)

    # ── Quick tickers ──────────────────────────────────────────────────────────
    st.markdown('<div class="section-label" style="margin-top:24px">Quick Picks</div>', unsafe_allow_html=True)
    quick_tickers = ["AAPL", "TSLA", "NVDA", "AMZN", "MSFT", "GOOGL"]
    qcols = st.columns(3)
    for i, qt in enumerate(quick_tickers):
        with qcols[i % 3]:
            if st.button(qt, key=f"q_{qt}"):
                ticker  = qt
                run_btn = True

    # ── History ────────────────────────────────────────────────────────────────
    if st.session_state.history:
        st.markdown('<div class="section-label" style="margin-top:24px">Recent Lookups</div>', unsafe_allow_html=True)
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f'<span class="tag">{item}</span>', unsafe_allow_html=True)

    st.markdown('<div class="disclaimer">For educational purposes only.<br>Not financial advice.</div>', unsafe_allow_html=True)

# ── Result panel ──────────────────────────────────────────────────────────────
with col_result:
    if run_btn and ticker:
        st.session_state.last_ticker = ticker
        entry = f"{ticker} · {analysis_label.split(' ', 1)[-1]}"
        if entry not in st.session_state.history:
            st.session_state.history.append(entry)

        with st.spinner(f"Analyzing {ticker}..."):
            user_message = f"Stock/Company: {ticker}\nAnalysis requested: {analysis_label}"
            if extra_context:
                user_message += f"\nAdditional context: {extra_context}"

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://your-app.streamlit.app",
                        "X-Title": "Smart Stock Analyzer",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": SYSTEM_PROMPTS[analysis_key]},
                            {"role": "user",   "content": user_message},
                        ],
                    },
                    timeout=45,
                )
                data = response.json()
                if "choices" in data:
                    st.session_state.result = data["choices"][0]["message"]["content"]
                elif "error" in data:
                    st.session_state.result = f"❌ Error: {data['error'].get('message', 'Unknown error')}"
                else:
                    st.session_state.result = f"❌ Unexpected: {data}"
            except requests.exceptions.Timeout:
                st.session_state.result = "❌ Timed out. Please try again."
            except Exception as e:
                st.session_state.result = f"❌ Error: {str(e)}"

    if st.session_state.result:
        t = st.session_state.last_ticker
        st.markdown(f'<div class="ticker-badge">{t}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:inline-block;margin-left:12px;color:#475569;font-size:0.75rem;'
            f'font-family:\'Space Mono\',monospace;letter-spacing:1px">{analysis_label}</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="analysis-card">' + st.session_state.result.replace("\n", "<br>") + '</div>',
            unsafe_allow_html=True
        )

        col_dl, col_cl = st.columns([3, 1])
        with col_cl:
            if st.button("🗑 Clear", use_container_width=True):
                st.session_state.result = ""
                st.rerun()
        with col_dl:
            st.download_button(
                "⬇ Download Report",
                data=st.session_state.result,
                file_name=f"{t}_analysis_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True,
            )
    else:
        st.markdown("""
        <div style="height:300px;display:flex;flex-direction:column;
             align-items:center;justify-content:center;opacity:0.25;">
            <div style="font-size:3rem;">📊</div>
            <div style="font-family:'Space Mono',monospace;font-size:0.8rem;
                 margin-top:12px;letter-spacing:2px;">ENTER A TICKER TO BEGIN</div>
        </div>
        """, unsafe_allow_html=True)
