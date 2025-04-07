# 📰 SocialMediaGen

**News Analytics and Social Media Post Generator**  
A smart, AI-driven platform that collects trending news, classifies it in real time, and generates tone-aware, platform-ready social media posts reducing manual effort and maximizing engagement.

---

## 🔗 Project Links

- **Project Board**: [GitHub Project Board](https://github.com/users/Akash1820/projects/3)
- **Topic Research**: [Google Doc](https://docs.google.com/document/d/1D-LyJIgpkWVJfpK2zqVApjrac3kLK9V9ZtJ0Oea3AWQ/edit?tab=t.0)
- **Documentation**: [Architecture & Components](https://docs.google.com/document/d/1GJD3quzE5uT2W5Tc6nIscqCOjW9xEHw037UtIlK0W24/edit?tab=t.0)
- **Weekly Check-ins**: [Progress Tracker](https://docs.google.com/document/d/1h99VUvllSyL6-47WVe66zkC2z7ib8frbYIsOBPSmdSc/edit?tab=t.0)

---

## 🧩 Key Features

- 🔄 **Real-Time News Aggregation**: Scrapes and streams news via Kafka
- 🧠 **Zero-Shot Topic Classification**: Uses DeBERTa to auto-label articles
- 💬 **Sentiment-Aware Post Generation**: Mistral 7B creates engaging content based on tone
- ⚙️ **Automated Workflow Orchestration**: Built using Apache Airflow
- 🔍 **Elasticsearch Integration**: For high-speed querying and filtering
- 📊 **Dashboard**: Streamlit + Django-based interface for content review and management

---

## 🛠️ Tech Stack

| Layer                  | Tools Used                                               |
|------------------------|----------------------------------------------------------|
| **Ingestion**          | BeautifulSoup / Selenium / APIs, Kafka Producers         |
| **Preprocessing**      | Python, Hugging Face Transformers (Zero-Shot)            |
| **Storage**            | MongoDB (raw/cleaned), Elasticsearch (indexed results)   |
| **Post Generation**    | Mistral 7B (LLM for content creation)                    |
| **Serving**            | Django (frontend API), Streamlit (visual dashboard)      |
| **Orchestration**      | Apache Airflow                                           |
| **Deployment**         | Docker, Microsoft Azure                                  |

---

## 🔄 Data Pipeline

News Scraper → Kafka → Airflow DAG → Zero-Shot Classification → NLP Enrichment → MongoDB & Elasticsearch → Mistral Post Generator → Django/Streamlit UI


---

## 📈 Insights

- 🔥 Peak scraping efficiency at 9 AM & 2 PM
- 🗳️ Politics showed the highest audience engagement
- 💼 Business content had low traction — needs optimization

---

## 🧪 AI Models

- **Zero-Shot Classifier** (`MoritzLaurer/deberta-v3-large-zeroshot-v1`)
  - Classifies news articles into predefined topics with no additional training
- **Mistral 7B**
  - Generates creative, tone-aligned, platform-specific posts
  - Uses prompt engineering and sampling techniques for coherence

---

## 🚀 Getting Started

1. Clone the repository  
   `git clone https://github.com/LCM-W25-3035/SocialMediaGen.git`
2. Install dependencies  
   `pip install -r requirements.txt`
3. Run Docker containers  
   `docker-compose up`
4. Access:
   - Streamlit: `localhost:8501`
   - Django: `localhost:8000`

---

## 📄 License

This project is part of **LCM W25-3035 Capstone** — for academic demonstration purposes only.

---

## 👩‍💻 Team Members

| Role | Name |
|------|------|
| Frontend & UI | Govind |
| Data Ingestion & Architecture | Akash Kumar |
| Kafka & Elasticsearch | Aniket |
| Topic Classification (ZSC) | Muskan |
| NLP Enrichment | Ronakkumar Chavda |
| Database Management | Ashish |
| Dashboard & Visuals | Jashan |
| Workflow Scheduling | Shlok |
| Deployment | Devansh |

---



