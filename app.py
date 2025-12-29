import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from streamlit_plotly_events import plotly_events

st.set_page_config(page_title="Multi-Probe Tool", layout="wide")

st.title("📍 マルチ・データプローブ追加ツール")
st.write("グラフ上をクリックして〇（プローブ）を追加してください。右側のボタンでリセットできます。")

# --- 1. データ準備 ---
uploaded_file = st.sidebar.file_uploader("CSVアップロード", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.DataFrame({
        "x": np.linspace(0, 10, 100),
        "y": np.sin(np.linspace(0, 10, 100)) ** 2 + np.random.normal(0, 0.05, 100),
        "備考": [f"サンプルデータ {i}" for i in range(100)]
    })
    st.sidebar.info("サンプルデータを表示中")

x_col = st.sidebar.selectbox("X軸", df.columns, index=0)
y_col = st.sidebar.selectbox("Y軸", df.columns, index=1)

# --- 2. 状態管理（複数の〇のインデックスをリストで保持） ---
if "probe_indices" not in st.session_state:
    st.session_state.probe_indices = []

# リセットボタン
if st.sidebar.button("すべての〇を削除"):
    st.session_state.probe_indices = []
    st.rerun()

# --- 3. グラフの作成 ---
fig = go.Figure()

# ベースの線（薄く表示）
fig.add_trace(go.Scatter(
    x=df[x_col], y=df[y_col], mode='lines', 
    line=dict(color='rgba(150, 150, 150, 0.3)'),
    hoverinfo='skip',
    name='データ'
))

# 追加されたすべての〇を描画
for i, idx in enumerate(st.session_state.probe_indices):
    target = df.iloc[idx]
    fig.add_trace(go.Scatter(
        x=[target[x_col]], y=[target[y_col]], 
        mode='markers+text',
        marker=dict(size=12, symbol='circle', line=dict(width=2, color='white')),
        text=[f"P{i+1}"], # プローブ番号を表示
        textposition="top center",
        name=f"Probe {i+1}"
    ))

fig.update_layout(
    xaxis_title=x_col, yaxis_title=y_col,
    clickmode='event+select',
    margin=dict(l=20, r=20, t=40, b=20),
    showlegend=False
)

# --- 4. グラフの表示とクリックイベントの取得 ---
selected_point = plotly_events(fig, click_event=True, hover_event=False)

# クリックされたら新しいインデックスをリストに追加
if selected_point:
    clicked_x = selected_point[0]['x']
    closest_idx = (df[x_col] - clicked_x).abs().idxmin()
    
    # すでに同じ場所にある場合は追加しない（重複防止）
    if closest_idx not in st.session_state.probe_indices:
        st.session_state.probe_indices.append(closest_idx)
        st.rerun()

# --- 5. 追加されたプローブの情報を一覧表示 ---
if st.session_state.probe_indices:
    st.markdown("---")
    st.subheader("📋 取得済みデータ一覧")
    
    # 選択された行だけを抽出して表示
    probed_df = df.iloc[st.session_state.probe_indices].copy()
    # 見やすくするためにプローブ番号の列を追加
    probed_df.insert(0, "プローブID", [f"P{i+1}" for i in range(len(probed_df))])
    
    st.dataframe(probed_df, use_container_width=True)
    
    # CSVとしてダウンロードする機能
    csv_data = probed_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="選択したデータをCSVで保存",
        data=csv_data,
        file_name='probed_data.csv',
        mime='text/csv',
    )
else:
    st.write("グラフをクリックしてデータをサンプリングしてください。")
