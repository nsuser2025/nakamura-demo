import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="CSV Data Probe Tool", layout="wide")

st.title("📊 CSVデータ・プローブツール")
st.markdown("CSVを読み込み、グラフ上の〇点を動かして値を読み取ります。")

# 1. CSVファイルのアップロード
uploaded_file = st.sidebar.file_uploader("CSVファイルをアップロードしてください", type="csv")

if uploaded_file is not None:
    # データの読み込み
    df = pd.read_csv(uploaded_file)
    
    st.sidebar.success("読み込み完了")
    
    # 軸の選択
    columns = df.columns.tolist()
    x_col = st.sidebar.selectbox("X軸（座標）を選択", columns, index=0)
    y_col = st.sidebar.selectbox("Y軸（値）を選択", columns, index=1 if len(columns) > 1 else 0)

    # 2. 点（〇）の位置を操作するスライダー
    # データフレームのインデックスに基づいて動かします
    max_idx = len(df) - 1
    selected_idx = st.slider("〇点の位置を移動", 0, max_idx, 0)

    # 選択された地点のデータを取得
    target_row = df.iloc[selected_idx]
    target_x = target_row[x_col]
    target_y = target_row[y_col]

    # 3. Plotlyでグラフ作成
    fig = go.Figure()

    # ベースの折れ線グラフ
    fig.add_trace(go.Scatter(
        x=df[x_col], 
        y=df[y_col], 
        mode='lines', 
        name='データ',
        line=dict(color='royalblue', width=1)
    ))

    # 移動する〇点
    fig.add_trace(go.Scatter(
        x=[target_x], 
        y=[target_y], 
        mode='markers', 
        name='現在地',
        marker=dict(size=15, color='red', symbol='circle', line=dict(width=2, color='white'))
    ))

    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        hovermode="x unified",
        height=600
    )

    # グラフ表示
    st.plotly_chart(fig, use_container_width=True)

    # 4. 詳細情報の表示（読み込み）
    st.subheader(f"📍 選択地点の情報 (Index: {selected_idx})")
    
    # 全カラムの情報をカード形式で表示
    cols = st.columns(min(len(columns), 4))
    for i, col_name in enumerate(columns):
        with cols[i % 4]:
            st.metric(label=col_name, value=target_row[col_name])

    # データテーブルの表示（周辺の確認用）
    with st.expander("データ詳細を確認"):
        st.write(df.iloc[max(0, selected_idx-5):min(max_idx, selected_idx+5)])

else:
    st.info("左側のサイドバーからCSVファイルをアップロードしてください。")
    # サンプルデータの表示
    if st.checkbox("サンプルデータを生成して試す"):
        sample_x = np.linspace(0, 10, 100)
        sample_y = np.sin(sample_x)
        sample_df = pd.DataFrame({"Time": sample_x, "Value": sample_y})
        st.write("サンプルデータを使います。このまま上のツールが動作します。")
        # ここで再代入して動かすことも可能です。
