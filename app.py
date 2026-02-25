import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 完美 CSS (還原所有間距與樣式) ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }

    .popup-container {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 400px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; 
        padding: 40px 20px; animation: fadeIn 0.3s forwards;
    }
    
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 35px; color: #555; text-decoration: none;
        font-family: Arial, sans-serif; font-weight: bold; cursor: pointer;
    }

    /* 框內定位按鈕樣式 */
    .anchor-btn-js {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 15px 30px; border-radius: 10px; border: none;
        font-size: 18px; font-weight: bold; width: 85%; margin-top: 20px;
        cursor: pointer; text-decoration: none;
    }
    
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-top: -12px !important; margin-bottom: -12px !important; }

    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 20px 0 !important; width: 100%;
    }
    
    .target-point { scroll-margin-top: 350px; }
    
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>

    <script>
    // 跨越 iframe 定位的黑科技
    function scrollToTable(num) {
        const target = window.parent.document.getElementById('t_' + num);
        if (target) {
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
    </script>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        for col in ['票號', '桌號']:
            if col in data.columns:
                data[col] = pd.to_numeric(data[col], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    highlight_set = set(highlighted_tables)
    
    st.markdown("### 🏟️ 千人宴場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            st.markdown(f'<div class="label-box-fixed" style="--label-color: {color};">{row_content}</div>', unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        display_name = f"VIP{table_num}" if table_num in [1,2,3] else str(table_num)
                        # 定位點 ID
                        st.markdown(f'<div id="t_{table_num}" class="target-point"></div>', unsafe_allow_html=True)
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", type="primary" if is_active else "secondary", use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 介面內容 ---
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
                
                # --- 這裡就是按鈕回歸的地方！ ---
                # 使用 onclick 調用 parent 的 JS 函式，達成無痕捲動
                st.markdown(f"""
                    <div class="popup-container">
                        <a href="./" target="_self" class="close-x">×</a>
                        <h2 style="color: black; margin: 0;">👋 {first_row['姓名']} 貴賓</h2>
                        <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                            您的位置在：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                        </p>
                        <button onclick="window.parent.scrollToTable({st.session_state.focus_table})" class="anchor-btn-js">
                            👉 點我看座位 (自動定位)
                        </button>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.session_state.focus_table = None
                if search_q: st.error("查無此票號")
        except:
            if search_q: st.error("請輸入數字")

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

# Tab 2, 3 ...