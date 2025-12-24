import os
import google.generativeai as genai # pip install google-generativeai
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Gemini Ayarları
genai.configure(api_key="AIzaSyBvF1PRBsBIIN4oaIAqtn_Q-1JL5Zje4wY")
model = genai.GenerativeModel('gemini-2.5-flash')

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def researcher_agent(user_query):
    # 1. Arama terimi üret
    search_prompt = f"Soru: {user_query}. Bu soruyu internette aramak için en iyi anahtar kelimeyi tek satır yaz."
    search_term = model.generate_content(search_prompt).text.strip()
    
    print(f"--- Aranıyor: {search_term} ---")
    
    # 2. Tavily Araması
    results = tavily.search(query=search_term, max_results=3)
    context = "\n".join([r['content'] for r in results['results']])
    
    # 3. Final Rapor
    final_prompt = f"Bilgiler: {context}\nSoru: {user_query}\nProfesyonel bir rapor hazırla."
    final_report = model.generate_content(final_prompt).text
    
    return final_report

if __name__ == "__main__":
    print(researcher_agent("2025 AI trendleri"))