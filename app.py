
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. ページの設定（スマホで余白をなくす）
st.set_page_config(page_title="シミュレーションアプリ", layout="wide")

# 2. サイドバーの設定
st.sidebar.markdown("### ⚙️ 条件変更")
st.sidebar.write("こちらでパラメータを調整できます")

# パラメータ入力スライダー
frequency = st.sidebar.slider('周波数', 1.0, 10.0, 5.0)
# 振幅を 0.0 〜 2.0 に設定
amplitude = st.sidebar.slider('振幅', 0.0, 2.0, 1.0)

# 3. 計算ロジック（サイン波）
x = np.linspace(0, 10, 500)
y = amplitude * np.sin(frequency * x)

# 4. グラフ作成（Plotlyを使用）
fig = go.Figure()

# 波形の描画
fig.add_trace(go.Scatter(
    x=x, y=y, 
    mode='lines', name='波形', 
    line=dict(color='#1f77b4', width=3)
))

# 5. レイアウト設定（ここで軸を固定してズームを禁止する）
fig.update_layout(
    xaxis_title="Time",
    yaxis_title="Value",
    # 軸の範囲を固定し、スマホ操作でのズレを防止
    xaxis=dict(range=[0, 10], fixedrange=True),
    yaxis=dict(range=[-2.2, 2.2], fixedrange=True),
    height=500,
    margin=dict(l=20, r=20, t=20, b=20),
    showlegend=False
)

# 6. 画面への表示
st.title('シミュレーション・グラフアプリ')

# グラフを表示（configでツールバーを消し、ズームを完全に無効化）
st.plotly_chart(
    fig, 
    use_container_width=True, 
    config={
        'displayModeBar': False, 
        'scrollZoom': False, 
        'staticPlot': False
    }
)

st.write(f"現在の設定：周波数 **{frequency}** / 振幅 **{amplitude}**")
st.info("スライダーを動かして波形を変化させてください。グラフは固定されています。")
