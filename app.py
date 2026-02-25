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

# 自定義 CSS：確保所有元素都在框內 (修正跑版問題)
st.markdown("""
    <style>
    /* 修正後的浮動視窗：使用 Flexbox 確保內容置中且不溢出 */
    .floating-info {
        position: fixed; top: 30%; left: 50%; transform: translate(-50%, -50%);
        background-color: #FFD700; 
        padding: 40px; 
        border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); 
        z-index: 10000;
        text-align: center; 
        border: 4px solid #DAA520; 
        width: 380px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        animation: fadeIn 0.3s forwards;
    }
    
    /* 修正後的叉叉按鈕：鎖定在父元素右上角 */
    .close-x-btn {
        position: absolute; top: 10px; right: 20px;
        font-size: 30px; font-weight: bold; color: #555;
        cursor: pointer; background: none; border: none;
        line-height: 1;
    }
    .close-x-btn:hover { color: #000; }
    
    /* 置中對齊標籤 */
    .table-anchor { scroll-margin-top: 300px; }
    
    /* 目標桌子變亮黃色 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.15);
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
    
    <script>
    // JavaScript 讓小框點擊叉叉後立刻消失，不需重整
    function closePopup() {
        const popup = document.getElementById('search-popup');
        if (popup) popup.style.display = 'none';
    }
    </script>
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
        search_trigger = st.button("🔍 查詢")

    if search_q or search_trigger:
        try:
            q_num = int(search_q)
            found = df_guest[df_guest['票號'] == q_num]
            
            if not found.empty:
                first_row = found.iloc[0]
                st.session_state.focus_table = int(first_row['桌號'])
                
                # --- 核心修正：純 HTML 框，不混合 Streamlit 元件 ---
                st.markdown(f"""
                    <div id="search-popup" class="floating-info">
                        <button onclick="closePopup()" class="close-x-btn">×</button>
                        <h2 style="color: black; margin-bottom: 0px;">👋 {first_row['姓名']} 貴賓</h2>
                        <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                            您的位置在：第 {st.session_state.focus_table} 桌
                        </p>
                        <a href="#table_{st.session_state.focus_table}" target="_self" style="text-decoration: none; width: 100%;">
                            <button style="background-color: #000; color: #fff; padding: 15px 30px; border-radius: 10px; border: none; cursor: pointer; font-size: 18px; font-weight: bold; width: 80%;">
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

# ... 其餘 tab2, tab3 維持原樣 ...