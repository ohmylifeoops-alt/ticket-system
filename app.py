import streamlit as st
import pandas as pd
import os

# --- 1. 系統效能與雲端設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
# 您提供的 Google Sheets CSV 下載連結
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次管理系統", page_icon="🎟️", layout="wide")

# 穩定讀取雲端資料 (緩存 30 秒以防塞車)
@st.cache_data(ttl=30, show_spinner=False)
def load_cloud_data():
    try:
        data = pd.read_csv(SHEET_URL)
        # 確保資料庫包含必要欄位，否則回傳空表
        required = ["姓名", "票號", "桌號"]
        if not all(col in data.columns for col in required):
            return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])
        # 強制將票號轉為數字，方便比對
        data['票號'] = pd.to_numeric(data['票號'], errors='coerce')
        return data.dropna(subset=['票號'])
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_cloud_data()

# 快速算桌邏輯 (10人一桌)
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 實景地圖繪製 (橫跨全排樣式) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到地圖佈局檔案")
        return

    @st.cache_data
    def get_layout():
        return pd.read_csv(LAYOUT_FILE, header=None)
    
    df_map = get_layout()
    highlight_set = set(highlighted_tables)

    for r_idx, row in df_map.iterrows():
        # 轉為字串檢查是否有標籤
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        # 🚩 舞台與入口橫跨 10 欄
        if "舞台" in row_content:
            st.markdown("<div style='background-color:#FF4B4B; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚩 舞 臺 STAGE</div>", unsafe_allow_html=True)
            continue
        elif "入口" in row_content:
            st.markdown("<div style='background-color:#2E7D32; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚪 主 入 口 ENTRANCE</div>", unsafe_allow_html=True)
            continue

        # 一般桌位列
        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text in ["", "nan"]:
                    st.write("")
                elif "電視" in cell_text:
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px;'>📺</div>", unsafe_allow_html=True)
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        st.button(f"{table_num}", key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        if cell_text != "nan": st.caption(cell_text)

# --- 3. 介面三大分頁 ---
st.title("🎟️ 宴會桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋與地圖", "📝 批次登記/防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 輸入姓名、電話或票號：", key="search_main")
    highlighted_list = []
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].dropna().unique().astype(int).tolist()
            st.success(f"✅ 找到賓客，分配在：{highlighted_list} 桌")
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📝 登記與防呆驗證")
    mode = st.radio("登記模式：", ["單筆登記", "批次登記 (多人領票)"], horizontal=True)

    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("領票人姓名")
            phone = st.text_input("聯絡電話")
        with c2:
            seller = st.text_input("售票負責人")
            if mode == "單筆登記":
                start_t = st.number_input("票號", 1, 1700, 1)
                count = 1
            else:
                ca, cb = st.columns(2)
                with ca: start_t = st.number_input("起始票號", 1, 1700, 1)
                with cb: count = st.number_input("張數", 1, 100, 10)
        
        if st.form_submit_button("執行防呆驗證"):
            if not name.strip():
                st.error("⚠️ 錯誤：姓名不能為空！")
            else:
                # 建立檢查範圍
                t_range = range(int(start_t), int(start_t) + int(count))
                existing_tickets = set(df_guest['票號'].astype(int).values)
                conflicts = [t for t in t_range if t in existing_tickets]
                
                if conflicts:
                    st.error(f"❌ 嚴重錯誤