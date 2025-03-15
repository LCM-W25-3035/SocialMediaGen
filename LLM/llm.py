
import streamlit as st
from pymongo import MongoClient
from transformers import pipeline
import os
import huggingface_hub

# Set your Hugging Face token (make sure it's a valid token with access to the model)
HF_TOKEN = "hf_vgOyjJ**********EkLIfbltneZLVcL"

# Login to Hugging Face inside the script
huggingface_hub.login(HF_TOKEN)

# Streamlit Page Config
st.set_page_config(page_title="Mistral News Post Generator", layout="wide")

# Connect to MongoDB
client = MongoClient("mongodb+srv://Govind:******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics") 
db = client["news_database"]
collection = db["master_news"]

# Use Hugging Face Inference API via pipeline
model_name = "mistralai/Mistral-7B-Instruct-v0.3"
generator = pipeline("text-generation", model=model_name, tokenizer=model_name, use_auth_token=HF_TOKEN)

def fetch_all_news():
    """Fetch all news articles from MongoDB"""
    news_list = list(collection.find({}, {"_id": 1, "headline": 1, "summary": 1}))
    return news_list

def generate_social_media_post(headline, summary):
    """Generate a social media post using Mistral model via Hugging Face Inference API"""
    prompt = f"Make a social media post from the provided data:\nHeadline: {headline}\nSummary: {summary}\n\nPost:"
    
    result = generator(prompt, max_length=100, num_return_sequences=1)
    return result[0]["generated_text"]

# Streamlit UI
st.title("Mistral News to Social Media Post Generator")
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
