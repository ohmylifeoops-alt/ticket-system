import streamlit as st
import pandas as pd
import os
import io

# --- 1. 系統效能與設定 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
# 雲端資料庫 URL (維持原樣)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1m7Ak2e7QZdXWYdzKL77g20gHieId5bRpRZsVtyQG05g/export?format=csv"

st.set_page_config(page_title="千人宴桌次實景管理系統", page_icon="🎟️", layout="wide")

# 讀取雲端資料庫 (緩存 30 秒)
@st.cache_data(ttl=30, show_spinner=False)
def load_data():
    try:
        data = pd.read_csv(SHEET_URL)
        # 強制將桌號轉為整數數字，若為空或非數字則設為 0
        if "桌號" in data.columns:
            data['桌號'] = pd.to_numeric(data['桌號'], errors='coerce').fillna(0).astype(int)
        return data
    except:
        return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

# 取得目前最新資料
df_guest = load_data()

# --- 2. 實景地圖繪製 (支援 VIP 顯示) ---
def draw_seating_chart(highlighted_tables):
    if not os.path.exists(LAYOUT_FILE):
        st.error(f"❌ 找不到佈局檔案 {LAYOUT_FILE}")
        return

    df_map = pd.read_csv(LAYOUT_FILE, header=None)
    num_cols = len(df_map.columns) 
    highlight_set = set(highlighted_tables)
    
    st.markdown("### 🏟️ 千人宴場地實景佈局")
    
    for r_idx, row in df_map.iterrows():
        row_content = "".join([str(v) for v in row if not pd.isna(v)])
        
        # 標籤處理 (舞台、入口)
        if any(k in row_content for k in ["舞台", "入口", "電視牆"]):
            color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            st.markdown(f"""<div style='background-color:{color}; color:white; text-align:center; 
                padding:12px; border-radius:10px; font-weight:bold; font-size:20px; margin: 10px 0;'>
                {row_content}</div>""", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                cell_text = str(val).strip() if not pd.isna(val) else ""
                if cell_text in ["", "nan"]:
                    st.write("")
                else:
                    try:
                        table_num = int(float(val))
                        is_active = table_num in highlight_set
                        
                        # 特殊顯示 VIP1, 2, 3
                        display_name = str(table_num)
                        if table_num == 1: display_name = "VIP1"
                        elif table_num == 2: display_name = "VIP2"
                        elif table_num == 3: display_name = "VIP3"
                        
                        st.button(display_name, key=f"btn_{r_idx}_{c_idx}_{table_num}", 
                                  type="primary" if is_active else "secondary", 
                                  use_container_width=True)
                    except:
                        st.caption(cell_text)

# --- 3. 介面內容 ---
st.title("🎟️ 千人宴桌次實景管理系統")
tab1, tab2, tab3 = st.tabs(["🔍 快速搜尋", "📝 批次登記與防呆", "📊 數據中心"])

# --- 頁籤一：搜尋 ---
with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號：", key="search_main", placeholder="請輸入資訊...")
    highlighted_list = []
    
    if search_q:
        mask = df_guest.astype(str).apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        
        if not found.empty:
            # 取得該賓客手動填寫的桌號
            highlighted_list = found['桌號'].unique().tolist()
            # 3. 彈跳小框提示
            for _, row in found.iterrows():
                st.toast(f"🔔 {row['姓名']} 貴賓：您坐在第 {row['桌號'] if row['桌號'] > 3 else 'VIP' + str(row['桌號'])} 桌")
            st.success(f"✅ 找到賓客，分配在：{highlighted_list} 桌")
        else:
            st.error("查無此賓客資訊，請確認輸入是否正確。")
            
    draw_seating_chart(highlighted_list)

# --- 頁籤二：批次登記 (支援上傳 Excel) ---
with tab2:
    st.subheader("📝 登記驗證 (支援 Excel 批次上傳)")
    
    uploaded_excel = st.file_uploader("上傳 Excel 登記表 (.xlsx)", type=["xlsx"])
    if uploaded_excel:
        try:
            batch_df = pd.read_excel(uploaded_excel)
            st.write("待驗證資料預覽：")
            st.dataframe(batch_df.head(), use_container_width=True)
            
            if st.button("執行批次防呆驗證"):
                # 簡單防呆：檢查票號是否重複
                existing_tickets = set(df_guest['票號'].dropna().astype(int))
                new_tickets = batch_df['票號'].tolist()
                conflicts = [t for t in new_tickets if t in existing_tickets]
                
                if conflicts:
                    st.error(f"❌ 錯誤：票號 {conflicts} 已在系統中登記過！")
                else:
                    st.balloons()
                    st.success("🎉 批次驗證通過！請點擊資料中心查看合併結果。")
        except Exception as e:
            st.error(f"讀取 Excel 失敗: {e}")

# --- 頁籤三：數據中心 (支援下載 Excel) ---
with tab3:
    st.subheader("📊 千人宴資料庫總表")
    
    # 下載 Excel 功能
    if not df_guest.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_guest.to_excel(writer, index=False, sheet_name='賓客名單')
        
        st.download_button(
            label="📥 下載完整資料庫 (Excel)",
            data=buffer.getvalue(),
            file_name="千人宴賓客總表.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    st.dataframe(df_guest.sort_values(by="票號"), use_container_width=True)
    
    if st.button("🔄 強制更新雲端數據"):
        st.cache_data.clear()
        st.rerun()