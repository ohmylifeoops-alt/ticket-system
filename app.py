import streamlit as st
import pandas as pd
import os

# --- 1. 初始化與檔案設定 ---
GUEST_FILE = 'guest_data.csv'
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv'

st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

# 讀取賓客資料庫
if os.path.exists(GUEST_FILE):
    df_guest = pd.read_csv(GUEST_FILE)
else:
    df_guest = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 自動算桌次邏輯
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (強化視覺標籤版) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案: {LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    st.markdown("### 🏟️ 場地實景佈局圖")
    
    for r_idx, row in df_map.iterrows():
        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
            
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                
                if cell_text == "":
                    st.write("")
                
                # --- 🚩 強化標籤：舞台 ---
                elif "舞台" in cell_text:
                    st.markdown("""
                        <div style='background-color:#FF4B4B; color:white; text-align:center; 
                        padding:10px 2px; border-radius:5px; font-weight:bold; font-size:18px; 
                        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);'>🚩 舞台</div>
                    """, unsafe_allow_html=True)
                
                # --- 🚪 強化標籤：入口 ---
                elif "入口" in cell_text:
                    st.markdown("""
                        <div style='background-color:#2E7D32; color:white; text-align:center; 
                        padding:10px 2px; border-radius:5px; font-weight:bold; font-size:18px; 
                        border: 2px solid #1B5E20;'>🚪 入口</div>
                    """, unsafe_allow_html=True)
                
                # --- 📺 強化標籤：電視 ---
                elif "電視" in cell_text:
                    st.markdown("""
                        <div style='background-color:#333333; color:white; text-align:center; 
                        padding:8px 2px; border-radius:5px; font-size:16px;'>📺 電視</div>
                    """, unsafe_allow_html=True)
                
                # --- 🔘 桌號按鈕 ---
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlighted_tables
                        st.button(
                            f"{table_num}", 
                            key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                            type="primary" if is_active else "secondary", 
                            use_container_width=True
                        )
                    except (ValueError, TypeError):
                        st.write(f"**{cell_text}**")

# --- 3. 介面主要內容 ---
st.title("🎟️ 宴會桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 實景地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話、票號或售出者：", key="main_search")
    highlighted_list = []
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        highlighted_list = df_guest[mask]['桌號'].tolist()
        if highlighted_list:
            st.success(f"找到相關賓客，位於第 {list(set(highlighted_list))} 桌")
    
    draw_seating_chart(highlighted_list)

with tab2:
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("📝 新增賓客登記")
        col_a, col_b = st.columns(2)
        with col_a:
            name_v = st.text_input("姓名")
            ticket_v = st.number_input("票號 (1-1700)", min_value=1, max_value=1700, step=1)
        with col_b:
            phone_v = st.text_input("聯絡電話")
            seller_v = st.text_input("售出者")
        
        if st.form_submit_button("確認提交"):
            if name_v:
                t_num = calculate_table(ticket_v)
                new_row = pd.DataFrame({
                    "姓名": [name_v], "聯絡電話": [phone_v], "票號": [ticket_v], "售出者": [seller_v], "桌號": [t_num] 
                })
                df_guest = pd.concat([df_guest, new_row], ignore_index=True)
                df_guest.to_csv(GUEST_FILE, index=False)
                st.success(f"✅ 登記成功！{name_v} 自動分配至第 {t_num} 桌")
            else:
                st.warning("請輸入姓名")

with tab3:
    st.subheader("📊 完整名單一覽表")
    st.dataframe(df_guest.sort_values(by="桌號"), use_container_width=True)