import streamlit as st
import pandas as pd
import os
import streamlit.components.v1 as components

# --- 1. 系統設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session 狀態
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None
if 'do_scroll' not in st.session_state:
    st.session_state.do_scroll = False

# --- 🎨 核心 CSS ---
st.markdown("""
    <style>
    div.stButton > button:first-child { height: 3em !important; margin-top: 28px !important; }
    
    /* 金黃色小框 */
    .popup-container {
        position: fixed; top: 40%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; padding: 40px 20px 80px 20px;
    }
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 30px; color: #555; text-decoration: none; font-weight: bold; cursor: pointer;
    }
    
    /* 地圖間距壓縮 */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    [data-testid="stHorizontalBlock"] { margin-top: -12px !important; margin-bottom: -12px !important; }

    .label-box-fixed {
        background-color: var(--label-color); color: white; text-align: center; 
        padding: 15px !important; border-radius: 10px; font-weight: bold; 
        font-size: 22px !important; margin: 20px 0 !important; width: 100%;
    }
    
    /* 錨點偏移設定 */
    .target-spot { scroll-margin-top: 350px; }
    
    /* 高亮桌子 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold; transform: scale(1.1);
    }
    
    .popup-btn-pos {
        position: fixed; top: 58%; left: 50%; transform: translate(-50%, -50%);
        z-index: 10000; width: 280px;
    }
    </style>
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
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 登記與防呆驗證", "📊 數據中心"])

with tab1:
    c_in, c_bt = st.columns([4, 1])
    search_q = c_in.text_input("輸入票號或姓名搜尋：", placeholder="例如：1351 或 徐鳳慈", key="search_main")
    if c_bt.button("🔍 查詢"):
        st.session_state.do_scroll = False

    if search_q:
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
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('<div class="popup-btn-pos">', unsafe_allow_html=True)
            if st.button("👉 點我看座位 (自動捲動)", key="scroll_btn"):
                st.session_state.do_scroll = True
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.do_scroll:
                components.html(f"""<script>window.parent.document.getElementById('t_{st.session_state.focus_table}').scrollIntoView({{behavior: 'smooth', block: 'start'}});</script>""", height=0)
                st.session_state.do_scroll = False # 捲動後立刻重置，避免干擾 Tab 2

    # 繪製地圖
    if os.path.exists(LAYOUT_FILE):
        df_map = pd.read_csv(LAYOUT_FILE, header=None)
        num_cols = len(df_map.columns)
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
                            st.markdown(f'<div id="t_{t_num}" class="target-spot"></div>', unsafe_allow_html=True)
                            st.button(f"VIP{t_num}" if t_num <= 3 else str(t_num), key=f"m_{r_idx}_{c_idx}", type="primary" if t_num == st.session_state.focus_table else "secondary", use_container_width=True)
                        except:
                            st.caption(cell_text)

with tab2:
    st.subheader("📝 登記功能與防呆驗證")
    reg_mode = st.radio("登記模式", ["單筆輸入", "連號批次登記", "Excel 批次上傳"], horizontal=True)
    
    if reg_mode == "單筆輸入":
        with st.form("single_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            s_name = c1.text_input("姓名")
            s_phone = c1.text_input("聯絡電話")
            s_ticket = c2.number_input("票號", 1, 2000)
            s_seller = c2.text_input("售票負責人")
            s_table = c3.number_input("預計桌號", 1, 200)
            if st.form_submit_button("執行單筆登記驗證"):
                st.success(f"✅ {s_name} (票號 {s_ticket}) 驗證成功！")
                st.code(f"{s_name}\t{s_phone}\t{s_ticket}\t{s_seller}\t{s_table}")

    elif reg_mode == "連號批次登記":
        with st.form("batch_form"):
            c1, c2 = st.columns(2)
            b_name = c1.text_input("代表姓名"); b_seller = c2.text_input("負責人")
            b_start = c1.number_input("起始票號", 1); b_count = c2.number_input("張數", 1)
            b_table = st.number_input("預計桌號", 1)
            if st.form_submit_button("批次生成驗證"):
                t_range = range(int(b_start), int(b_start) + int(b_count))
                st.code("\n".join([f"{b_name}\t電話\t{t}\t{b_seller}\t{b_table}" for t in t_range]))

    elif reg_mode == "Excel 批次上傳":
        st.file_uploader("上傳 Excel (.xlsx)", type=["xlsx"])

with tab3:
    st.subheader("📊 數據中心")
    st.dataframe(df_guest, use_container_width=True)