"""
 Prompt:
 
 Write a Streamlit app that generates social media posts from MongoDB articles using the DeepSeek framework and the DeepThink R1 model. The app should:
 
 - Load the model efficiently to improve performance.
 - Display articles from MongoDB in a dropdown menu.
 - Add Sentiment Analysis to analyze the sentiment of generated posts
 - Allow users to select a platform (Twitter, LinkedIn, Instagram, Facebook) and a tone (Professional, Casual, Funny, Inspirational).
 - Use a well-structured prompt template that ensures generated posts:
 - Start with a strong hook.
 - Use clear and engaging language.
 - Include relevant hashtags.
 - Add appropriate emojis.
 - End with a strong call to action.
 
 Ensure efficient caching for both model loading and MongoDB queries to enhance performance."""
 

import streamlit as st
from langchain.prompts import PromptTemplate
from ctransformers import AutoModelForCausalLM
from pymongo import MongoClient
import pandas as pd
from textblob import TextBlob  # For Sentiment Analysis

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

# Load the model once during app startup
@st.cache_resource
def load_model():
    return AutoModelForCausalLM.from_pretrained(
        "E:/Sem-3/Capstone Project/llama-2-7b-chat.ggmlv3.q8_0.bin",
        model_type='llama',
        max_new_tokens=100,
        temperature=0.09,
        top_p=0.95,  # 🔥 Higher value for diverse yet focused text
        top_k=50     # 🔥 Limits vocabulary to improve coherence
    )

# Initialize model at startup
llm = load_model()

# Function to get response from LLaMA 2 model
def getLLamaresponse(input_text, platform, tone):
    template = """
       🎯 *Attention-grabbing post for {platform} with a {tone} tone:*

       📰 **Article Summary:** 
       {input_text}

       📢 **Post Structure:** 
       1️⃣ Start with an intriguing hook (e.g., "Did you know...?")  
       2️⃣ Follow with a concise yet impactful message  
       3️⃣ Include relevant hashtags (#News, #Trending, #MustRead)  
       4️⃣ Add an emoji or two if appropriate  
       5️⃣ End with a strong call to action (e.g., "Share your thoughts!")  

       🚀 **Generated Post:** 
     """
    
    prompt = PromptTemplate(
        input_variables=["platform", "tone", "input_text"],
        template=template
    )
    
    response = llm(prompt.format(platform=platform, tone=tone, input_text=input_text))
    return response

# Function to analyze sentiment
def analyze_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive 😊"
    elif analysis.sentiment.polarity < 0:
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
            # Generate post using LLaMA 2 model
            post = getLLamaresponse(selected_article_text, platform, tone)
            st.write(post)  # Display the generated post

            # Analyze sentiment of the generated post
            sentiment = analyze_sentiment(post)
            st.success(f"Sentiment: {sentiment}")  # 🔥 Display Sentiment