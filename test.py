# streamlit_toplama.py
import streamlit as st

st.title("➕ İki Sayı Toplama Hesaplayıcısı")

# Kullanıcıdan giriş almak için Streamlit widget'ları kullanıyoruz
sayi1 = st.number_input("İlk sayıyı girin", value=0.0)
sayi2 = st.number_input("İkinci sayıyı girin", value=0.0)

# Bir düğme ekleyerek toplama işlemini tetikliyoruz
if st.button("Topla"):
    toplam = sayi1 + sayi2
    # Sonucu göstermek için Streamlit fonksiyonu kullanıyoruz
    st.success(f"İki sayının toplamı: {toplam}")

st.markdown("---")
st.info("Bu basit hesaplayıcı, komut satırı uygulamasının Streamlit'e nasıl adapte edildiğini gösterir.")
