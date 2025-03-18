"""
Prompt:

Write a Streamlit app that generates social media posts from MongoDB articles using the DeepSeek framework and the DeepThink R1 model. The app should:

- Load the model efficiently to improve performance.
- Display articles from MongoDB in a dropdown menu.
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

# Set Streamlit Page Configuration (Moved to the top)
st.set_page_config(page_title="Generate Social Media Posts", page_icon='📱')

# MongoDB Connection
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
        temperature=0.07
    )

# Initialize model at startup
llm = load_model()

# Function to get response from LLaMA 2 model
def getLLamaresponse(input_text, platform, tone):
    template = """
       Generate a compelling social media post for {platform} with a {tone} tone based on the following article:

       {input_text}

       The post should:
       - Start with a strong hook.
       - Use clear and engaging language.
       - Include relevant hashtags.
       - Add an emoji or two if appropriate.
       - End with a call to action suitable for {platform}.

       Post:
     """
    
    prompt = PromptTemplate(
        input_variables=["platform", "tone", "input_text"],
        template=template
    )
    
    response = llm(prompt.format(platform=platform, tone=tone, input_text=input_text))
    return response

st.header("Generate Social Media Posts 📱")

# Display articles from MongoDB in a dropdown
articles = fetch_articles()
article_options = [f"{a['headline']} - {a['summary']}" for a in articles]
selected_article = st.selectbox("Select an article:", article_options)

col1, col2 = st.columns([5, 5])

with col1:
    platform = st.selectbox('Select Platform', ('Twitter', 'LinkedIn', 'Instagram', 'Facebook'))

with col2:
    tone = st.selectbox('Select Tone', ('Professional', 'Casual', 'Funny', 'Inspirational'))

submit = st.button("Generate Post")

if submit:
    if not selected_article:
        st.warning("Please select an article to generate a post.")
    else:
        with st.spinner("Generating post..."):
            st.write(getLLamaresponse(selected_article, platform, tone))
