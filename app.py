import streamlit as st
import pandas as pd
import os

# --- 1. 檔案與雲端連結設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
# 您的 Google Sheets CSV 下載網址
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

# 讀取 Google 試算表資料
@st.cache_data(ttl=30)
def load_cloud_data():
    try:
        # 強制指定編碼以防亂碼
        data = pd.read_csv(SHEET_URL)
        return data
    except Exception as e:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_cloud_data()

# 自動算桌次邏輯
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案: {LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    st.markdown("### 🏟️ 場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        # 檢查該列是否包含標籤
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        if "舞台" in row_content:
            st.markdown("<div style='background-color:#FF4B4B; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚩 舞 臺 STAGE</div>", unsafe_allow_html=True)
            continue
        elif "入口" in row_content:
            st.markdown("<div style='background-color:#2E7D32; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚪 主 入 口 ENTRANCE</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            # 修正處：確保 if 語句後的縮排完整
            if c_idx >= 10: 
                break 
                
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text == "" or cell_text == "nan":
                    st.write("")
                elif "電視" in cell_text:
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px;'>📺</div>", unsafe_allow_html=True)
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlighted_tables
                        st.button(
                            f"{table_num}", 
                            key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                            type="primary" if is_active else "secondary", 
                            use_container_width=True
                        )
                    except:
                        if cell_text != "nan": 
                            st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 宴會桌次管理 (雲端同步版)")

tab1, tab2 = st.tabs(["🔍 實景搜尋", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_input")
    highlighted_list = []
    if search_q:
        # 強制轉換所有欄位為字串進行模糊搜尋
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        # 確保抓取到的桌號是整數
        found_data = df_guest[mask]
        if not found_data.empty:
            highlighted_list = found_data['桌號'].dropna().astype(int).tolist()
            st.success(f"找到賓客，位於第 {list(set(highlighted_list))} 桌")
        else:
            st.warning("查無資料，請確認 Google Sheets 內容")
            
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📊 雲端試算表數據預覽")
    st.info("資料每 30 秒自動更新，或點擊下方按鈕強制重新讀取。")
    st.dataframe(df_guest, use_container_width=True)
    if st.button("🔄 立即強制刷新雲端資料"):
        st.cache_data.clear()
        st.rerun()