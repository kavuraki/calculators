# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import streamlit as st
import math

# -----------------------------------------------------------------------------
# Çekirdek Faiz Hesaplama Fonksiyonu (önceki koddan alındı)
# -----------------------------------------------------------------------------
def yillik_vadeler_arasi_faiz_hesapla(
    kisa_vade_faiz_orani: float,
    kisa_vade_gun: int,
    uzun_vade_faiz_orani: float,
    uzun_vade_gun: int,
    yil_gun_sayisi: int = 365
) -> tuple[float | None, str | None]: # Dönüş tipi güncellendi: (faiz_orani, hata_mesaji)
    """
    İki farklı vade ve bu vadelere ait yıllık faiz oranları verildiğinde,
    bu iki vade arasında kalan dönem için yıllık forward faiz oranını hesaplar.
    """
    hata_mesaji = None
    if not (0 < kisa_vade_gun < uzun_vade_gun):
        hata_mesaji = "Hata: Gün girdileri mantıksız. 'Kısa Vade (Gün)' > 0 ve 'Kısa Vade (Gün)' < 'Uzun Vade (Gün)' olmalıdır."
        return None, hata_mesaji
    
    if kisa_vade_faiz_orani < -1 or uzun_vade_faiz_orani < -1:
        # %-100'den düşük faiz oranı mantıksız olacağından basit bir kontrol.
        # Streamlit number_input min_value ile de bu kontrol sağlanabilir.
        pass


    kisa_vade_yil = kisa_vade_gun / yil_gun_sayisi
    uzun_vade_yil = uzun_vade_gun / yil_gun_sayisi

    uzun_vade_sonu_deger = 1 + (uzun_vade_faiz_orani * uzun_vade_yil)
    kisa_vade_sonu_deger = 1 + (kisa_vade_faiz_orani * kisa_vade_yil)

    ara_donem_yil = (uzun_vade_gun - kisa_vade_gun) / yil_gun_sayisi

    if ara_donem_yil <= 0: # Bu durum ilk kontrolde yakalanmalı
        hata_mesaji = "Hata: Ara dönem süresi sıfır veya negatif olamaz (bu durum ilk kontrolde yakalanmalıydı)."
        return None, hata_mesaji

    if abs(kisa_vade_sonu_deger) < 1e-9: # Neredeyse sıfırsa
        # Bu durum, kisa_vade_faiz_orani = -1 ve kisa_vade_yil = 1 gibi durumlarda oluşur.
        hata_mesaji = "Hata: Kısa vade sonu değer sıfıra çok yakın veya sıfır. Bu, forward faiz hesaplamasında tanımsızlığa yol açar (Örn: Kısa vade faizi %-100 ve vade 1 yıl ise)."
        return None, hata_mesaji
    
    forward_faizi_yillik = ((uzun_vade_sonu_deger / kisa_vade_sonu_deger) - 1) / ara_donem_yil

    return forward_faizi_yillik, hata_mesaji

# -----------------------------------------------------------------------------
# Streamlit Uygulaması Arayüzü
# -----------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Forward Faiz Hesaplayıcı")

st.title("🏦 Vadeler Arası (Forward) Faiz Oranı Hesaplayıcı")
st.markdown("""
Bu uygulama, iki farklı vade için verilen yıllık basit faiz oranlarından yararlanarak,
bu iki vade arasında kalan dönem için yıllık **basit forward faiz oranını** ve ilgili
**günlük bileşik getirileri** hesaplar.
""")

# --- Girdi Alanları ---
st.sidebar.header("🗓️ Girdi Parametreleri")

# Yıl gün sayısı seçimi
yil_gun_sayisi_secenekleri = {
    "365 Gün (Standart)": 365,
    "360 Gün (Bazı Piyasalar)": 360,
    "366 Gün (Artık Yıl)": 366
}
secilen_yil_gun_str = st.sidebar.selectbox(
    "Yıl İçin Gün Sayısı Konvansiyonu:",
    options=list(yil_gun_sayisi_secenekleri.keys()),
    index=0 # Varsayılan olarak 365 gün
)
yil_gun_sayisi = yil_gun_sayisi_secenekleri[secilen_yil_gun_str]
st.sidebar.info(f"Hesaplamalarda 1 yıl = **{yil_gun_sayisi} gün** olarak alınacaktır.")


