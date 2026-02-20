import streamlit as st
import pandas as pd
import os

# --- 1. 檔案與雲端連結設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次管理系統", page_icon="🎟️", layout="wide")

# 讀取雲端資料
@st.cache_data(ttl=10) # 縮短緩存時間，讓輸入後更快看到結果
def load_cloud_data():
    try:
        return pd.read_csv(SHEET_URL)
    except:
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
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        if "舞台" in row_content:
            st.markdown("<div style='background-color:#FF4B4B; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚩 舞 臺 STAGE</div>", unsafe_allow_html=True)
            continue
        elif "入口" in row_content:
            st.markdown("<div style='background-color:#2E7D32; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; font-size:24px; margin: 10px 0;'>🚪 主 入 口 ENTRANCE</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
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
                        st.button(f"{table_num}", key=f"btn_{r_idx}_{c_idx}_{table_num}", type="primary" if is_active else "secondary", use_container_width=True)
                    except:
                        if cell_text != "nan": st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 宴會桌次管理系統")

tab1, tab2, tab3 = st.tabs(["🔍 實景搜尋", "📝 賓客登記", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main")
    highlighted_list = []
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found_data = df_guest[mask]
        if not found_data.empty:
            highlighted_list = found_data['桌號'].dropna().astype(int).tolist()
            st.success(f"找到賓客，位於第 {list(set(highlighted_list))} 桌")
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📝 賓客資料輸入")
    with st.form("guest_entry", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("賓客姓名")
            new_ticket = st.number_input("票號 (1-1700)", min_value=1, max_value=1700, step=1)
        with col2:
            new_phone = st.text_input("聯絡電話")
            new_seller = st.text_input("售出者")
        
        submit = st.form_submit_button("確認提交")
        
        if submit:
            # --- 🛡️ 防呆機制 ---
            if not new_name.strip():
                st.error("❌ 錯誤：請輸入賓客姓名！")
            elif df_guest['票號'].astype(str).str.contains(f"^{new_ticket}$").any():
                st.error(f"❌ 錯誤：票號 {new_ticket} 已經被登記過了！")
            else:
                # 計算桌號
                assigned_table = calculate_table(new_ticket)
                
                # 提醒：目前的 Sheet 串接為「唯讀」
                st.success(f"✅ 驗證成功！")
                st.info(f"建議桌號為：第 {assigned_table} 桌")
                st.warning("⚠️ 注意：目前的系統是連動 Google Sheets，請手動將資料填入雲端表格，網頁會自動同步。")
                
                # 顯示準備新增的內容，方便使用者複製貼上
                st.code(f"{new_name}, {new_phone}, {new_ticket}, {new_seller}, {assigned_table}", language="text")

with tab3:
    st.subheader("📊 雲端數據預覽")
    st.dataframe(df_guest, use_container_width=True)
    if st.button("🔄 強制刷新雲端資料"):
        st.cache_data.clear()
        st.rerun()