import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

# 初始化狀態
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None
if 'scroll_trigger' not in st.session_state:
    st.session_state.scroll_trigger = False

# --- 🎨 核心 CSS：確保排版莊重且間距壓縮 ---
st.markdown("""
    <style>
    /* 搜尋區域對齊 */
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }

    /* 金黃色小框 */
    .popup-container {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; 
        padding: 40px 20px 80px 20px;
        animation: fadeIn 0.3s forwards;
    }
    
    /* 叉叉關閉：使用 Streamlit 重新整理機制清空狀態 */
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 35px; color: #555; text-decoration: none;
        font-family: Arial, sans-serif; font-weight: bold; cursor: pointer;
    }
    
    /* 強制壓縮地圖上下間距 */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-top: -12px !important; margin-bottom: -12px !important; }

    /* 標籤盒還原大氣感 */
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 20px 0 !important; width: 100%;
    }
    
    .target-spot { scroll-margin-top: 350px; }
    
    /* 亮黃色選中桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }
    
    /* 鎖定框內按鈕位置 */
    .popup-btn-pos {
        position: fixed; top: 58%; left: 50%; transform: translate(-50%, -50%);
        z-index: 10000; width: 280px;
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if '票號' in data.columns:
            data['票號_str'] = data['票號'].astype(str)
        if '桌號' in data.columns:
            data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

def draw_seating_chart(highlighted_table):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案：{LAYOUT_FILE}")
        return
    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    
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
                        is_active = (table_num == highlighted_table)
                        # 這是 JS 定位用的 ID
                        st.markdown(f'<div id="t_{table_num}" class="target-spot"></div>', unsafe_allow_html=True)
                        st.button(f"VIP{table_num}" if table_num <= 3 else str(table_num), 
                                  key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        search_q = st.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 王大明", key="search_main")
    with c_btn:
        if st.button("🔍 查詢"):
            st.session_state.scroll_trigger = False # 重設捲動觸發

    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        
        if not found.empty:
            first_row = found.iloc[0]
            st.session_state.focus_table = int(first_row['桌號'])
            
            # 1. 顯示金黃色彈窗
            st.markdown(f"""
                <div class="popup-container">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2 style="color: black; margin: 0;">👋 {first_row['姓名']} 貴賓</h2>
                    <p style="font-size: 20px; color: #555; margin: 5px 0;">票號：{first_row['票號']}</p>
                    <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 15px 0;">
                        位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # 2. 定位按鈕 (原生按鈕，點擊後觸發 Session State)
            st.markdown('<div class="popup-btn-pos">', unsafe_allow_html=True)
            if st.button("👉 點我看座位 (自動定位)", key="jump_loc_btn"):
                st.session_state.scroll_trigger = True
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 3. 真正執行定位的組件 (只有點擊後才會渲染並執行，執行完不留痕跡)
            if st.session_state.scroll_trigger:
                components.html(f"""
                    <script>
                        var target = window.parent.document.getElementById('t_{st.session_state.focus_table}');
                        if (target) {{
                            target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                        }}
                    </script>
                """, height=0)
                st.session_state.scroll_trigger = False # 執行完畢
        else:
            st.session_state.focus_table = None
            st.error("查無此貴賓或票號。")

    draw_seating_chart(st.session_state.focus_table)

with tab2:
    st.subheader("📝 登記與驗證")
    # 這裡原本會變空白，現在因為網址乾淨，會正常顯示
    st.info("請輸入賓客資料進行登記。")
    # ... (其餘登記功能代碼)

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)