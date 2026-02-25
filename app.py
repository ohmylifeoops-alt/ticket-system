import streamlit as st
import pandas as pd
import io

# 設定頁面標題
st.set_page_config(page_title="VIP 座位管理系統", layout="wide")

st.title("🎟️ VIP 座位與桌次查詢系統")
st.markdown("---")

# 1. 側邊欄：上傳與下載功能
with st.sidebar:
    st.header("數據管理")
    uploaded_file = st.file_uploader("上傳座位表 (CSV)", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.success("檔案上傳成功！")
        
        # 轉成 CSV 供下載的函式
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8-sig') # 使用 utf-8-sig 確保 Excel 開啟不亂碼

        csv_data = convert_df(df)
        st.download_button(
            label="下載當前資料庫 (CSV)",
            data=csv_data,
            file_name='current_seat_layout.csv',
            mime='text/csv',
        )

# 2. 主要邏輯：資料顯示
if uploaded_file is not None:
    # 確保資料依照桌號排序
    df = df.sort_values(by=['VIP_Level', 'Table_No'])

    # 建立分頁或標籤來區分 VIP1, VIP2, VIP3
    vip_types = ["VIP1", "VIP2", "VIP3"]
    tabs = st.tabs(vip_types)

    for i, vip_level in enumerate(vip_types):
        with tabs[i]:
            # 篩選該 VIP 等級的資料
            vip_df = df[df['VIP_Level'] == vip_level]
            
            if vip_df.empty:
                st.info(f"目前沒有 {vip_level} 的資料")
                continue

            # 核心邏輯：依照桌號 (Table_No) 分組，解決非連號問題
            tables = vip_df.groupby('Table_No')

            # 使用欄位 (Columns) 佈局，讓畫面更直覺
            cols = st.columns(3) # 每一列顯示 3 桌
            
            for idx, (table_id, group) in enumerate(tables):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.subheader(f"第 {table_id} 桌")
                        
                        # 顯示該桌所有人名或編號 (不管連不連號，只要在這桌的都列出來)
                        # 我們將座號轉為字串並用逗號隔開
                        seats = group['Seat_ID'].astype(str).tolist()
                        names = group['Name'].tolist()
                        
                        # 組合顯示內容
                        display_text = ""
                        for s, n in zip(seats, names):
                            display_text += f"🔹 **{s}** : {n}  \n"
                        
                        st.write(display_text)
                        st.caption(f"共計: {len(group)} 人")

else:
    st.warning("請先在左側上傳 CSV 檔案以開始操作。")
    # 這裡可以放一個範例表格讓用戶參考格式
    st.info("建議 CSV 格式：姓名(Name), 座號(Seat_ID), 桌號(Table_No), 等級(VIP_Level)")