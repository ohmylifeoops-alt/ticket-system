import streamlit as st
import pandas as pd
import os

# --- 1. 初始化與檔案讀取 ---
FILE_NAME = 'guest_data.csv'
st.set_page_config(page_title="宴會桌次實景系統", page_icon="🎟️", layout="wide")

if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

def calculate_table(ticket_number):
    return (int(ticket_number) - 1) // 10 + 1

# --- 2. 繪製地圖函數 (地毯式檢查：確保縮排完全正確) ---
def draw_seating_chart(highlighted_tables):
    def draw_btn(num):
        is_active = num in highlighted_tables
        st.button(f"{num}", key=f"map_btn_{num}", type="primary" if is_active else "secondary", use_container_width=True)

    # === A. 舞台核心區 (1-100號) ===
    st.markdown("<h2 style='text-align: center; color: white; background-color: #d32f2f; padding: 10px; border-radius: 10px;'>🚩 舞台 STAGE 🚩</h2>", unsafe_allow_html=True)
    
    st.write("⬅️ 上菜方向 | 舞台第一排 (核心排序)")
    row1_order = [10, 9, 8, 7, 3, 1, 2, 4, 5, 6]
    cols1 = st.columns(10)
    for idx, num in enumerate(row1_order):
        with cols1[idx]:
            draw_btn(num)

    st.write("---")
    st.caption("30尺龍帳區 (11 - 100 號)")
    for i in range(11, 101, 10):
        # 這裡縮排已精確校正
        if i > 11 and (i - 11) % 20 == 0:
            st.markdown("<div style='text-align: center; color: #999; margin: 15px 0; border-top: 1px dashed #ccc;'>↑ ⬅️ 走道 AISLE ⬅️ ↑</div>", unsafe_allow_html=True)
        cols = st.columns(10)
        for j in range(10):
            num = i + j
            if num <= 100:
                with cols[j]:
                    draw_btn(num)

    # === B. 電視牆分界 ===
    st.markdown("<div style='text-align: center; padding: 20px; background-color: #333; color: white; margin: 30px 0; border-radius: 5px;'>📺 電視牆 & 看板區域 📺</div>", unsafe_allow_html=True)

    # === C. 電視牆後 5 欄區 (101-125 號) ===
    st.write("### 📺 電視牆後區 (101 - 125 號)")
    for i in range(101, 126, 5):
        cols_5 = st.columns(5)
        for j in range(5):
            num = i + j
            if num <= 125:
                with cols_5[j]:
                    draw_btn(num)

    # === D. 入口前 10 欄區 (126-170 號) ===
    st.write("### 🚪 入口前大區 (126 - 170 號)")
    for i in range(126, 171, 10):
        cols_10 = st.columns(10)
        for j in range(10):
            num = i + j
            if num <= 170:
                with cols_10[j]:
                    draw_btn(num)
    
    st.markdown("<br><h2 style='text-align: center; border: 2px solid black; padding: 10px;'>🚪 入口 ENTRANCE</h2>", unsafe_allow_html=True)

# --- 3. 分頁介面邏輯 ---
st.title("宴會桌次管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 實景地圖搜尋", "📝 賓客登記", "📊 名單管理"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話、票號：", key="main_search_box")
    highlighted_list = []
    if search_q:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        highlighted_list = df[mask]['桌號'].tolist()
        if highlighted_list:
            st.success(f"找到賓客，位於第 {list(set(highlighted_list))} 桌")
    draw_seating_chart(highlighted_list)

with tab2:
    with st.form("entry_form_v5", clear_on_submit=True):
        st.subheader("新增登記")
        c_a, c_b = st.columns(2)
        with c_a:
            name_val = st.text_input("姓名")
            ticket_val = st.number_input("票號", min_value=1, max_value=2000, step=1)
        with c_b:
            phone_val = st.text_input("聯絡電話")
            seller_val = st.text_input("售出者")
        if st.form_submit_button("確認提交"):
            if name_val:
                t_n = calculate_table(ticket_val)
                new_data = pd.DataFrame({"姓名":[name_val],"聯絡電話":[phone_val],"票號":[ticket_val],"售出者":[seller_val],"桌號":[t_n]})
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                st.success(f"✅ 已登記成功！分配在第 {t_n} 桌")
            else:
                st.warning("請輸入姓名")

with tab3:
    st.subheader("名單一覽表")
    st.dataframe(df.sort_values(by="桌號"), use_container_width=True)