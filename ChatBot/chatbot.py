import json
import random
import re
import wikipedia

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -------- OPTIONAL AI --------
try:
    import openai
    openai.api_key = "YOUR_API_KEY"   # 🔑 Put your API key here
    AI_ENABLED = True
except:
    AI_ENABLED = False


class ChatBot:
    def __init__(self):
        with open("intents.json") as file:
            self.data = json.load(file)

        self.patterns = []
        self.tags = []

        # Collect patterns for ML
        for tag, intent in self.data.items():
            for pattern in intent["patterns"]:
                self.patterns.append(pattern.lower())
                self.tags.append(tag)

        # Train TF-IDF
        self.vectorizer = TfidfVectorizer()
        self.pattern_vectors = self.vectorizer.fit_transform(self.patterns)

    # -------- CLEAN INPUT --------
    def preprocess(self, text):
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    # -------- MAIN RESPONSE --------
    def get_response(self, user_input):

        clean_input = self.preprocess(user_input)
        words = clean_input.split()

        # -------- 1. TF-IDF MATCH --------
        user_vec = self.vectorizer.transform([clean_input])
        similarity = cosine_similarity(user_vec, self.pattern_vectors)

        best_match_index = similarity.argmax()
        confidence = similarity[0][best_match_index]
        best_tag = self.tags[best_match_index]

        # -------- 2. KEYWORD BOOST (LINKED INTENTS) --------
        keyword_score = 0

        for tag, intent in self.data.items():
            for keyword in intent.get("keywords", []):
                if keyword in words:
                    if tag == best_tag:
                        keyword_score += 0.2   # boost same intent

        confidence += keyword_score

        # -------- DEBUG --------
        print("Input:", user_input)
        print("Predicted Intent:", best_tag)
        print("Confidence:", round(confidence, 2))

        # -------- 3. STRONG INTENT --------
        if confidence > 0.65:
            return random.choice(self.data[best_tag]["responses"])

        # -------- 4. MEDIUM CONFIDENCE --------
        if 0.4 < confidence <= 0.65:
            return "🤔 I'm not fully sure. Can you rephrase?"

        # -------- 5. WIKIPEDIA --------
        try:
            summary = wikipedia.summary(user_input, sentences=2)
            return summary
        except:
            pass

        # -------- 6. AI RESPONSE --------
      

      
    