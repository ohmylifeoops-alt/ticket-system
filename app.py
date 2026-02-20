import streamlit as st
import pandas as pd
import os

# 設定檔案名稱
FILE_NAME = 'guest_data.csv'

# 核心邏輯：計算桌次
def calculate_table(ticket_number):
    # 邏輯：(票號 - 1) // 10 + 1
    # 例如：票號 10 -> (9 // 10) + 1 = 1 桌
    # 例如：票號 11 -> (10 // 10) + 1 = 2 桌
    return (int(ticket_number) - 1) // 10 + 1

# 設定頁面標題
st.set_page_config(page_title="票號桌次管理系統", page_icon="🎟️")
st.title("🎟️ 票號桌次管理系統")

# 1. 讀取或建立資料庫 (CSV)
if os.path.exists(FILE_NAME):
    df = pd.read_csv(FILE_NAME)
else:
    # 初始化空的 DataFrame
    df = pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 使用分頁 (Tabs) 區分功能
tab1, tab2 = st.tabs(["📝 新增資料 (自動算桌次)", "🔍 搜尋與查詢"])

# --- 功能一：新增資料 ---
with tab1:
    with st.form("entry_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("姓名")
            ticket = st.number_input("票號 (1-2000)", min_value=1, max_value=2000, step=1)
        with col2:
            phone = st.text_input("聯絡電話")
            seller = st.text_input("售出者")
            
        submitted = st.form_submit_button("新增並計算桌次")
        
        if submitted:
            # 驗證票號是否重複
            if not df.empty and ticket in df['票號'].values:
                st.error(f"錯誤：票號 {ticket} 已經存在於資料庫中！")
            elif not name:
                st.warning("請輸入姓名")
            else:
                # 自動計算桌次
                table_num = calculate_table(ticket)
                
                # 建立新資料列
                new_data = pd.DataFrame({
                    "姓名": [name], 
                    "聯絡電話": [phone], 
                    "票號": [ticket], 
                    "售出者": [seller],
                    "桌號": [table_num]
                })
                
                # 合併並存檔
                df = pd.concat([df, new_data], ignore_index=True)
                df.to_csv(FILE_NAME, index=False)
                
                st.success(f"✅ 已新增！ {name} (票號 {ticket}) 分配在 **第 {table_num} 桌**")

# --- 功能二：搜尋資料 ---
with tab2:
    st.subheader("快速查詢")
    search_term = st.text_input("請輸入姓名、電話、票號或桌號進行搜尋：")
    
    if search_term:
        # 模糊搜尋所有欄位
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
        results = df[mask]
        
        if not results.empty:
            st.info(f"找到 {len(results)} 筆資料：")
            st.dataframe(results, use_container_width=True)
        else:
            st.warning("找不到符合的資料。")
    else:
        # 顯示所有資料（依票號排序）
        st.write("目前所有名單：")
        if not df.empty:
            df = df.sort_values(by="票號")
        st.dataframe(df, use_container_width=True)

    # 顯示統計資訊
    st.markdown("---")
    st.caption(f"目前總人數：{len(df)} 人 | 已使用桌數：{df['桌號'].nunique()} 桌")
import streamlit as st

def draw_seating_chart(highlighted_tables):
    # --- 區域一：入口區 (30桌) ---
    st.subheader("🚪 入口區域 (第 141 - 170 桌)")
    cols_30 = st.columns(5)
    for i, num in enumerate(range(141, 171)):
        with cols_30[i % 5]:
            btn_type = "primary" if num in highlighted_tables else "secondary"
            st.button(f"{num}", key=f"t{num}", type=btn_type, use_container_width=True)

    st.write("↓ 往內走 (經過看板/電視牆) ↓")

    # --- 區域二：中間區 (40桌) ---
    st.subheader("📺 中間區域 (第 101 - 140 桌)")
    cols_40 = st.columns(5)
    for i, num in enumerate(range(101, 141)):
        with cols_40[i % 5]:
            btn_type = "primary" if num in highlighted_tables else "secondary"
            st.button(f"{num}", key=f"t{num}", type=btn_type, use_container_width=True)

    st.write("↓ 抵達核心區 ↓")

    # --- 區域三：舞台核心區 (100桌) ---
    st.markdown("<h2 style='text-align: center; color: red;'>🚩 舞台位置 🚩</h2>", unsafe_allow_html=True)
    
    # 舞台第一排：3, 1, 2 特別排法
    st.write("### 舞台正前方 (第一排)")
    c1, c2, c3 = st.columns([1, 1, 1])
    def stage_btn(num):
        t = "primary" if num in highlighted_tables else "secondary"
        st.button(f"第 {num} 桌", key=f"t{num}", type=t, use_container_width=True)
    
    with c1: stage_btn(3) # 左
    with c2: stage_btn(1) # 中
    with c3: stage_btn(2) # 右

    # 剩下的 97 桌 (依照 10x10 扣除前 3 桌後的排法)
    # 為了美觀，我們從第 4 桌開始，每排 10 桌繪製
    st.write("### 核心區後方 (每排 10 桌)")
    remaining_100 = list(range(4, 101))
    for i in range(0, len(remaining_100), 10):
        cols = st.columns(10)
        batch = remaining_100[i:i+10]
        for idx, num in enumerate(batch):
            with cols[idx]:
                t = "primary" if num in highlighted_tables else "secondary"
                st.button(f"{num}", key=f"t{num}", type=t, use_container_width=True)
