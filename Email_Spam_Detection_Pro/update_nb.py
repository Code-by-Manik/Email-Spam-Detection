import json

with open('sul_final_evaluation.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = ''.join(cell['source'])
        if 'if best_model_name=="Naive Bayes":' in source:
            new_source = '''if best_model_name=="Logistic Regression":

    feature_names=np.array(tfidf.get_feature_names_out())

    # In Logistic Regression, feature importance is determined by coefficients
    coefs = best_model.coef_[0]
    sorted_idx = np.argsort(coefs)

    # Lowest (negative) coefficients predict Ham
    ham_idx = sorted_idx[:15]
    # Highest (positive) coefficients predict Spam
    spam_idx = sorted_idx[-15:]

    spam_words = feature_names[spam_idx]
    ham_words = feature_names[ham_idx]
    
    spam_importances = coefs[spam_idx]
    ham_importances = abs(coefs[ham_idx])

    plt.figure(figsize=(10, 6))
    plt.barh(spam_words, spam_importances)
    plt.title("Top Spam Words")
    plt.xlabel("Coefficient Strength")
    plt.show()

    plt.figure(figsize=(10,6))
    plt.barh(ham_words, ham_importances)
    plt.title("Top Ham Words")
    plt.xlabel("Coefficient Strength (Absolute)")
    plt.show()
'''
            lines = new_source.split('\n')
            new_lines = [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines[-1] else [line + '\n' for line in lines[:-1]]
            cell['source'] = new_lines

with open('sul_final_evaluation.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
