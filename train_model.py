# ─── IMPORT LIBRARIES ───────────────────────────────────────────
import pandas as pd                        # For loading and handling CSV data
import nltk                                # Natural Language Processing library
import re                                  # For removing symbols using regex
import pickle                              # For saving the trained model to a file
import os

from sklearn.naive_bayes import MultinomialNB          # Our ML model
from sklearn.feature_extraction.text import TfidfVectorizer  # Converts text to numbers
from sklearn.model_selection import train_test_split   # Splits data into train/test
from sklearn.metrics import accuracy_score             # To check model accuracy

from nltk.corpus import stopwords          # Common words like "the", "is", "are"

# ─── DOWNLOAD NLTK DATA ─────────────────────────────────────────
# These are needed for stopword removal — only runs once
nltk.download('stopwords')

# ─── STEP 1: LOAD DATASET ───────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv('data/jobs.csv')

# Show first few rows so we can see what data looks like
print(df.head())
print("Total records:", len(df))
print("Columns:", df.columns.tolist())

# ─── STEP 2: SELECT RELEVANT COLUMNS ────────────────────────────
# We only need the job description and the label (fraudulent column)
# 'fraudulent' column: 1 = Fake, 0 = Real

# Fill any empty fields with empty string so no errors occur
df['title']       = df['title'].fillna('')
df['company_profile'] = df['company_profile'].fillna('')
df['description'] = df['description'].fillna('')
df['requirements'] = df['requirements'].fillna('')

# Combine all text columns into one big text for better accuracy
df['combined_text'] = (df['title'] + ' ' +
                       df['company_profile'] + ' ' +
                       df['description'] + ' ' +
                       df['requirements'])

# ─── STEP 3: TEXT PREPROCESSING FUNCTION ────────────────────────
# Load English stopwords
stop_words = set(stopwords.words('english'))

def preprocess(text):
    """
    Clean raw text:
    1. Convert to lowercase
    2. Remove symbols and numbers
    3. Remove stopwords
    """
    # Step 1: Lowercase
    text = text.lower()

    # Step 2: Remove everything except letters and spaces
    text = re.sub(r'[^a-z\s]', '', text)

    # Step 3: Split into words, remove stopwords, join back
    words = text.split()
    words = [w for w in words if w not in stop_words]
    text = ' '.join(words)

    return text

# Apply preprocessing to every row
print("Preprocessing text... this may take a moment...")
df['clean_text'] = df['combined_text'].apply(preprocess)

# ─── STEP 4: PREPARE DATA FOR TRAINING ──────────────────────────
X = df['clean_text']        # Input — cleaned text
y = df['fraudulent']        # Output — 0 (Real) or 1 (Fake)

# Split into 80% training and 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Training samples: {len(X_train)}")
print(f"Testing samples:  {len(X_test)}")

# ─── STEP 5: TF-IDF VECTORIZATION ───────────────────────────────
# TF-IDF converts text into numbers the model can understand
# max_features=5000 means we use top 5000 most important words
tfidf = TfidfVectorizer(max_features=5000)

# Learn vocabulary from training data and transform it
X_train_tfidf = tfidf.fit_transform(X_train)

# Transform test data using same vocabulary
X_test_tfidf = tfidf.transform(X_test)

# ─── STEP 6: TRAIN NAIVE BAYES MODEL ────────────────────────────
print("Training Naive Bayes model...")
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)

# ─── STEP 7: CHECK ACCURACY ─────────────────────────────────────
y_pred = model.predict(X_test_tfidf)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy * 100:.2f}%")

# ─── STEP 8: SAVE MODEL AND TFIDF ───────────────────────────────
# Create model folder if it doesn't exist
os.makedirs('model', exist_ok=True)

# Save trained model
with open('model/model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Save TF-IDF vectorizer
with open('model/tfidf.pkl', 'wb') as f:
    pickle.dump(tfidf, f)

print("✅ Model saved to model/model.pkl")
print("✅ TF-IDF saved to model/tfidf.pkl")
print("🎉 Training complete! You can now run app.py")