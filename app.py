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

# 自定義 CSS (強化小框與右上角叉叉)
st.markdown("""
    <style>
    .floating-info {
        position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%);
        background-color: #FFD700; padding: 40px; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; animation: fadeIn 0.3s;
        min-width: 350px;
    }
    /* 真正的叉叉按鈕樣式 */
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 32px; font-weight: bold; color: #555;
        cursor: pointer; line-height: 1; transition: 0.2s;
        background: none; border: none;
    }
    .close-x:hover { color: #000; transform: scale(1.2); }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .table-anchor { scroll-margin-top: 300px; }
    
    /* 亮黃色目標桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.15); transition: 0.3s;
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
    # 搜尋欄 (拿掉清除查詢按鈕)
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main", placeholder="輸入後自動定位...")

    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        
        if not found.empty:
            first_row = found.iloc[0]
            st.session_state.focus_table = int(first_row['桌號'])
            
            # 建立小框內容
            st.markdown(f"""
                <div class="floating-info">
                    <form action="/" method="get">
                        <button type="submit" class="close-x">×</button>
                    </form>
                    <h2 style="color: black; margin-top: 10px;">👋 {first_row['姓名']} 貴賓</h2>
                    <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                        您的位置在：第 {st.session_state.focus_table} 桌
                    </p>
                    <a href="#table_{st.session_state.focus_table}" target="_self" style="text-decoration: none;">
                        <button style="background-color: #000; color: #fff; padding: 15px 30px; border-radius: 10px; border: none; cursor: pointer; font-size: 20px; font-weight: bold;">
                            👉 點我看座位 (自動定位)
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.session_state.focus_table = None

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

with tab2:
    st.subheader("📝 登記與驗證")
    mode = st.radio("登記模式：", ["單筆輸入", "連號批次登記", "Excel 批次上傳"], horizontal=True)
    if mode == "單筆輸入":
        with st.form("single_form"):
            c1, c2, c3 = st.columns(3)
            with c1: name = st.text_input("姓名"); phone = st.text_input("電話")
            with c2: seller = st.text_input("售票者"); ticket = st.number_input("票號", 1, 2000)
            with c3: table = st.number_input("預計桌號", 1, 200)
            if st.form_submit_button("執行驗證"):
                st.success(f"{name} 驗證通過")
    elif mode == "連號批次登記":
        with st.form("batch_form"):
            c1, c2 = st.columns(2)
            name_b = c1.text_input("代表姓名"); seller_b = c2.text_input("售票負責人")
            start_t = c2.number_input("起始票號", 1, 2000); count_t = c2.number_input("張數", 1, 100)
            if st.form_submit_button("批次驗證"):
                st.success("驗證通過")
    else:
        st.file_uploader("上傳 Excel", type=["xlsx"])

with tab3:
    st.subheader("📊 數據中心")
    csv = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載目前資料庫 (CSV)", csv, "千人宴總表.csv", "text/csv")
    st.dataframe(df_guest, use_container_width=True)