import os

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from indicators import evaluate_all_indicators
from patterns import detect_all_patterns
from utils import analyze_with_vision, extract_text, fuse_signals

load_dotenv()

st.set_page_config(page_title="Stockity Crypto IDX Analyzer", layout="centered")
st.title("📊 Stockity Crypto IDX Analyzer")
st.caption("Upload do print do gráfico e receba CALL / PUT / NEUTRO com base em IA + padrões + indicadores.")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("🔑 Configure sua OPENAI_API_KEY no arquivo .env")
    st.stop()

uploaded_file = st.file_uploader("📤 Envie o print do gráfico da Stockity (Crypto IDX)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gráfico enviado", use_container_width=True)

    with st.spinner("Analisando imagem, padrões e indicadores..."):
        extracted_text = extract_text(image)
        vision_result = analyze_with_vision(image, extracted_text, api_key)

        # Dados simulados para teste (substituir por extração real de candles no futuro)
        sample_closes = [100.0, 100.5, 99.8, 101.2, 100.9, 101.5, 102.0, 101.8, 102.5, 103.0,
                         102.8, 103.5, 104.0, 103.7, 104.2, 104.8, 105.0, 104.5, 105.5, 106.0]

        sample_ohlc = []
        for i, close in enumerate(sample_closes):
            open_p = close - 0.1 if i % 2 == 0 else close + 0.1
            high = max(open_p, close) + 0.2
            low = min(open_p, close) - 0.2
            sample_ohlc.append({"open": open_p, "high": high, "low": low, "close": close})

        pattern_signals = detect_all_patterns(sample_ohlc)
        indicator_signals = evaluate_all_indicators(sample_closes)
        final_dir, confidence, votes = fuse_signals(pattern_signals, indicator_signals, vision_result)

    st.subheader("🎯 Sinal Final")

    color = {"CALL": "green", "PUT": "red", "NEUTRO": "gray"}[final_dir]
    st.markdown(f"<h1 style='text-align: center; color: {color};'>{final_dir}</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>Confiança: {confidence:.0%}</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    col1.metric("Direção IA Visual", vision_result.get("direcao", "NEUTRO"))
    col2.metric("Confiança IA Visual", f"{vision_result.get('confianca', 0):.0%}")

    st.write("**Justificativa da IA:**", vision_result.get("justificativa", "—"))
    st.write("**Timeframe sugerido:**", vision_result.get("timeframe_sugerido", "—"))
    st.write("**Texto detectado na imagem:**", extracted_text or "Nenhum")

    with st.expander("📋 Sinais dos padrões de candle"):
        if pattern_signals:
            for name, direction, weight in pattern_signals:
                st.write(f"- {name} → **{direction}** (peso {weight})")
        else:
            st.write("Nenhum padrão detectado.")

    with st.expander("📈 Sinais dos indicadores técnicos"):
        if indicator_signals:
            for name, direction, weight in indicator_signals:
                st.write(f"- {name} → **{direction}** (peso {weight})")
        else:
            st.write("Nenhum sinal de indicador.")

    with st.expander("🤖 Votos combinados"):
        st.json(votes)

    st.warning(
        "⚠️ Este aplicativo é uma ferramenta de análise técnica automatizada. "
        "Não é recomendação de investimento. Opções binárias envolvem alto risco de perda."
    )
