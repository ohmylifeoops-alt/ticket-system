import streamlit as st
import pandas as pd
import os

# --- 1. 系統設定與檔案讀取 ---
LAYOUT_FILE = '排桌.xlsx - 工作表1.csv' 
LOCAL_DB = "guest_data_db.csv"

st.set_page_config(page_title="宴會實景導引系統", page_icon="🎟️", layout="wide")

# 讀取資料邏輯：優先讀取上傳過的資料庫
def load_data():
    if os.path.exists(LOCAL_DB):
        try:
            return pd.read_csv(LOCAL_DB).astype(str)
        except:
            pass
    # 若無資料，建立空白範本欄位
    return pd.DataFrame(columns=["姓名", "聯絡電話", "票號", "售出者", "桌號"])

df_guest = load_data()

# 💡 核心：自動轉化顯示標籤 (1 -> 1~10)
def get_display_label(val):
    try:
        # 移除可能產生的 .0 並轉數字
        n = int(float(str(val).strip()))
        if 1 <= n <= 200: # 假設桌號在 200 內皆為區間模式
            return f"{(n-1)*10+1}~{n*10}"
    except:
        pass
    return str(val) # 特殊編號 (如 855) 則原樣顯示

# --- 2. 實景地圖 (智慧顯示版) ---
def draw_seating_chart(highlighted_ids):
    if not os.path.exists(LAYOUT_FILE):
        st.error("❌ 找不到佈局 CSV 檔案，請確認已上傳至 GitHub。")
        return
    
    df_map = pd.read_csv(LAYOUT_FILE, header=None).astype(str)
    num_cols = len(df_map.columns)
    # 清理高亮集合
    highlight_set = {str(x).strip().replace(".0", "") for x in highlighted_ids}

    st.markdown("### 🏟️ 場地實景佈局圖")
    for r_idx, row in df_map.iterrows():
        # 標籤辨識 (舞台/入口...)
        row_content = "".join([val for val in row if val != "nan"])
        if any(k in row_content for k in ["舞台", "入口", "電視", "收銀"]):
            color = "#FF4B4B" if "舞台" in row_content else ("#333333" if "電視" in row_content else "#2E7D32")
            st.markdown(f"<div style='background-color:{color}; color:white; text-align:center; padding:12px; border-radius:10px; font-weight:bold; font-size:20px; margin: 10px 0;'>{row_content}</div>", unsafe_allow_html=True)
            continue

        cols = st.columns(num_cols) 
        for c_idx, val in enumerate(row):
            with cols[c_idx]:
                raw_id = val.strip().replace(".0", "") if val != "nan" else ""
                if raw_id:
                    display_text = get_display_label(raw_id)
                    is_active = raw_id in highlight_set
                    st.button(
                        display_text, 
                        key=f"btn_{r_idx}_{c_idx}_{raw_id}", 
                        type="primary" if is_active else "secondary", 
                        use_container_width=True
                    )

# --- 3. 介面內容 ---
st.title("🎟️ 宴會實景導引系統 (批次管理版)")
tab1, tab2 = st.tabs(["🔍 快速搜尋", "📊 數據更新與下載"])

with tab1:
    search_q = st.text_input("🔍 搜尋姓名、電話或票號 (地圖會自動對應發亮)：")
    highlighted_list = []
    if search_q and not df_guest.empty:
        # 全表模糊搜尋
        mask = df_guest.apply(lambda x: x.str.contains(search_q, case=False)).any(axis=1)
        found = df_guest[mask]
        if not found.empty:
            highlighted_list = found['桌號'].tolist()
            labels = [get_display_label(x) for x in set(highlighted_list)]
            st.success(f"✅ 找到賓客！地圖標記：{', '.join(labels)}")
        else:
            st.warning("查無資料")
    draw_seating_chart(highlighted_list)

with tab2:
    st.subheader("📥 步驟 1：下載修改範本")
    st.write("請下載目前的清單，在 Excel 裡修改「桌號」欄位。")
    # 下載目前資料
    csv_temp = df_guest.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 下載賓客清單 (Excel/CSV 範本)",
        data=csv_temp,
        file_name="宴會名單總表.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("📤 步驟 2：上傳更新後的檔案")
    st.info("上傳後，系統會直接取代現有資料。請確保欄位名稱包含：姓名、票號、桌號。")
    uploaded_file = st.file_uploader("選擇您填寫好的 CSV 檔案", type="csv")
    
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        # 存入本地庫，這樣下次開啟也會是這份資料
        new_df.to_csv(LOCAL_DB, index=False)
        st.success("✅ 資料庫更新成功！")
        if st.button("點此重新整理頁面"):
            st.rerun()

    st.divider()
    st.subheader("📋 目前資料庫內容預覽")
    st.dataframe(df_guest, use_container_width=True)