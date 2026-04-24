from flask import Flask, render_template, request, jsonify
import joblib
import re
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = joblib.load(os.path.join(BASE_DIR, 'spam_model.pkl'))
tfidf = joblib.load(os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl'))
THRESHOLD = joblib.load(os.path.join(BASE_DIR, 'threshold.pkl'))

def clean_text(text):
    text = re.sub(r'^Subject:\s*', '', str(text).lower())
    text = re.sub(r'\W', ' ', text)
    return ' '.join(text.split())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json(silent=True) or {}
        text = data.get('text', '')

        if not text.strip():
            return jsonify({'error': 'No text provided'}), 400

        cleaned = clean_text(text)
        vec = tfidf.transform([cleaned])
        prob_spam = model.predict_proba(vec)[0][1]

        is_spam = bool(prob_spam >= THRESHOLD)
        confidence = float(prob_spam if is_spam else 1 - prob_spam)

        return jsonify({
            'prediction': 'Spam' if is_spam else 'Ham',
            'confidence': round(confidence * 100, 2)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)