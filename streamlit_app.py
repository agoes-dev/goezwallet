from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Konfigurasi Halaman & Tema Mobile-friendly
st.set_page_config(
    page_title="Dompetku", page_icon="💳", layout="centered", initial_sidebar_state="collapsed"
)

# Styling CSS Tambahan untuk Mempercantik Tampilan (Custom UI)
st.markdown(
    """
    <style>
    /* Styling utama agar lebih rapi */
    .main {
        background-color: #f8f9fa;
    }
    /* Kartu metrik kustom */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        text-align: center;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# File CSV untuk penyimpanan data
DATA_FILE = "keuangan_data.csv"


def load_data():
  if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Tanggal", "Tipe", "Kategori", "Jumlah", "Catatan"])
    df.to_csv(DATA_FILE, index=False)
  return pd.read_csv(DATA_FILE)


def save_data(tanggal, tipe, kategori, jumlah, catatan):
  df = load_data()
  new_data = pd.DataFrame([{
      "Tanggal": tanggal,
      "Tipe": tipe,
      "Kategori": kategori,
      "Jumlah": jumlah,
      "Catatan": catatan if catatan else "-",
  }])
  df = pd.concat([df, new_data], ignore_index=True)
  df.to_csv(DATA_FILE, index=False)


# Header Aplikasi
st.markdown("## 💳 Dompetku")
st.markdown("<p style='color: gray;'>Kelola keuangan harian jadi lebih mudah</p>", unsafe_allow_html=True)

# Navigasi menggunakan Radio Button horizontal / Tabs agar mudah di HP
menu = st.radio(
    "Navigasi", ["📊 Dashboard", "➕ Catat", "📜 Riwayat"], horizontal=True, label_visibility="collapsed"
)

df_transaksi = load_data()

# ================= MENU 1: DASHBOARD / LAPORAN =================
if menu == "📊 Dashboard":
  st.markdown("### Ringkasan Keuangan")

  if not df_transaksi.empty:
    total_masuk = df_transaksi[df_transaksi["Tipe"] == "Pemasukan"]["Jumlah"].sum()
    total_keluar = df_transaksi[df_transaksi["Tipe"] == "Pengeluaran"]["Jumlah"].sum()
    sisa_saldo = total_masuk - total_keluar

    # Tampilan Metrik Modern
    col1, col2 = st.columns(2)
    with col1:
      st.markdown(
          f"""
            <div class="metric-card">
                <span style="color: green; font-weight: bold;">Pemasukan</span>
                <h4 style="color: green; margin: 5px 0;">Rp {total_masuk:,.0f}</h4>
            </div>
            """,
          unsafe_allow_html=True,
      )
    with col2:
      st.markdown(
          f"""
            <div class="metric-card">
                <span style="color: red; font-weight: bold;">Pengeluaran</span>
                <h4 style="color: red; margin: 5px 0;">Rp {total_keluar:,.0f}</h4>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.markdown(
        f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <span style="font-weight: bold;">Sisa Saldo Anda</span>
            <h2 style="margin: 5px 0;">Rp {sisa_saldo:,.0f}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("#### 📈 Grafik Pengeluaran per Kategori")
    df_keluar = df_transaksi[df_transaksi["Tipe"] == "Pengeluaran"]
    if not df_keluar.empty:
      chart_data = df_keluar.groupby("Kategori")["Jumlah"].sum()
      st.bar_chart(chart_data)
    else:
      st.info("Belum ada data pengeluaran untuk dibuat grafik.")

  else:
    st.info("👋 Selamat datang! Belum ada data transaksi. Silakan tambah data di menu **Catat**.")

# ================= MENU 2: CATAT TRANSAKSI =================
elif menu == "➕ Catat":
  st.markdown("### Tambah Transaksi Baru")

  with st.form("form_transaksi", clear_on_submit=True):
    tanggal = st.date_input("Tanggal", datetime.today())
    tipe = st.selectbox("Tipe Transaksi", ["Pengeluaran", "Pemasukan"])

    # Dinamis kategori berdasarkan tipe
    if tipe == "Pengeluaran":
      kategori = st.selectbox(
          "Kategori",
          [
              "Makanan & Minuman",
              "Transportasi",
              "Belanja",
              "Tagihan & Utilitas",
              "Hiburan",
              "Lain-lain",
          ],
      )
    else:
      kategori = st.selectbox(
          "Kategori", ["Gaji", "Bonus", "Investasi", "Pemasukan Lainnya"]
      )

    jumlah = st.number_input("Nominal (Rp)", min_value=0, step=1000, format="%d")
    catatan = st.text_input("Catatan (Opsional)", placeholder="Contoh: Beli kopi")

    submit = st.form_submit_button(
        "💾 Simpan Transaksi", use_container_width=True
    )

    if submit:
      if jumlah > 0:
        save_data(str(tanggal), tipe, kategori, jumlah, catatan)
        st.success("✅ Transaksi berhasil disimpan!")
      else:
        st.error("⚠️ Nominal harus lebih besar dari 0!")

# ================= MENU 3: RIWAYAT TRANSAKSI =================
elif menu == "📜 Riwayat":
  st.markdown("### Riwayat Transaksi")

  if not df_transaksi.empty:
    # Tampilkan tabel yang lebih rapi
    st.dataframe(
        df_transaksi.sort_index(ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("---")
    # Tombol Reset Data
    if st.button("🗑️ Hapus Semua Riwayat", type="secondary"):
      if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("Semua data berhasil dihapus.")
        st.rerun()
  else:
    st.info("Belum ada riwayat transaksi.")
