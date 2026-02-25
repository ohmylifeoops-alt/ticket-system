import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統效能與設定 ---
# 請確保 GitHub 上的 CSV 檔名與此處完全一致
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

# 初始化 Session State
if 'focus_table' not in st.session_state:
    st.session_state.focus_table = None

# --- 🎨 完美排版 CSS 修正 ---
st.markdown("""
    <style>
    /* 1. 搜尋區域對齊：讓放大鏡按鈕跟輸入框底部齊平 */
    div.stButton > button:first-child {
        height: 3em !important;
        margin-top: 28px !important;
    }

    /* 2. 浮動視窗絕對排版 (全 HTML 結構) */
    .popup-container {
        position: fixed; top: 35%; left: 50%; transform: translate(-50%, -50%);
        width: 380px; background-color: #FFD700; border-radius: 20px;
        box-shadow: 0px 20px 60px rgba(0,0,0,0.5); z-index: 9999;
        text-align: center; border: 4px solid #DAA520; 
        padding: 45px 20px 30px 20px; animation: fadeIn 0.3s forwards;
    }
    
    /* 右上角叉叉 - 使用 HTML 連結模擬關閉 */
    .close-x {
        position: absolute; top: 10px; right: 20px;
        font-size: 35px; color: #555; text-decoration: none;
        font-family: Arial, sans-serif; font-weight: bold;
        line-height: 1;
    }
    .close-x:hover { color: #000; }

    /* 框內「點我看座位」按鈕樣式 */
    .anchor-btn {
        display: inline-block; background-color: #000; color: #fff !important;
        padding: 15px 30px; border-radius: 10px; text-decoration: none;
        font-size: 18px; font-weight: bold; width: 85%; margin-top: 15px;
    }
    
    /* 自動捲動置中偏移量 */
    .table-anchor { scroll-margin-top: 350px; }
    
    /* 搜尋到的桌子變亮黃色 */
    .stButton > button[kind="primary"] {
        background-color: #FFEB3B !important; color: #000 !important;
        border: 3px solid #FBC02D !important; font-weight: bold;
        transform: scale(1.15);
    }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
    """, unsafe_allow_html=True)

# 讀取雲端資料
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

# --- 2. 實景地圖繪製 ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到場地佈局檔案：{LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    highlight_set = set(highlighted_tables)
    
    st.markdown("### 🏟️ 千人宴場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        # 繪製標籤列 (舞台、入口等)
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else "#2E7D32"
            st.markdown(f"""<div style='background-color:{color}; color:white; text-align:center; 
                padding:12px; border-radius:10px; font-weight:bold; font-size:20px; margin: 10px 0;'>
                {row_content}</div>""", unsafe_allow_html=True)
            continue

        # 繪製桌位按鈕
        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text not in ["", "nan"]:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        
                        # 特殊顯示 VIP
                        display_name = str(table_num)
                        if table_num == 1: display_name = "VIP1"
                        elif table_num == 2: display_name = "VIP2"
                        elif table_num == 3: display_name = "VIP3"
                        
                        # 設置錨點供自動捲動使用
                        st.markdown(f"<div id='table_{table_num}' class='table-anchor'></div>", unsafe_allow_html=True)
                        
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

with tab1:
    # 搜尋 UI：文字框與放大鏡對齊
    c_input, c_btn = st.columns([4, 1])
    with c_input:
        search_q = st.text_input("請輸入票號查詢：", placeholder="請輸入票號數字，例如：1351", key="search_main")
    with c_btn:
        search_trigger = st.button("🔍 查詢")

    if search_q or search_trigger:
        try:
            q_num = int(search_q)
            found = df_guest[df_guest['票號'] == q_num]
            
            if not found.empty:
                first_row = found.iloc[0]
                st.session_state.focus_table = int(first_row['桌號'])
                
                # --- 🎨 完美浮動視窗：純 HTML 排版 ---
                # 點擊叉叉導向 "./" 會刷新狀態並關閉小框，不跳新視窗
                st.markdown(f"""
                    <div class="popup-container">
                        <a href="./" target="_self" class="close-x">×</a>
                        <h2 style="color: black; margin: 0;">👋 {first_row['姓名']} 貴賓</h2>
                        <p style="font-size: 28px; color: #d32f2f; font-weight: bold; margin: 20px 0;">
                            您的位置在：第 {st.session_state.focus_table if st.session_state.focus_table > 3 else 'VIP' + str(st.session_state.focus_table)} 桌
                        </p>
                        <a href="#table_{st.session_state.focus_table}" target="_self" class="anchor-btn">
                            👉 點我看座位 (自動定位)
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.session_state.focus_table = None
                if search_q: st.error("查無此票號，請重新確認。")
        except:
            if search_q: st.error("請輸入正確的數字票號。")

    draw_seating_chart([st.session_state.focus_table] if st.session_state.focus_table else [])

with tab2:
    st.subheader("📝 登記與驗證")
    reg_mode = st.radio("登記方式：", ["單筆輸入", "連號批次登記", "Excel 批次上傳"], horizontal=True)
    
    if reg_mode == "單筆輸入":
        with st.form("single_form", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            with c1: name = st.text_input("姓名"); phone = st.text_input("電話")
            with c2: seller = st.text_input("售票者"); ticket = st.number_input("票號", 1, 2000)
            with c3: table = st.number_input("預計桌號", 1, 200)
            if st.form_submit_button("執行單筆驗證"):
                st.balloons()
                st.success(f"✅ {name} 驗證成功 (票號 {ticket})")
                
    elif reg_mode == "連號批次登記":
        with st.form("batch_form"):
            c1, c2 = st.columns(2)
            name_b = c1.text_input("代表姓名"); seller_b = c2.text_input("售票負責人")
            start_t = c2.number_input("起始票號", 1, 2000); count_t = c2.number_input("張數", 1, 100)
            target_t = st.number_input("統一桌號", 1, 200)
            if st.form_submit_button("批次防呆驗證"):
                t_range = range(int(start_t), int(start_t) + int(count_t))
                st.code("\n".join([f"{name_b}\t聯絡電話\t{t}\t{seller_b}\t{target_t}" for t in t_range]))

    else:
        st.file_uploader("上傳 Excel (.xlsx)", type=["xlsx"])

with tab3:
    st.subheader("📊 數據中心")
    csv_data = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載目前資料庫 (CSV)", csv_data, "千人宴總表.csv", "text/csv")
    st.dataframe(df_guest, use_container_width=True)