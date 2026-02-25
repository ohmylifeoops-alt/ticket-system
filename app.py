import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定與資料來源 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
# 您原有的 Google Sheets 資料庫連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"
LOCAL_DB = "thousand_banquet_db.csv"

st.set_page_config(page_title="千人盛宴實景導引系統", page_icon="🧧", layout="wide")

# 💡 智慧讀取：優先看剛上傳的檔案，沒有的話就去抓原有的 Google Sheets
def load_combined_data():
    # 如果有剛上傳/更新的本地檔，用本地的
    if os.path.exists(LOCAL_DB):
        try:
            return pd.read_csv(LOCAL_DB).astype(str)
        except:
            pass
    
    # 如果沒有本地檔，則從您原有的 Google Sheets 抓取
    try:
        data = pd.read_csv(SHEET_URL)
        # 確保資料格式統一
        return data.astype(str)
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_combined_data()

# 💡 標籤轉化邏輯 (1 -> 1~10)
def get_display_label(val):
    try:
        n = int(float(str(val).strip()))
        if 1 <= n <= 300: 
            return f"{(n-1)*10+1}~{n*10}"
    except:
        pass
    return str(val)

# --- 2. 實景地圖 ---
def draw_seating_chart(highlighted_ids):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局 CSV，請確認 GitHub 檔案名稱正確。")
        return
    
    df_map = pd.read_csv(LAYOUT_FILE, header=None).astype(str)
    num_cols = len(df_map.columns)
    highlight_set = {str(x).strip().replace(".0", "") for x in highlighted_ids}

    st.markdown("### 🏟️ 千人盛宴：場地實景佈局")
    for r_idx, row in df_map.iterrows():
        row_content = "".join([val for val in row if val != "nan"])
        if any(k in row_content for k in ["舞台", "入口", "電視", "收銀", "禮賓"]):
            color = "#D32F2F" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:15px; border-radius:12px; font-weight:bold; font-size:22px; margin: 15px 0; box-shadow: 2px 2px 8px rgba(0,0,0,0.2);'>✨ {row_content} ✨</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                raw_id = val.strip().replace(".0", "") if val != "nan" else ""
                if raw_id:
                    display_text = get_display_label(raw_id)
                    is_active = raw_id in highlight_set
                    st.button(display_text, key=f"btn_{r_idx}_{c_idx}_{raw_id}", 
                              type="primary" if is_active else "secondary", use_container_width=True)

# --- 3. 介面內容 ---
st.markdown("<h1 style='text-align: center; color: #D32F2F;'>🧧 千人盛宴實景管理系統</h1>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔍 賓客位置搜尋", "📊 數據更新與下載"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", placeholder="請輸入關鍵字...")
    highlighted_list = []
    if search_q and not df_guest.empty:
        mask = df_guest.apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].tolist()
            labels = [get_display_label(x) for x in set(highlighted_list)]
            st.success(f"✅ 找到賓客！位置標記：{', '.join(labels)}")
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📥 1. 下載原有資料 (含 Google Sheets 內容)")
    st.write("點擊下方按鈕，系統會將您原有的雲端資料與最新更新合併匯出。")
    csv_temp = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載賓客清單範本 (CSV)",
        data=csv_temp,
        file_name="千人宴名單總表.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("📤 2. 批次更新 (全場大整理)")
    st.info("請將整理好「桌號」的 CSV 檔案上傳。上傳後系統會優先顯示此份檔案的內容。")
    uploaded_file = st.file_uploader("選擇上傳修正後的 CSV", type="csv")
    
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        new_df.to_csv(LOCAL_DB, index=False)
        st.success("✅ 全場資料更新成功！")
        if st.button("🔄 立即重新整理頁面"):
            st.rerun()

    st.divider()
    st.subheader("📋 目前資料預覽")
    st.dataframe(df_guest, use_container_width=True)