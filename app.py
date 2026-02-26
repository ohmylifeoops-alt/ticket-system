import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴管理系統", page_icon="🎟️", layout="wide")

if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 核心 CSS ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }
    
    /* 完美同框黃框容器 */
    .popup-container {
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; padding: 40px 20px;
    }
    
    .close-x {
        position: absolute; top: 15px; right: 20px;
        font-size: 30px; color: #555; text-decoration: none; font-weight: bold;
    }

    .inner-btn {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 15px 30px; border-radius: 12px; text-decoration: none;
        font-size: 18px; font-weight: bold; width: 85%; margin-top: 20px;
    }

    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 15px 0 !important; width: 100%;
    }
    
    .target-spot { scroll-margin-top: 350px; }
    
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }

    .download-section {
        margin: 20px 0 30px 0 !important;
        padding-bottom: 20px;
        border-bottom: 1px solid #eee;
    }

    .spacer-row { height: 45px; width: 100%; }
    </style>

    <script>
    setInterval(function() {
        if (window.location.hash) {
            history.replaceState(null, null, window.location.pathname);
        }
    }, 500);
    </script>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30, show_spinner=False)
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
    c_in, c_bt = st.columns([4, 1])
    search_q = c_in.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 徐鳳慈", key="search_main")
    
    if search_q:
        # --- 🥚 催淚彩蛋邏輯區 ---
        if search_q == "陳聰發":
            st.markdown(f"""
                <div class="popup-container" style="background-color: #FFF9C4; border-color: #FBC02D;">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2 style="color: #F57F17; margin-bottom: 15px;">🕯️ 陳聰發</h2>
                    <p style="font-size: 24px; color: #424242; font-weight: bold; line-height: 1.5;">
                        他在旁邊<br>一直幫我們加油喔
                    </p>
                </div>
                """, unsafe_allow_html=True)
        elif search_q == "馬慧斌":
            st.markdown(f"""
                <div class="popup-container" style="background-color: #FFF9C4; border-color: #FBC02D;">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2 style="color: #F57F17; margin-bottom: 15px;">🕯️ 馬慧斌</h2>
                    <p style="font-size: 24px; color: #424242; font-weight: bold; line-height: 1.5;">
                        他在現場喔！<br>你有看到嗎？
                    </p>
                </div>
                """, unsafe_allow_html=True)
        elif search_q == "辛苦了":
            st.snow() # 下起淡淡的雪花，增加氣氛
            st.markdown(f"""
                <div class="popup-container" style="background-color: #E3F2FD; border-color: #2196F3;">
                    <a href="./" target="_self" class="close-x">×</a>
                    <h2 style="color: #1565C0; margin-bottom: 15px;">💙 致 工作人員</h2>
                    <p style="font-size: 20px; color: #0D47A1; font-weight: bold; line-height: 1.4;">
                        各位工作人員辛苦了，<br>這場「千人宴」因為有你們而完美！
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        # --- 正常搜尋邏輯 ---
        else:
            mask = (df_guest['票號_str'].str.contains(search_q, na=False)) | (df_guest['姓名'].str.contains(search_q, na=False))
            found = df_guest[mask]
            
            if not found.empty:
                row = found.iloc[0]
                st.session_state.focus_table = int(row['桌號'])
                st.markdown(f"""
                    <div class="popup-container">
                        <a href="./" target="_self" class="close-x">×</a>
                        <h2 style="color: black; margin: 0;">👋 {row['姓名']} 貴賓</h2>
                        <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                            位置：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                        </p>
                        <a href="#t_{st.session_state.focus_table}" target="_self" class="inner-btn">
                            👉 點我看座位 (自動捲動)
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.session_state.focus_table = None
                st.error(f"❌ 查無資料。")

    # 繪製地圖 (略...)
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None, skip_blank_lines=False)
        num_cols = len(df_map.columns)
        for r_idx, row in df_map.iterrows():
            if row.isnull().all() or "".join([str(v) for v in row if not pd.isna(v)]).strip() == "":
                st.markdown('<div class="spacer-row"></div>', unsafe_allow_html=True)
                continue
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
                            st.markdown(f'<div id="t_{t_num}" class="target-spot"></div>', unsafe_allow_html=True)
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"m_{r_idx}_{c_idx}", type="primary" if t_num == st.session_state.focus_table else "secondary", use_container_width=True)
                        except:
                            st.caption(cell_text)

# Tab 2, 3 維持不變
with tab2:
    st.subheader("📝 登記與驗證功能")
    m_choice = st.radio("模式", ["單筆登記", "連號批次登記", "Excel 批次上傳"], horizontal=True)
    if m_choice == "單筆登記":
        with st.form("s"):
            st.text_input("姓名"); st.number_input("票號", 1); st.form_submit_button("執行")
    elif m_choice == "連號批次登記":
        with st.form("b"):
            st.text_input("代表名"); st.number_input("張數", 1); st.form_submit_button("生成")
    elif m_choice == "Excel 批次上傳":
        st.file_uploader("上傳 Excel", type=["xlsx"])

with tab3:
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    export_data = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button(label="📥 下載總表", data=export_data, file_name="千人宴總表.csv")
    st.markdown('</div>', unsafe_allow_html=True)
    st.dataframe(df_guest, use_container_width=True)