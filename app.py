import streamlit as st
import numpy as np
import plotly.graph_objects as go
import pandas as pd

# ページのレイアウト設定
st.set_page_config(page_title="SOFC Analyzer", layout="centered")
st.title("SOFC OCV 解析シミュレーター")

# --- サイドバーの設定 ---
st.sidebar.header("共通条件")
T_c = st.sidebar.slider("温度 (°C)", 400, 1100, 800)

st.sidebar.header("個別圧力設定（赤線）")
P_fuel_user = st.sidebar.slider("燃料極 全圧 (atm)", 0.5, 10.0, 1.0, 0.5)
P_air_user = st.sidebar.slider("空気極 全圧 (atm)", 0.5, 10.0, 1.0, 0.5)

# --- 定数計算 ---
T_k = T_c + 273.15
R, F = 8.314, 96485
# 標準電極電位 E0 の計算
E0 = 1.2844 - 0.0002521 * T_k 
O2_ratio = 0.21

# --- 計算用関数 ---
def get_ocv(h2_ratio, p_f, p_a):
    x = max(min(h2_ratio / 100.0, 0.9999), 0.0001) # 0除算回避
    p_h2 = x * p_f
    p_h2o = (1 - x) * p_f
    p_o2 = O2_ratio * p_a
    # ネルンストの式
    term = (R * T_k / (2 * F)) * np.log((p_h2 * (p_o2**0.5)) / p_h2o)
    return E0 + term

# --- データ作成 ---
h_list = np.arange(1, 100, 1)
y_user = [get_ocv(h, P_fuel_user, P_air_user) for h in h_list]
y_1 = [get_ocv(h, 1.0, 1.0) for h in h_list]
y_3 = [get_ocv(h, 3.0, 3.0) for h in h_list]
y_5 = [get_ocv(h, 5.0, 5.0) for h in h_list]

# --- グラフ描画 ---
fig = go.Figure()

# 比較用ライン
fig.add_trace(go.Scatter(x=h_list, y=y_1, name='1atm平衡', line=dict(color='lightgray', dash='dot')))
fig.add_trace(go.Scatter(x=h_list, y=y_3, name='3atm平衡', line=dict(color='gray', dash='dash')))
fig.add_trace(go.Scatter(x=h_list, y=y_5, name='5atm平衡', line=dict(color='black', dash='dash')))

# メインライン（赤太線）
fig.add_trace(go.Scatter(x=h_list, y=y_user, name='現在の設定', line=dict(color='red', width=4)))

fig.update_layout(
    width=650, height=650,
    plot_bgcolor='white',
    legend=dict(x=0.02, y=0.98, bgcolor='rgba(255,255,255,0.8)', bordercolor="black", borderwidth=1),
    
    # 横軸の設定
    xaxis=dict(
        title=dict(text="水素容量比率 [%]", font=dict(color='black', size=14)),
        tickmode='linear',
        tick0=0,
        dtick=5,
        range=[0, 100],
        tickfont=dict(color='black'),
        showgrid=True, gridcolor='DarkGray', gridwidth=1,
        showline=True, linewidth=2, linecolor='black', mirror=True
    ),
    
    # 縦軸の設定（0.6V〜1.3Vで完全固定）
    yaxis=dict(
        title=dict(text="開回路電圧 OCV [V]", font=dict(color='black', size=14)),
        tickmode='linear',
        tick0=0.6,
        dtick=0.05,        # 0.05V刻み
        range=[0.6, 1.3],  # 最小0.6V, 最大1.3Vに固定
        tickfont=dict(color='black'),
        showgrid=True, gridcolor='DarkGray', gridwidth=1,
        showline=True, linewidth=2, linecolor='black', mirror=True,
        autorange=False    # 自動伸縮を無効化
    ),
    margin=dict(l=80, r=40, t=60, b=80)
)

st.plotly_chart(fig, use_container_width=False)

# --- 情報表示 ---
st.info(f"**標準電極電位 E0:** {E0:.4f} V  \n（温度 {T_c}℃ における基礎電圧。ここからガス分圧の影響でOCVが上下します）")

# ダウンロード機能
df = pd.DataFrame({"H2_ratio_%": h_list, "OCV_V": y_user})
st.download_button("CSV保存", df.to_csv(index=False).encode('utf-8'), "sofc_ocv_data_csv")
