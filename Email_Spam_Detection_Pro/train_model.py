import pandas as pd
import numpy as np
import re
import joblib
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_curve, f1_score, precision_score, recall_score

warnings.filterwarnings('ignore')

def clean_text(text):
    text = re.sub(r'^Subject:\s*', '', str(text).lower())
    text = re.sub(r'\W', ' ', text)
    return ' '.join(text.split())

def main():
    print("Loading data...")
    try:
        df = pd.read_csv('emails.csv')
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
    except Exception as e:
        print(f"Error loading emails.csv: {e}")
        return

    print("Cleaning text...")
    df['text'] = df['text'].apply(clean_text)



    print("Vectorizing text...")
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english', ngram_range=(1,2))
    X = tfidf.fit_transform(df['text'])
    y = df['spam'].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("Training Model (same 80/20 split as notebook)...")
    model = LogisticRegression(solver="liblinear", class_weight="balanced")
    model.fit(X_train, y_train)

    probs = model.predict_proba(X_test)[:, 1]
    precision, recall, thresholds = precision_recall_curve(y_test, probs)
    
    f1_scores = 2 * (precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-10)
    
    # Find the baseline probability of an all-zero vector (an unseen word)
    import scipy.sparse as sp
    empty_vec = sp.csr_matrix((1, X_train.shape[1]))
    baseline_prob = model.predict_proba(empty_vec)[0, 1]

    valid_indices = np.where(thresholds > baseline_prob)[0]
    
    if len(valid_indices) > 0:
        best_idx = valid_indices[np.argmax(f1_scores[valid_indices])]
        best_threshold = float(thresholds[best_idx])
    else:
        best_idx = np.argmax(f1_scores)
        best_threshold = float(thresholds[best_idx])

    y_pred = (probs >= best_threshold).astype(int)
    final_prec = precision_score(y_test, y_pred)
    final_rec = recall_score(y_test, y_pred)
    final_f1 = f1_score(y_test, y_pred)

    print(f"Baseline unseen probability:                {baseline_prob:.4f}")
    print(f"Optimal threshold (> baseline):             {best_threshold:.4f}")
    print(f"Precision at optimal threshold:             {final_prec:.4f}")
    print(f"Recall at optimal threshold:                {final_rec:.4f}")
    print(f"F1-Score at optimal threshold:              {final_f1:.4f}")

    print("Saving model, vectorizer, and threshold...")
    joblib.dump(model, 'spam_model.pkl')
    joblib.dump(tfidf, 'tfidf_vectorizer.pkl')
    joblib.dump(best_threshold, 'threshold.pkl')

    print("Training complete! Files saved.")

if __name__ == "__main__":
    main()
