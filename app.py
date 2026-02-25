import streamlit as st
import pandas as pd
import os

# --- 1. 系統效能與雲端設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="宴會桌次實景管理系統", page_icon="🎟️", layout="wide")

# 讀取雲端賓客資料 (緩存 30 秒)
@st.cache_data(ttl=30, show_spinner=False)
def load_cloud_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if "票號" in data.columns:
            data['票號'] = pd.to_numeric(data['票號'], errors='coerce')
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_cloud_data()

def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 實景地圖繪製 (動態欄位校正版) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局檔案，請確認 CSV 已上傳至 GitHub。")
        return

    # 讀取最新佈局檔
    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) # 動態偵測欄位數 (例如現在是 9 欄)
    
    highlight_set = set(highlighted_tables)
    st.markdown("### 🏟️ 場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        # 檢查整列內容
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        # --- 🚩 滿版大標籤處理 (舞台、入口、電視牆) ---
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            icon = "🚩" if "舞台" in row_content else ("📺" if "電視" in row_content else "🚪")
            st.markdown(f"""
                <div style='background-color:{color}; color:white; text-align:center; 
                padding:12px; border-radius:10px; font-weight:bold; font-size:20px; margin: 10px 0;'>
                {icon} {row_content}
                </div>
                """, unsafe_allow_html=True)
            continue

        # --- 🔘 桌位按鈕處理 (動態對齊欄位) ---
        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            if c_idx >= num_cols: break 
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                
                if cell_text in ["", "nan"]:
                    st.write("")
                elif "電視" in cell_text:
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px;'>📺</div>", unsafe_allow_html=True)
                else:
                    try:
                        # 嘗試轉為桌號
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        st.button(f"{table_num}", key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        # 非數字則顯示一般文字
                        if cell_text != "nan": st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 宴會桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main")
    highlighted_list = []
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].dropna().unique().astype(int).tolist()
            st.success(f"✅ 找到賓客，分配在：{highlighted_list} 桌")
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📝 登記驗證 (支援批次)")
    mode = st.radio("模式：", ["單筆", "批次"], horizontal=True)
    with st.form("input_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("領票人姓名")
            phone = st.text_input("電話")
        with c2:
            seller = st.text_input("售票負責人")
            if mode == "單筆":
                start_t = st.number_input("票號", 1, 1700, 1)
                count = 1
            else:
                ca, cb = st.columns(2)
                with ca: start_t = st.number_input("起始票號", 1, 1700, 1)
                with cb: count = st.number_input("張數", 1, 100, 10)
        if st.form_submit_button("執行驗證"):
            if not name.strip():
                st.error("⚠️ 錯誤：姓名不能為空！")
            else:
                t_range = range(int(start_t), int(start_t) + int(count))
                existing = set(df_guest['票號'].dropna().astype(int).values) if not df_guest.empty else set()
                conflicts = [t for t in t_range if t in existing]
                if conflicts:
                    st.error(f"❌ 錯誤：票號 {conflicts} 已被登記過！")
                else:
                    st.balloons()
                    st.success("🎉 驗證通過！請將內容貼至 Google Sheets：")
                    final_rows = [f"{name}\t{phone}\t{t}\t{seller}\t{calculate_table(t)}" for t in t_range]
                    st.code("\n".join(final_rows), language="text")

with tab3:
    st.subheader("📊 資料庫預覽")
    st.dataframe(df_guest.sort_values(by="票號") if not df_guest.empty else df_guest, use_container_width=True)
    if st.button("🔄 強制重新讀取 (地圖與雲端)"):
        st.cache_data.clear()
        st.rerun()