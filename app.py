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
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

# 自定義 CSS (移除表單提交，改用絕對定位按鈕)
st.markdown("""
    <style>
    .floating-info {
        position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%);
        background-color: #FFD700; padding: 40px; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; animation: fadeIn 0.3s;
        min-width: 350px;
    }
    /* 叉叉按鈕隱藏在 Streamlit 原生組件中 */
    .close-container {
        position: absolute; top: 10px; right: 10px; z-index: 10001;
    }
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    .table-anchor { scroll-margin-top: 300px; }
    
    div.stButton > button:first-child { height: 3em; margin-top: 28px; }
    
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
        if "票號" in data.columns:
            data['票號'] = pd.to_numeric(data['票號'], errors='coerce').fillna(0).astype(int)
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
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        search_q = st.text_input("請輸入票號查詢：", placeholder="例如：888", key="search_main")
    with c_btn:
        search_trigger = st.button("🔍 查詢")

    # 邏輯判斷：如果搜尋欄有變動或按下按鈕
    if search_q:
        try:
            q_num = int(search_q)
            found = df_guest[df_guest['票號'] == q_num]
            
            if not found.empty:
                first_row = found.iloc[0]
                # 僅在搜尋內容變動時，更新 focus_table
                if st.session_state.last_search != search_q:
                    st.session_state.focus_table = int(first_row['桌號'])
                    st.session_state.last_search = search_q

                # 繪製浮動小框
                if st.session_state.focus_table:
                    # 在小框內放一個「真正的」關閉按鈕，並用 CSS 定位到右上角
                    st.markdown('<div class="floating-info">', unsafe_allow_html=True)
                    
                    # 這是關鍵：Streamlit 原生按鈕，點擊會觸發程式碼邏輯而不是整頁 Reload
                    if st.button("✖️", key="close_popup"):
                        st.session_state.focus_table = None
                        st.session_state.last_search = ""
                        st.rerun() # 僅重刷 Streamlit 元件，不重載整個網頁頁面

                    st.markdown(f"""
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
                if search_q: st.error("查無此票號")
        except ValueError:
            if search_q: st.error("請輸入數字票號")

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

# ... 其餘 tab2, tab3 代碼保持不變 ...