from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 模拟存储数据
data_store = {
    "title": "ADAM",
    "name": "Timmy_Service_1",
    "time": "From 2024/6/2 16:30:12 TO 2024/6/2 16:36:39",
    "person_name": "Timmy",
    "organization": "Microsoft Digital Global",
    "total_score": 83.9,
    "audio_score": 78.6,
    "text_score": 88.5,
    "facial_score": 84.7,
    "ai_text1": "AI文本1",
    "ai_text2": "AI文本2",
    "ai_text3": "AI文本3",
    "charts": [
        "Customer_Emotion_Wave & Server_Emotion_Wave.jpg",
        "combined_sentiment_analysis.png",
        "emotion_distribution_combined.png"
    ]
}

@app.route('/')
def report():
    return render_template('report2.html', data=data_store)

@app.route('/update', methods=['POST'])
def update_data():
    new_data = request.json
    data_store.update(new_data)
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)
