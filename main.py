import streamlit as st
import time
from agent_logic import researcher_agent

st.set_page_config(
    page_title="Gemini AI Researcher",
    page_icon="🔍",
    layout="centered"
)
st.markdown("""
Bu agent, internete bağlanarak gerçek zamanlı araştırma yapar ve bilgileri sentezler.
* **Beyin:** Google Gemini 2.5 Flash
* **Arama:** Serper Search Engine
""")

# Kullanıcı Girişi
query = st.text_input("Araştırmak istediğiniz konu:", placeholder="Örn: 2025'in en popüler programlama dilleri")

if st.button("Araştırmayı Başlat", use_container_width=True):
    if query:
        with st.spinner("Agent interneti tarıyor ve rapor hazırlıyor..."):
            try:
                start_time = time.time()
                
                # Agent'ı çalıştırıyoruz
                report = researcher_agent(query)
                
                end_time = time.time()
                duration = round(end_time - start_time, 2)
                
                st.success(f"Araştırma {duration} saniyede tamamlandı!")
                
                st.markdown("---")
                st.markdown("### 📊 Araştırma Sonucu")
                st.markdown(report)
                
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


st.markdown("---")