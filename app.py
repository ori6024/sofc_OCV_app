import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. ページの設定
st.set_page_config(page_title="SOFC OCV Calculator", layout="wide")

# 2. サイドバーに条件変更の設定
st.sidebar.markdown("### ⚙️ 条件変更")
st.sidebar.write("セルの動作条件を設定してください")

# パラメータ入力
temp_c = st.sidebar.slider('温度 (°C)', 400.0, 1000.0, 700.0)
p_h2 = st.sidebar.slider('水素分圧 H2 (atm)', 0.01, 1.0, 0.97)
p_h2o = st.sidebar.slider('水蒸気分圧 H2O (atm)', 0.01, 0.5, 0.03)
p_o2 = st.sidebar.slider('酸素分圧 O2 (atm)', 0.01, 1.0, 0.21) # 0.21は空気

# 3. ネルンストの式による計算ロジック
# 定数
R = 8.314  # 気体定数 [J/mol·K]
F = 96485  # ファラデー定数 [C/mol]
T = temp_c + 273.15  # 摂氏からケルビンへ変換

# 標準ギブズ自由エネルギー変化（簡易的な温度依存式）
# ΔG = -247500 + 55.8 * T (J/mol) ※水素燃焼反応の概算
delta_g = -247500 + 55.8 * T
E0 = -delta_g / (2 * F)

# ネルンストの式: E = E0 + (RT/2F) * ln( (P_H2 * P_O2^0.5) / P_H2O )
ocv = E0 + (R * T / (2 * F)) * np.log((p_h2 * np.sqrt(p_o2)) / p_h2o)

# 4. グラフ表示用のデータ作成（温度変化によるOCVの推移）
t_range = np.linspace(400, 1000, 100)
t_kelvin = t_range + 273.15
# 温度変化に伴うΔGの変化を考慮したOCV推移
ocv_range = (-(-247500 + 55.8 * t_kelvin) / (2 * F)) + \
            (R * t_kelvin / (2 * F)) * np.log((p_h2 * np.sqrt(p_o2)) / p_h2o)

# 5. グラフ作成（Plotly: 軸固定・ズーム禁止）
fig = go.Figure()
fig.add_trace(go.Scatter(x=t_range, y=ocv_range, mode='lines', name='OCV推移',