st.sidebar.subheader("1️⃣ Kısa Vade Bilgileri")
kv_faiz_orani_input = st.sidebar.number_input(
    "Yıllık Basit Faiz Oranı (%)",
    min_value=-100.0,  # Pratikte negatif faizler olabilir
    max_value=1000.0, # Makul bir üst sınır
    value=48.70,      # Örnek değer
    step=0.01,
    format="%.2f",
    key="kv_faiz"
)
kv_gun_input = st.sidebar.number_input(
    "Vade (Gün)",
    min_value=1,
    value=30,         # Örnek değer
    step=1,
    key="kv_gun"
)

st.sidebar.subheader("2️⃣ Uzun Vade Bilgileri")
uv_faiz_orani_input = st.sidebar.number_input(
    "Yıllık Basit Faiz Oranı (%)",
    min_value=-100.0,
    max_value=1000.0,
    value=46.60,      # Örnek değer
    step=0.01,
    format="%.2f",
    key="uv_faiz"
)
uv_gun_input = st.sidebar.number_input(
    "Vade (Gün)",
    min_value=1,
    value=93,         # Örnek değer
    step=1,
    key="uv_gun"
)

# Girdileri ondalık formata çevir
kisa_vade_faiz_orani = kv_faiz_orani_input / 100.0
kisa_vade_gun = int(kv_gun_input)
uzun_vade_faiz_orani = uv_faiz_orani_input / 100.0
uzun_vade_gun = int(uv_gun_input)

# --- Hesaplama ve Sonuçların Gösterimi ---
st.divider()
st.header("📊 Hesaplama Sonuçları")

