import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS 與 網址清理器 ---
st.markdown("""
    <style>
    /* 搜尋按鈕對齊 */
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }

    /* 完美同框容器 */
    .perfect-popup {
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        width: 420px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; padding: 40px 20px;
    }
    
    /* 框內叉叉 */
    .close-btn {
        position: absolute; top: 15px; right: 20px;
        font-size: 30px; color: #555; text-decoration: none; font-weight: bold;
    }

    /* 框內黑按鈕 */
    .inner-black-btn {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 15px 30px; border-radius: 12px; text-decoration: none;
        font-size: 18px; font-weight: bold; width: 85%; margin-top: 25px;
    }

    /* 地圖排版縮小上下間距 */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-bottom: -15px !important; }
    
    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    
    .scroll-target { scroll-margin-top: 350px; }
    
    /* 亮黃色選中桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
    }
    </style>

    <script>
    // 網址清潔工：定時檢查網址，只要有 # 就擦掉，保證 Tab 2 不會空白
    setInterval(function() {
        if (window.location.hash) {
            history.replaceState(null, null, window.location.pathname);
        }
    }, 500);
    </script>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        if '票號' in data.columns: data['票號_str'] = data['票號'].astype(str)
        if '桌號' in data.columns: data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

# --- 2. 介面內容 ---
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    c1, c2 = st.columns([4, 1])
    search_q = c1.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 楊美蓮", key="search_input")
    c2.button("🔍 查詢")

    if search_q:
        mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
        found = df_guest[mask]
        if not found.empty:
            row = found.iloc[0]
            st.session_state.focus_table = int(row['桌號'])
            
            # --- 核心：純 HTML 彈窗，所有東西都在同一個框框 ---
            st.markdown(f"""
                <div class="perfect-popup">
                    <a href="./" target="_self" class="close-btn">×</a>
                    <h2 style="color: black; margin: 0;">👋 {row['姓名']} 貴賓</h2>
                    <p style="font-size: 18px; color: #555; margin: 10px 0;">票號：{row['票號']}</p>
                    <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                        位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                    </p>
                    <a href="#table_{st.session_state.focus_table}" target="_self" class="inner-black-btn">
                        👉 點我看座位 (自動捲動)
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.session_state.focus_table = None
            st.error("查無資料")

    # 繪製地圖
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None)
        num_cols = len(df_map.columns)
        st.markdown("### 🏟️ 場地佈局實景")
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
                            t_num = int(float(val))
                            # 設定錨點供捲動
                            st.markdown(f'<div id="table_{t_num}" class="scroll-target"></div>', unsafe_allow_html=True)
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), 
                                      key=f"b_{r_idx}_{c_idx}", 
                                      type="primary" if t_num == st.session_state.focus_table else "secondary", 
                                      use_container_width=True)
                        except:
                            st.caption(cell_text)

with tab2:
    st.subheader("📝 登記功能")
    # 這裡絕對正常，因為背景腳本會持續清理網址
    st.text_input("輸入測試")

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)