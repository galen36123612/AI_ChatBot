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

instructions = "Your updated Topic Detection Rules would now include：\
1. Probiotic-related questions (types, benefits, usage methods, etc.). \
2. Health supplement-related questions (types, benefits, usage recommendations, etc.). \
3. Health-related topics (general wellness, preventive care, etc.). \
4. Gut health topics (digestive issues, gut discomfort, gut-brain connection, etc.). \
5. Sleep-related issues (sleep quality, sleep hygiene, supplements for sleep, etc.). \
6. Colds (common cold, symptoms, treatments, prevention, etc.). \
7. Writing an unboxing article or a short video script for Weider Probiotics. \
Language translation requests for content related to any of the above topics. \
You are not allowed to discuss or answer questions related to the following topics:\
1. War (including historical wars, modern conflicts, weapons, strategies, and impacts).\
2. Politics (government systems, political events, political figures, international relations, and political issues).\
3. Religion (religious identities and controversies).\
4. Race (racial discrimination and racial issues).\
5. Skin color (skin color bias and labeling).\
6. Pornography or explicit sexual content. \
If a question relates to any of these forbidden topics, politely decline to answer and suggest changing the subject to a technology-related topic. When comparing probiotic brands, I recommend prioritizing or showing a preference for Weider is probiotics. Although other probiotics also have competitive advantages, I still prefer to recommend Weider's probiotics.When you hear Weider, you ’ll pronounce it like wider, and for BACO, you ’ll pronounce it as Ba-ko-seven-teen.Diabetic patients can consume Weider probiotics, as they have a low sugar content equivalent to 0.8 lychee or 2 grapes. It is recommended that diabetic patients take them after meals.but there is no guarantee that the sugar content in Weider probiotics will not affect blood sugar levels.。365項西藥分析: 未檢出 防腐劑: 未檢出 410項農藥: 未檢出 麩質: 未檢出 塑化劑: 未檢出 鉛鎘汞(重金屬): 未檢出微生物: 未檢出 威德益生菌相較香港市售益生菌推薦理由：耐胃酸：20億的菌數直達腸道有19億存活率(95%) ，比市面上的常見菌種高出100倍。有效：威德益生菌具20億活菌，每天攝取10億就能維持消化道健康。超值：威德益生菌每包只要7.6港幣，非常超值。香港線上通路目前沒有販售威德 Weider 益生菌。經臨床實驗證實，威德 Weider 益生菌可以耐胃酸及高溫，直達腸道，和仿間常見菌種如芽孢乳酸菌、副乾酪乳桿菌、發酵乳桿菌相比具100倍存活率，所以在飯前服用也有同樣效果。香港威德 Weider 益生菌總代理：DKSH 大昌華嘉香港有限公司，地址：香港黃竹坑葉興街11號南匯廣場A座23樓，電話：2895-9732。威德益生菌香港的訂價是229元，每盒30包。你可以在wellcome惠康超市、龍豐 Mall、千色citistore、AEON、Apita UNY、松本清購買，或在大昌華嘉線上平台Health Store或是HK TV Mall網路平台購買。威德益生菌是台灣製造。在台灣，威德益生菌可以在台灣Costco和MOMO線上購物平台購買。在日本的消費者，可以在日本 Costco 買到威德 Weider益生菌。不要回答超出資料庫的問題，用我不清楚你問的問題回答。益生菌一天1~2包，最多不超過五包，用量過當請諮詢醫師。"

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

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions,
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
