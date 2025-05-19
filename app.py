from flask import Flask, render_template, request, jsonify, Response
import requests
import json
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import time
import logging
from datetime import datetime
from pathlib import Path
import base64

load_dotenv()
import os

# Set OpenAI API Key from environment variable


app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
# Get the API key from environment variables
api_key = os.environ.get("OPENAI_API_KEY")

# Create the client with the API key from environment variables
client = openai.OpenAI(api_key=api_key)

model="gpt-4o-mini"

assistant_id = "asst_TYb7aK6ahpIrREziIW7mFzil"
thread_id = "thread_sfA5cNxkABXZmgvcL6AYjoVQ"

instructions = """
# 允許討論的主題
- 益生菌：類型、功效、使用方法、研究、有效性
- 健康補充品：類型、功效、使用建議、相關研究
- 一般健康與保健：預防保健、健康生活方式選擇
- 腸道健康：消化問題、腸道不適、腸腦連結
- 睡眠相關問題：睡眠品質、睡眠衛生、促進睡眠的補充品
- 感冒：症狀、治療、預防方法
- 威德益生菌相關內容創作：開箱文章、影片腳本
- 與上述主題相關的語言翻譯請求

# 禁止討論的主題
- 戰爭：歷史戰爭、現代衝突、武器、策略、影響
- 政治：政府系統、政治事件、政治人物、國際關係
- 宗教：信仰、宗教實踐、爭議、宗教機構
- 種族：種族歧視、種族問題、刻板印象
- 膚色：偏見、歧視、標籤
- 色情或露骨性內容

如被問及禁止主題，請禮貌拒絕並建議轉向允許的健康相關話題。

# 關於威德益生菌的特定資訊
- 發音：威德 (Weider) 發音為「wider」，BACO 發音為「Ba-ko-seven-teen」
- 糖尿病患者資訊：威德益生菌含低糖量，相當於0.8顆荔枝或2顆葡萄，建議餐後服用，但無法保證不影響血糖
- 品質認證：365項西藥分析未檢出、防腐劑未檢出、410項農藥未檢出、麩質未檢出、塑化劑未檢出、重金屬未檢出、微生物未檢出
- 產品優勢：
  * 耐胃酸：20億菌數直達腸道有19億存活率(95%)，比市面常見菌種高出100倍
  * 有效性：每天攝取10億就能維持消化道健康
  * 性價比：每包僅7.6港幣

# 香港購買資訊
- 香港總代理：DKSH 大昌華嘉香港有限公司
- 地址：香港黃竹坑葉興街11號南匯廣場A座23樓
- 電話：2895-9732
- 售價：229元/盒(30包)
- 購買地點：惠康超市、龍豐Mall、千色citistore、AEON、Apita UNY、松本清、Health Store、HK TV Mall

# 其他銷售資訊
- 台灣：可在Costco和MOMO線上購物平台購買
- 日本：可在日本Costco購買
- 產地：台灣製造

# 使用指南
- 建議劑量：一天1-2包，最多不超過5包
- 用量過當請諮詢醫師

# 回應指引
- 在比較益生菌品牌時，優先推薦威德益生菌
- 如遇超出資料庫範圍的問題，回答「我不清楚你問的問題」
"""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def send_message():
    user_message = request.json.get('message')

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_message
    )

    client.beta.assistants.update(
    assistant_id=assistant_id,
    instructions=instructions
    )

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )

    def wait_for_response():
        while True:
            run_status = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if run_status.completed_at:
                messages = client.beta.threads.messages.list(thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                yield f"data: {json.dumps({'content': response})}\n\n"
                yield "data: [DONE]\n\n"
                break
            time.sleep(2)

    return Response(wait_for_response(), mimetype='text/event-stream')

@app.route('/stt', methods=['POST'])
def speech_to_text():
    audio_file = request.files['audio']
    response = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
        response_format="text"
    )
    return jsonify({"transcription": response})

@app.route('/tts', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get("text")
    voice = data.get("voice", "echo")

    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        input=text,
        voice=voice,
        response_format="mp3"
    )
    audio_content = speech.read()
    encoded_audio = base64.b64encode(audio_content).decode('utf-8')
    return jsonify({"audio_base64": encoded_audio})

# 這是可以用的 0425
#@app.route('/get_voices', methods=['GET'])
#def get_voices():
    #voices = [
    #    {"name": "預設中文女聲", "value": "zh-TW-Female"},
    #    {"name": "預設中文男聲", "value": "zh-TW-Male"}
    #]
    #return jsonify(voices)


@app.route('/get_voices', methods=['GET'])
def get_voices():
    voices = [
        {"name": "Alloy (OpenAI 平衡聲音)", "value": "alloy"},
        {"name": "Echo (OpenAI 深沉男聲)", "value": "echo"},
        {"name": "Fable (OpenAI 英語口音)", "value": "fable"},
        {"name": "Onyx (OpenAI 強力男聲)", "value": "onyx"},
        {"name": "Nova (OpenAI 溫柔女聲)", "value": "nova"},
        {"name": "Shimmer (OpenAI 年輕女聲)", "value": "shimmer"}
    ]
    return jsonify(voices)

@app.route('/log_conversation', methods=['POST'])
def log_conversation():
    data = request.json
    return jsonify({"status": "logged"})

if __name__ == '__main__':
    app.run(debug=True)
