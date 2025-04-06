""" I provided ChatGPT with my previous LLM app code and asked improvements to enhance my prompt engineering for generating better and more creative social media posts.
 Specifically, I asked for:

--> Improved Prompt Engineering: The new prompt should generate posts with appropriate hashtags and emojis that align with the article's content, rather than relying 
on predefined options.

--> Enhanced Sentiment Analysis: The sentiment analysis should more accurately reflect the emotional tone of the generated posts based on the article's context."""



import streamlit as st
from langchain.prompts import PromptTemplate
from pymongo import MongoClient
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer  # Improved Sentiment Analysis
import requests  # For Hugging Face API
import re  # For extracting hashtags

# Set Streamlit Page Configuration
st.set_page_config(page_title="Generate Social Media Posts", page_icon='📱')

# MongoDB Connection (Use environment variables or Streamlit secrets for production)
client = MongoClient("mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics")
db = client["news_database"]
collection = db["master_news"]

# Fetch articles from MongoDB
@st.cache_data
def fetch_articles():
    articles = collection.find({}, {"headline": 1, "summary": 1}).limit(20)
    return list(articles)

# Function to extract hashtags from text
def extract_hashtags(text, limit=5): # Limit to 5 hashtags by default
    words = re.findall(r'\b\w{4,}\b', text.lower())
    common_hashtags = [f"#{word}" for word in words if len(word) > 3][:limit]
    return ' '.join(common_hashtags) if common_hashtags else "#News #Update #Breaking"

# Function to get response from Hugging Face API
def getLLamaresponse(input_text, platform, tone):
    # Improved prompt template
    template = """
       🎯 *Attention-grabbing post for {platform} with a {tone} tone:*

       📰 **Article Summary:** 
       {input_text}

       📢 **Post Structure:** 
       1️⃣ Start with a creative hook (e.g., "Did you know...?", "Breaking news!", "Here's something you can't miss!")  
       2️⃣ Follow with a concise yet impactful message that highlights the key points of the article.  
       3️⃣ Include relevant hashtags: {hashtags}  
       4️⃣ Add appropriate emojis: {emojis}  
       5️⃣ End with a strong call to action (e.g., "What are your thoughts?", "Tag someone who needs to see this!", "Let's discuss below!")  

       🚀 **Generated Post:** 
     """

    prompt = PromptTemplate(
        input_variables=["platform", "tone", "input_text", "hashtags", "emojis"],
        template=template
    )

    # Generate dynamic hashtags and emojis based on content
    hashtags = extract_hashtags(input_text)
    emojis = "🔥📢🚨" if "breaking" in input_text.lower() else "📰📣📌"

    # Format the prompt
    formatted_prompt = prompt.format(
        platform=platform,
        tone=tone,
        input_text=input_text,
        hashtags=hashtags,
        emojis=emojis
    )

    # Hugging Face API endpoint and headers
    API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-2-7b-chat-hf"
    headers = {
        "Authorization": f"Bearer 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",
        "Content-Type": "application/json"
    }

    # Payload for the API request
    payload = {
        "inputs": formatted_prompt,
        "parameters": {
            "max_new_tokens": 150,  # Increased token limit for detailed posts
            "temperature": 0.7, # Lower temperature for more controlled output
            "top_p": 0.95, # Higher nucleus sampling probability
            "top_k": 50     # Higher top-k value for diverse output
        }
    }

    # Send request to Hugging Face API
    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        return f"Error: {response.status_code}, {response.text}"

# Improved Sentiment Analysis with VADER
def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)['compound']
    if sentiment_score > 0.2:
        return "Positive 😊"
    elif sentiment_score < -0.2:
        return "Negative 😞"
    else:
        return "Neutral 😐"

# Streamlit App
st.header("Generate Social Media Posts 📱")

# Fetch and display articles
articles = fetch_articles()
articles_df = pd.DataFrame(articles)

# Select article using a dropdown
st.subheader("Select an article:")
selected_article_index = st.selectbox(
    "Choose an article:",
    range(len(articles_df)),
    format_func=lambda x: articles_df.iloc[x]['headline']
)

# Extract selected article details
selected_article_text = f"{articles_df.iloc[selected_article_index]['headline']} - {articles_df.iloc[selected_article_index]['summary']}"

# Platform and Tone Selection
col1, col2 = st.columns([5, 5])
with col1:
    platform = st.selectbox('Select Platform', ('Twitter', 'LinkedIn', 'Instagram', 'Facebook'))
with col2:
    tone = st.selectbox('Select Tone', ('Professional', 'Casual', 'Funny', 'Inspirational'))

# Generate Post Button
submit = st.button("Generate Post")

if submit:
    if not selected_article_text:
        st.warning("Please select an article to generate a post.")
    else:
        with st.spinner("Generating post..."):
            # Generate post using Hugging Face API
            post = getLLamaresponse(selected_article_text, platform, tone)
            st.write(post)  # Display the generated post

            # Analyze sentiment of the generated post
            sentiment = analyze_sentiment(post)
            st.success(f"Sentiment: {sentiment}") # Display the sentiment
