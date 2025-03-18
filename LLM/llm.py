""" GPT PROMPTS
first prompt: I want to create a app which will take news data like summary and headline from mongo and use hugging face and llama to convert that news into social media post
last prompt:Getting error:
            Response Status Code: 415

            Response Text: Expected request with Content-Type: application/json

            Generated Social Media Post:
            Error: 415 - Expected request with Content-Type: application/json"""

import streamlit as st
from pymongo import MongoClient
import requests
import json
import os

# Set your Hugging Face API token
HF_TOKEN = "hf_epIuUP**********AKkUvdvam"

# Hugging Face Inference API endpoint
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{model_name}"

# Headers to pass with the request
headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json" 
}

# Streamlit Page Config
st.set_page_config(page_title="Mistral News Post Generator", layout="wide")

# Connect to MongoDB
client = MongoClient("mongodb+srv://Govind:******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics") 
db = client["news_database"]
collection = db["master_news"]

def fetch_all_news():
    """Fetch all news articles from MongoDB"""
    news_list = list(collection.find({}, {"_id": 1, "headline": 1, "summary": 1}))
    return news_list

def generate_social_media_post(headline, summary):
    """Generate a social media post using the Mistral model via Hugging Face Inference API"""
    prompt = f"Determine the sentiment (positive, negative, neutral) of this news.Generate a short social media post based on the sentiment:Positive**: Exciting, highlight good news. Negative**: Serious, sensitive, informative.Neutral**: Factual, engaging.Give me only one post based on sentiment type of the news. Include a catchy hook, key insight, emojis and relevant hashtags:Headline: {headline}\nSummary: {summary}\n\nPost:"
    
    # Sending a POST request to Hugging Face Inference API
    payload = json.dumps({"inputs": prompt})
    response = requests.post(API_URL, headers=headers, data=payload)
    
    # Debugging response
    st.write(f"Response Status Code: {response.status_code}")
    st.write(f"Response Text: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        return result[0]["generated_text"]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.title("🦙 Mistral News to Social Media Post Generator")
st.write("Select a news article and convert it into a social media post using Mistral.")

# Fetch all news
news_list = fetch_all_news()

if news_list:
    # Dropdown to select news
    selected_news = st.selectbox(
        "Select a news article:",
        news_list,
        format_func=lambda x: x["headline"]
    )

    # Display selected news
    st.subheader("Selected News:")
    st.write(f"**Headline:** {selected_news['headline']}")
    st.write(f"**Summary:** {selected_news['summary']}")

    if st.button("Generate Social Media Post"):
        with st.spinner("Generating..."):
            social_post = generate_social_media_post(selected_news["headline"], selected_news["summary"])
        st.subheader("Generated Social Media Post:")
        st.success(social_post)
else:
    st.warning("No news found in MongoDB.")
