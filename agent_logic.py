import os
import sys
import json
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv
from rich.console import Console 
from rich.panel import Panel
from rich.json import JSON
from rich.table import Table

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def search_serper(query):
    url = "https://google.serper.dev/search"
    # 2025 verilerini zorlamak için sorguya yıl ekliyoruz
    payload = {"q": f"{query} 2025", "gl": "tr", "hl": "tr"}
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        results = response.json()
        search_context = ""
        
        # Sadece organik sonuçları değil, varsa 'answerBox' (direkt cevap) kısmını da alalım
        if "answerBox" in results:
            search_context += f"Direkt Cevap: {results['answerBox'].get('answer') or results['answerBox'].get('snippet')}\n"

        if "organic" in results:
            for result in results["organic"][:5]: 
                search_context += f"Başlık: {result['title']}\nÖzet: {result['snippet']}\nLink: {result.get('link')}\n---\n"
        
        return search_context if search_context else "İnternet üzerinde güncel sonuç bulunamadı."
    except Exception as e:
        return f"Arama hatası oluştu: {str(e)}"

def researcher_agent(user_query):
    start_time = time.time()

    model_flash = genai.GenerativeModel('gemini-2.5-flash')
    prompt_1 = f"Soru: {user_query}. Bu soruyu en güncel verilerle yanıtlamak için Google arama terimi üret (Sadece tek satır)."
    search_term = model_flash.generate_content(prompt_1).text.strip()
    
    context = search_serper(search_term)

    model_json = genai.GenerativeModel(
        'gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )
    
    prompt_2 = f"""
    KULLANICI SORUSU: {user_query}
    ARAMA VERİLERİ:
    {context}
    
    GÖREV: Yukarıdaki verileri kullanarak soruyu yanıtla. Eğer link varsa mutlaka 'data' kısmında belirt. 
    Yanıtı şu JSON şemasında ver:
    {{
      "summary": "1-2 cümlelik teknik özet",
      "data": "Linkleri ve detaylı fiyat/konum bilgilerini içeren araştırma sonucu"
    }}
    """
    
    response = model_json.generate_content(prompt_2)
    
    try:
        raw_result = json.loads(response.text)
    except:
        raw_result = {"summary": "Hata", "data": "JSON ayrıştırma hatası."}

    # Zaman hesaplama
    elapsed = time.time() - start_time
    execution_time_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"

    return {
        "team_name": "In Frames",
        "task_id": 1,
        "input_prompts": [prompt_1, prompt_2],
        "execution_time": execution_time_str,
        "result_output": raw_result
    }

if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    soru = input("Araştırma konusu girin: ")
    result = researcher_agent(soru)
    
    json_output = json.dumps(result, indent=4, ensure_ascii=False)
    
    final_view = json_output.replace("\\n", "\n")
    
    print("\n" + "="*50)
    print(final_view)
    print("="*50)