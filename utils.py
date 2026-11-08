import base64
import json
import re
from io import BytesIO

import cv2
import easyocr
import numpy as np
import openai
from PIL import Image


reader = easyocr.Reader(["pt", "en"], gpu=False)


def extract_text(image: Image.Image):
    arr = np.array(image)
    results = reader.readtext(arr)
    return " ".join([r[1] for r in results])


def analyze_with_vision(image: Image.Image, text_extracted: str, api_key: str):
    client = openai.OpenAI(api_key=api_key)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    prompt = f"""
Você é um trader técnico especializado em opções binárias de curto prazo.
Analise o print do gráfico enviado e responda APENAS com JSON válido:

{{
  "direcao": "CALL" ou "PUT" ou "NEUTRO",
  "confianca": número entre 0.0 e 1.0,
  "justificativa": "máximo 2 frases",
  "timeframe_sugerido": "ex: 1 minuto, 5 minutos, M5",
  "observacao": "indicadores ou padrões visuais identificados"
}}

Texto extraído da imagem: {text_extracted or "nenhum"}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{img_b64}"},
                        },
                    ],
                }
            ],
            max_tokens=500,
        )
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*|```$", "", raw).strip()
        return json.loads(raw)
    except Exception as e:
        return {
            "direcao": "NEUTRO",
            "confianca": 0.0,
            "justificativa": f"Erro na análise visual: {str(e)}",
            "timeframe_sugerido": "N/A",
            "observacao": "",
        }


def fuse_signals(pattern_signals, indicator_signals, vision_result):
    votes = {"CALL": [], "PUT": [], "NEUTRO": []}

    for name, direction, weight in pattern_signals + indicator_signals:
        votes[direction].append((name, weight))

    vision_dir = vision_result.get("direcao", "NEUTRO")
    vision_conf = vision_result.get("confianca", 0)
    if vision_dir != "NEUTRO":
        votes[vision_dir].append(("Análise visual IA", vision_conf))

    score_call = sum(w for _, w in votes["CALL"])
    score_put = sum(w for _, w in votes["PUT"])
    total = score_call + score_put

    if total == 0:
        return "NEUTRO", 0.0, votes

    if score_call > score_put:
        return "CALL", score_call / total, votes
    if score_put > score_call:
        return "PUT", score_put / total, votes
    return "NEUTRO", 0.5, votes
