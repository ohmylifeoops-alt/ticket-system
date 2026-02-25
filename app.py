import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session State
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# 自定義 CSS
st.markdown("""
    <style>
    .floating-info {
        position: fixed; top: 20%; left: 50%; transform: translate(-50%, -50%);
        background-color: #FFD700; padding: 25px; border-radius: 15px;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.3); z-index: 9999;
        text-align: center; border: 3px solid #DAA520; animation: fadeIn 0.5s;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .table-anchor { scroll-margin-top: 250px; }
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 2px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.1); transition: 0.3s;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if "桌號" in data.columns:
            data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局檔案")
        return
    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    st.markdown("### 🏟️ 千人宴場地實景佈局")
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else "#2E7D32"
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold;'>{row_content}</div>", unsafe_allow_html=True)
            continue
        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        is_target = (table_num == st.session_state.focus_table)
                        display_name = f"VIP{table_num}" if table_num in [1,2,3] else str(table_num)
                        st.markdown(f"<div id='table_{table_num}' class='table-anchor'></div>", unsafe_allow_html=True)
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", type="primary" if is_target else "secondary", use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main")
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            first_row = found.iloc[0]
            target_t = int(first_row['桌號'])
            st.markdown(f"""<div class="floating-info"><h2 style="color: black;">👋 {first_row['姓名']} 貴賓</h2>
                <p style="font-size: 24px; color: #d32f2f; font-weight: bold;">您的位置在：第 {target_t} 桌</p>
                <a href="#table_{target_t}" target="_self"><button style="background-color: #000; color: #fff; padding: 10px 20px; border-radius: 8px; border: none; cursor: pointer;">👉 點我看座位 (自動定位)</button></a></div>""", unsafe_allow_html=True)
            st.session_state.focus_table = target_t
        else:
            st.session_state.focus_table = None
            st.error("查無資訊")
    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

with tab2:
    st.subheader("📝 登記驗證系統")
    mode = st.radio("選擇登記模式：", ["單筆輸入", "連號批次登記", "Excel 批次上傳"], horizontal=True)

    if mode == "單筆輸入":
        with st.form("single_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                name = st.text_input("姓名")
                phone = st.text_input("電話")
            with c2:
                seller = st.text_input("售票者")
                ticket = st.number_input("票號", 1, 2000, 1)
            with c3:
                table = st.number_input("預計桌號", 1, 200, 1)
            
            if st.form_submit_button("執行單筆驗證"):
                if not name: st.error("請輸入姓名")
                elif not seller: st.error("請輸入售票者")
                else:
                    existing = set(df_guest['票號'].values)
                    if ticket in existing: st.error(f"❌ 票號 {ticket} 已被登記！")
                    else:
                        st.balloons()
                        st.success(f"✅ 驗證通過！請手動填入雲端表：\n{name} / {phone} / {ticket} / {seller} / {table}")

    elif mode == "連號批次登記":
        with st.form("batch_form"):
            c1, c2 = st.columns(2)
            name_b = c1.text_input("領票代表姓名")
            phone_b = c1.text_input("聯絡電話")
            seller_b = c2.text_input("售票負責人")
            ca, cb = c2.columns(2)
            start_t = ca.number_input("起始票號", 1, 2000, 1)
            count_t = cb.number_input("張數", 1, 100, 10)
            table_b = st.number_input("統一安排桌號 (可事後手動微調)", 1, 200, 1)
            
            if st.form_submit_button("執行連號驗證"):
                t_range = range(int(start_t), int(start_t) + int(count_t))
                existing = set(df_guest['票號'].values)
                conflicts = [t for t in t_range if t in existing]
                if conflicts: st.error(f"❌ 衝突！票號 {conflicts} 已登記")
                else:
                    st.success("🎉 驗證成功！請複製以下內容至 Google Sheets：")
                    rows = [f"{name_b}\t{phone_b}\t{t}\t{seller_b}\t{table_b}" for t in t_range]
                    st.code("\n".join(rows))

    else:
        up_file = st.file_uploader("上傳 Excel", type=["xlsx"])
        if up_file: st.info("Excel 已讀取，請執行資料比對")

with tab3:
    st.subheader("📊 數據中心")
    csv = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載目前資料庫 (CSV)", csv, "backup.csv", "text/csv")
    st.dataframe(df_guest, use_container_width=True)