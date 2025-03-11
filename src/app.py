"""
This code is designed to generate social media posts based on a given article using the LLaMA 2 model. It leverages 
the ctransformers library to load the LLaMA 2 model locally and uses langchain for prompt engineering. The user can 
input an article, select a platform (e.g., Twitter, LinkedIn), and choose a tone (e.g., Professional, Casual). 
The app then generates a social media post tailored to the selected platform and tone."""

# LLM Framework: DeepSeek
# Model: DeepThink R1

import streamlit as st
from langchain.prompts import PromptTemplate
from ctransformers import AutoModelForCausalLM

# Function to get response from LLaMA 2 model
def getLLamaresponse(input_text, platform, tone):
    llm = AutoModelForCausalLM.from_pretrained(
        "E:/Sem-3/Capstone Project/llama-2-7b-chat.ggmlv3.q8_0.bin",
        model_type='llama',
        max_new_tokens=100,
        temperature=0.03
    )
    
    template = """
        Generate a social media post for {platform} with a {tone} tone based on the following article:
        
        {input_text}
        
        Post:
    """
    
    prompt = PromptTemplate(
        input_variables=["platform", "tone", "input_text"],
        template=template
    )
    
    response = llm(prompt.format(platform=platform, tone=tone, input_text=input_text))
    return response

st.set_page_config(page_title="Generate Social Media Posts", page_icon='📱')

st.header("Generate Social Media Posts 📱")

input_text = st.text_area("Paste your article here:", height=200)

col1, col2 = st.columns([5, 5])

with col1:
    platform = st.selectbox('Select Platform', ('Twitter', 'LinkedIn', 'Instagram', 'Facebook'))

with col2:
    tone = st.selectbox('Select Tone', ('Professional', 'Casual', 'Funny', 'Inspirational'))

submit = st.button("Generate Post")

if submit:
    if input_text.strip() == "":
        st.warning("Please enter an article to generate a post.")
    else:
        with st.spinner("Generating post..."):
            st.write(getLLamaresponse(input_text, platform, tone))