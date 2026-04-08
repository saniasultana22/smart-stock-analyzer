import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Smart Stock Analyzer", page_icon="📈")
st.title("📈 Smart Stock Analyzer")

api_key = st.secrets["OPENROUTER_API_KEY"]
model = "openai/gpt-4o-mini"

# System prompt with today's real date injected
today = datetime.now().strftime("%A, %B %d, %Y")
SYSTEM_PROMPT = f"""You are an expert AI stock market analyst with deep knowledge of financial markets, technical analysis, fundamental analysis, and investment strategies. Today's date is {today}. Always use this date as your reference when discussing market conditions, recent trends, or time-sensitive stock data.

Your capabilities include:
- Analyzing stocks based on ticker symbols, company names, or sectors
- Explaining financial metrics (P/E ratio, EPS, market cap, RSI, MACD, etc.)
- Discussing investment strategies (value investing, growth investing, swing trading, etc.)
- Providing risk assessments and portfolio diversification advice
- Interpreting news and macroeconomic factors affecting stocks
- Comparing companies within the same industry

Always remind users that your analysis is for educational purposes only and does not constitute financial advice. Encourage consulting a licensed financial advisor for personalized investment decisions."""

with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown(f"**Model:** `{model}`")
    st.caption(f"📅 Today: {today}")

    st.divider()
    st.subheader("🔍 Quick Prompts")
    quick_prompts = [
        "Analyze Apple (AAPL) stock",
        "Explain P/E ratio",
        "Best sectors to invest in 2025?",
        "Compare Tesla vs Rivian",
        "What is a bull trap?",
        "How to read candlestick charts?",
    ]
    for prompt in quick_prompts:
        if st.button(prompt, use_container_width=True):
            st.session_state["quick_input"] = prompt

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pop("quick_input", None)
        st.rerun()

    st.caption("⚠️ *For educational purposes only. Not financial advice.*")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle quick prompt injection
default_input = st.session_state.pop("quick_input", "")

user_input = st.chat_input("Ask about any stock, market trend, or financial concept...") or default_input

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Analyzing market data..."):
            try:
                messages_with_system = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + st.session_state.messages

                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://your-app.streamlit.app",
                        "X-Title": "Smart Stock Analyzer",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages_with_system
                    },
                    timeout=30
                )
                data = response.json()
                if "choices" in data:
                    reply = data["choices"][0]["message"]["content"]
                elif "error" in data:
                    reply = f"❌ Error {data['error'].get('code', '')}: {data['error'].get('message', 'Unknown error')}"
                else:
                    reply = f"❌ Unexpected response: {data}"
            except requests.exceptions.Timeout:
                reply = "❌ Request timed out. Please try again."
            except Exception as e:
                reply = f"❌ Error: {str(e)}"
        st.write(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