if st.sidebar.button("🔄 Hesapla", type="primary", use_container_width=True):
    # Yıllık forward basit faiz oranını hesapla
    forward_basit_faiz_yillik, hata = yillik_vadeler_arasi_faiz_hesapla(
        kisa_vade_faiz_orani,
        kisa_vade_gun,
        uzun_vade_faiz_orani,
        uzun_vade_gun,
        yil_gun_sayisi
    )

    if hata:
        st.error(hata)
    elif forward_basit_faiz_yillik is not None:
        ara_donem_gun = uzun_vade_gun - kisa_vade_gun
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"➡️ Forward Dönem ({kisa_vade_gun}. - {uzun_vade_gun}. gün / {ara_donem_gun} gün)")
            st.metric(
                label="Hesaplanan Yıllık Basit Forward Faiz Oranı",
                value=f"{forward_basit_faiz_yillik*100:.4f}%"
            )

        # Günlük bileşik getirilerin hesaplanması
        results_container = st.container()
        results_container.subheader("🗓️ Günlük Bileşik Getiri Detayları")
        
        # 1. Kısa dönem için günlük bileşik getiri
        kisa_donem_toplam_getiri_faktoru = 1 + kisa_vade_faiz_orani * (kisa_vade_gun / yil_gun_sayisi)
        gunluk_bilesik_kisa_str = "Hesaplanamadı"
        if kisa_vade_gun > 0 and kisa_donem_toplam_getiri_faktoru >= 0:
            try:
                gunluk_bilesik_kisa = (kisa_donem_toplam_getiri_faktoru ** (1 / kisa_vade_gun)) - 1
                gunluk_bilesik_kisa_str = f"{gunluk_bilesik_kisa*100:.6f}%"
            except (ValueError, OverflowError): # Math domain error veya çok büyük/küçük sayılar
                 gunluk_bilesik_kisa_str = "Matematiksel Hata"
        
        with results_container:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Kısa Vade ({kisa_vade_gun} gün):**")
                st.info(f"Dönem Sonu Toplam Getiri Faktörü (Basit Faiz): {kisa_donem_toplam_getiri_faktoru:.6f}")
                st.success(f"Günlük Bileşik Getiri Oranı: {gunluk_bilesik_kisa_str}")

        # 2. Ara (forward) dönem için günlük bileşik getiri
        ara_donem_toplam_getiri_faktoru = 1 + forward_basit_faiz_yillik * (ara_donem_gun / yil_gun_sayisi)
        gunluk_bilesik_ara_str = "Hesaplanamadı"
        if ara_donem_gun > 0 and ara_donem_toplam_getiri_faktoru >= 0:
            try:
                gunluk_bilesik_ara = (ara_donem_toplam_getiri_faktoru ** (1 / ara_donem_gun)) - 1
                gunluk_bilesik_ara_str = f"{gunluk_bilesik_ara*100:.6f}%"
            except (ValueError, OverflowError):
                 gunluk_bilesik_ara_str = "Matematiksel Hata"

        with results_container:
            with c2:
                st.markdown(f"**Ara Dönem ({ara_donem_gun} gün):**")
                st.info(f"Dönem Sonu Toplam Getiri Faktörü (Basit Faiz): {ara_donem_toplam_getiri_faktoru:.6f}")
                st.success(f"Günlük Bileşik Getiri Oranı: {gunluk_bilesik_ara_str}")

        # Doğrulama
        st.divider()
        st.subheader("🔍 Doğrulama (Günlük Bileşik Getirilerle)")
        valid_calc_kisa = (kisa_vade_gun > 0 and kisa_donem_toplam_getiri_faktoru >= 0 and isinstance(gunluk_bilesik_kisa, float))
        valid_calc_ara = (ara_donem_gun > 0 and ara_donem_toplam_getiri_faktoru >= 0 and isinstance(gunluk_bilesik_ara, float))

        if valid_calc_kisa and valid_calc_ara:
            bilesik_kisa_sonu_deger = (1 + gunluk_bilesik_kisa) ** kisa_vade_gun
            bilesik_uzun_sonu_deger = bilesik_kisa_sonu_deger * ((1 + gunluk_bilesik_ara) ** ara_donem_gun)
            uzun_vade_basit_faiz_sonu_deger = 1 + uzun_vade_faiz_orani * (uzun_vade_gun / yil_gun_sayisi)

            st.write(f"Kısa vade sonu değer (günlük bileşik ile): `{bilesik_kisa_sonu_deger:.8f}` (Basit ile: `{kisa_donem_toplam_getiri_faktoru:.8f}`)")
            st.write(f"Uzun vade sonu değer (günlük bileşikler ile): `{bilesik_uzun_sonu_deger:.8f}`")
            st.write(f"Uzun vade sonu değer (orijinal basit faiz ile): `{uzun_vade_basit_faiz_sonu_deger:.8f}`")

            if math.isclose(bilesik_uzun_sonu_deger, uzun_vade_basit_faiz_sonu_deger, rel_tol=1e-7): # Tolerans artırıldı
                st.success("✅ Doğrulama başarılı: İki yöntemle hesaplanan uzun vade sonu değerler eşleşiyor.")
            else:
                st.warning(f"⚠️ Doğrulama uyarısı: Değerler arasında küçük bir fark var (Fark: {abs(bilesik_uzun_sonu_deger - uzun_vade_basit_faiz_sonu_deger):.2e}). Bu, yuvarlama farklarından kaynaklanıyor olabilir.")

            # --- Grafik Ekleme ---
            st.subheader("📈 Günlük Bileşik Getiri Grafiği")

            # Grafik için veri hazırlama
            # 1. Kısa Vade Dönemi
            days_kv = list(range(kisa_vade_gun + 1)) # 0'dan kisa_vade_gun'e kadar
            returns_kv = [(1 + gunluk_bilesik_kisa)**d for d in days_kv]

            # 2. Forward Dönemi
            # Bu dönem kisa_vade_gun'den baslar ve uzun_vade_gun'e kadar devam eder.
            # X ekseni için günler: kisa_vade_gun, kisa_vade_gun + 1, ..., uzun_vade_gun
            days_fv_plot = list(range(kisa_vade_gun, uzun_vade_gun + 1))
            # Y ekseni için getiriler: Bu dönemin getirisi, kısa vade sonundaki birikmiş değer üzerinden hesaplanır.
            # Forward periyodunun kendi içindeki gün sayısı: 0, 1, ..., ara_donem_gun
            returns_fv_plot = [returns_kv[-1] * ((1 + gunluk_bilesik_ara)**d) for d in range(ara_donem_gun + 1)]

            # 3. Birleşik (Uzun Vade) Dönemi
            # Bu, 0. günden uzun_vade_gun'e kadar olan toplam birikimi gösterir.
            days_uzun_vade_plot = list(range(uzun_vade_gun + 1))
            returns_uzun_vade_plot = []
            for d_idx, d_val in enumerate(days_uzun_vade_plot):
                if d_val <= kisa_vade_gun:
                    returns_uzun_vade_plot.append(returns_kv[d_idx]) # Kısa vade bölümünden al
                else:
                    # Forward bölümü için, kisa_vade_gun'deki değerden başlayarak hesapla
                    # Forward periyodundaki gün sayısı: d_val - kisa_vade_gun
                    day_in_forward_period = d_val - kisa_vade_gun
                    returns_uzun_vade_plot.append(
                        returns_kv[-1] * ((1 + gunluk_bilesik_ara)**day_in_forward_period)
                    )

            plt.figure(figsize=(12, 7))

            # 1. Kısa Vade Çizgisi
            plt.plot(days_kv, returns_kv, label=f"Kısa Vade ({kisa_vade_gun} gün)", marker='o', linestyle='-', markersize=4, zorder=3)

            # 2. Forward Dönem Çizgisi
            # days_fv_plot ve returns_fv_plot zaten doğru başlangıç değerlerini içeriyor.
            plt.plot(days_fv_plot, returns_fv_plot, label=f"Forward Dönem ({ara_donem_gun} gün)", marker='s', linestyle='-', markersize=4, zorder=3)

            # 3. Birleşik Uzun Vade Çizgisi
            # returns_uzun_vade_plot, 0. günden uzun vade sonuna kadar olan birleşik getiriyi zaten hesaplıyor.
            plt.plot(days_uzun_vade_plot, returns_uzun_vade_plot, label=f"Birleşik Getiri ({uzun_vade_gun} gün)", linestyle='--', color='purple', linewidth=2, zorder=2)

            plt.title("Günlük Bileşik Getiri Grafiği", fontsize=16)
            plt.xlabel("Günler", fontsize=12)
            plt.ylabel("Kümülatif Getiri (Başlangıç = 1.0)", fontsize=12)
            plt.legend(fontsize=10)
            plt.grid(True, which='both', linestyle='--', linewidth=0.5)
            plt.tight_layout()
            st.pyplot(plt.gcf())
            plt.close() # Streamlit'te memory leak önlemek için figürü kapat
            # --- Grafik Ekleme Sonu ---
        else:
            st.warning("Doğrulama için gerekli günlük bileşik getirilerden biri veya birkaçı hesaplanamadı.")
    else:
        # Bu durum normalde yillik_vadeler_arasi_faiz_hesapla içinde hata mesajıyla yakalanmalı
        st.error("Beklenmedik bir hata oluştu, forward faiz oranı hesaplanamadı.")
else:
    st.info("Hesaplama yapmak için lütfen sol paneldeki 'Hesapla' butonuna tıklayın.")

st.sidebar.divider()
st.sidebar.markdown("---")
st.sidebar.markdown("<p style='text-align: center; font-size: small;'>Forward Faiz Hesaplayıcı v1.0</p>", unsafe_allow_html=True)

