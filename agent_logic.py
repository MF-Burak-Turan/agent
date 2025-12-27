import os
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
    console = Console()
    
    soru = input("\n Araştırmak istediğiniz konuyu girin: ")
    
    with console.status("[bold green]Araştırılıyor...", spinner="earth"):
        result = researcher_agent(soru)
    
    console.print("\n[bold cyan]🚀 ARAŞTIRMA TAMAMLANDI[/bold cyan]\n")

    table = Table(title="Agent Bilgileri", show_header=True, header_style="bold magenta")
    table.add_column("Takım", style="dim")
    table.add_column("Görev ID")
    table.add_column("İşlem Süresi")
    table.add_row(result["team_name"], str(result["task_id"]), result["execution_time"])
    console.print(table)

    output = result["result_output"]
    summary_text = f"[bold yellow]Özet:[/bold yellow]\n{output['summary']}\n\n"
    data_text = f"[bold green]Detaylı Veri:[/bold green]\n{output['data']}"
    
    console.print(Panel(
        summary_text + data_text,
        title="[bold white]Sonuç Çıktısı[/bold white]",
        border_style="blue",
        expand=False,
        padding=(1, 2)
    ))