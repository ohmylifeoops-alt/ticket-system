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

# 自動算桌次邏輯：票號每 10 人一桌
def calculate_table(ticket_number):
    try:
        return (int(ticket_number) - 1) // 10 + 1
    except:
        return 0

# --- 2. 繪製地圖函數 (完全遵循您的 Excel 佈局) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"找不到佈局檔案: {LAYOUT_FILE}，請確保此 CSV 檔已上傳至 GitHub。")
        return

    # 讀取 Excel 網格數據
    df_map = pd.read_csv(LAYOUT_FILE, header=None)

    st.markdown("### 🏟️ 場地實景佈局圖")
    
    # 逐列(Row)掃描 Excel 格子
    for r_idx, row in df_map.iterrows():
        cols = st.columns(10) 
        for c_idx, val in enumerate(row):
            if c_idx >= 10: break 
            
            with cols[c_idx]:
                if pd.isna(val) or str(val).strip() == "":
                    st.write("")
                elif str(val).strip() == "舞台":
                    st.markdown("<div style='background-color:#d32f2f; color:white; text-align:center; padding:5px; border-radius:5px; font-weight:bold; font-size:12px;'>舞台</div>", unsafe_allow_html=True)
                elif str(val).strip() == "電視":
                    st.markdown("<div style='background-color:#333; color:white; text-align:center; padding:5px; border-radius:5px; font-size:12px;'>📺</div>", unsafe_allow_html=True)
                else:
                    try:
                        # 嘗試轉為整數桌號
                        table_num = int(float(val))
                        is_active = table_num in highlighted_tables
                        # 確保按鈕括號完整閉合
                        st.button(
                            f"{table_num}", 
                            key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                            type="primary" if is_active else "secondary", 
                            use_container_width=True
                        )
                    except (ValueError, TypeError):
                        # 如果是其他備註文字
                        st.caption(str(val))

# --- 3. 介面主要內容 ---
st.title("🎟️ 宴會桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 實景地圖搜尋", "📝 新增賓客登記", "📊 所有數據管理"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話、票號或售出者：", key="main_search")
    highlighted_list = []
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        # 獲取自動生成的桌號
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
                # 自動計算並儲存桌號
                t_num = calculate_table(ticket_v)
                new_row = pd.DataFrame({
                    "姓名": [name_v], 
                    "聯絡電話": [phone_v], 
                    "票號": [ticket_v], 
                    "售出者": [seller_v],
                    "桌號": [t_num] 
                })
                df_guest = pd.concat([df_guest, new_row], ignore_index=True)
                df_guest.to_csv(GUEST_FILE, index=False)
                st.success(f"✅ 登記成功！{name_v} 自動分配至第 {t_num} 桌")
            else:
                st.warning("請輸入姓名")

with tab3:
    st.subheader("📊 完整名單一覽表")
    st.dataframe(df_guest.sort_values(by="桌號"), use_container_width=True)