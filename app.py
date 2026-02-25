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
if 'popup_open' not in st.session_state:
    st.session_state.popup_open = False

# 自定義 CSS
st.markdown("""
    <style>
    /* 黃色大框框容器 */
    .popup-wrapper {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; z-index: 9999;
    }
    
    .floating-info {
        background-color: #FFD700; padding: 40px; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); 
        text-align: center; border: 4px solid #DAA520; 
        width: 100%; animation: fadeIn 0.3s forwards;
    }
    
    /* 這裡是最關鍵的修正：把 Streamlit 按鈕的容器強制移到黃色框的右上角 */
    .close-btn-pos {
        position: absolute; top: 15px; right: 15px; z-index: 10001;
    }
    
    /* 讓叉叉按鈕看起來更像叉叉 */
    .close-btn-pos button {
        background-color: transparent !important;
        border: none !important;
        font-size: 24px !important;
        color: #555 !important;
        font-weight: bold !important;
    }
    .close-btn-pos button:hover { color: #000 !important; }

    .table-anchor { scroll-margin-top: 300px; }
    
    /* 亮黃色選中桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.15);
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
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
        search_q = st.text_input("請輸入票號查詢：", placeholder="例如：1351", key="search_main")
    with c_btn:
        if st.button("🔍 查詢"):
            if search_q:
                try:
                    q_num = int(search_q)
                    found = df_guest[df_guest['票號'] == q_num]
                    if not found.empty:
                        st.session_state.focus_table = int(found.iloc[0]['桌號'])
                        st.session_state.popup_open = True
                        st.session_state.found_name = found.iloc[0]['姓名']
                    else:
                        st.session_state.focus_table = None
                        st.session_state.popup_open = False
                        st.error("查無此票號")
                except:
                    st.error("請輸入數字票號")

    # --- 這次的結構調整：把按鈕強行塞進包裝層 ---
    if st.session_state.popup_open and st.session_state.focus_table:
        # 開啟一個包裝容器
        st.markdown('<div class="popup-wrapper">', unsafe_allow_html=True)
        
        # 繪製金黃色內容框
        st.markdown(f"""
            <div class="floating-info">
                <h2 style="color: black; margin-bottom: 0px;">👋 {st.session_state.found_name} 貴賓</h2>
                <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                    您的位置在：第 {st.session_state.focus_table} 桌
                </p>
                <a href="#table_{st.session_state.focus_table}" target="_self" style="text-decoration: none;">
                    <button style="background-color: #000; color: #fff; padding: 15px 30px; border-radius: 10px; border: none; cursor: pointer; font-size: 18px; font-weight: bold; width: 100%;">
                        👉 點我看座位 (自動定位)
                    </button>
                </a>
            </div>
            """, unsafe_allow_html=True)
        
        # 在同一個 wrapper 裡放置關閉按鈕，並套用絕對定位
        st.markdown('<div class="close-btn-pos">', unsafe_allow_html=True)
        if st.button("✖️", key="final_close_btn"):
            st.session_state.popup_open = False
            st.session_state.focus_table = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 關閉包裝容器
        st.markdown('</div>', unsafe_allow_html=True)

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

# ... 其餘 tab2, tab3 維持原樣 ...