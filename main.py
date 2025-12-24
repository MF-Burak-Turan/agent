import streamlit as st
import time
# Burada fonksiyon ismini 'researcher_agent' olarak güncelliyoruz
from agent_logic import researcher_agent

st.set_page_config(
    page_title="Gemini AI Researcher",
    page_icon="🔍",
    layout="centered"
)
st.markdown("""
Bu agent, internete bağlanarak gerçek zamanlı araştırma yapar ve bilgileri sentezler.
* **Beyin:** Google Gemini 2.5 Flash
* **Arama:** Tavily Search Engine
""")

# Kullanıcı Girişi
query = st.text_input("Araştırmak istediğiniz konu:", placeholder="Örn: 2025'in en popüler programlama dilleri")

if st.button("Araştırmayı Başlat", use_container_width=True):
    if query:
        # Görsel bir ilerleme çubuğu ve spinner
        with st.spinner("Agent interneti tarıyor ve rapor hazırlıyor..."):
            try:
                start_time = time.time()
                
                # Agent'ı çalıştırıyoruz
                report = researcher_agent(query)
                
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                st.success(f"Araştırma {duration} saniyede tamamlandı!")
                
                # Sonucu yazdır
                st.markdown("---")
                st.markdown("### 📊 Araştırma Sonucu")
                st.markdown(report)
                
                # İndirme butonu (Opsiyonel ama şık durur)
                st.download_button(
                    label="Raporu İndir (.txt)",
                    data=report,
                    file_name="arastirma_raporu.txt",
                    mime="text/plain"
                )
                
            except Exception as e:
                st.error(f"Bir hata oluştu: {e}")
    else:
        st.warning("Lütfen bir araştırma konusu girin!")

# Footer
st.markdown("---")
st.caption("AI Agent Hackathon 2025 - Geliştirici: Burak")
