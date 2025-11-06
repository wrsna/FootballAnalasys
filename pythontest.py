import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------
# 📄 1. Naloži podatke
# -------------------------------
st.set_page_config(page_title="Analiza Serie A modela", layout="wide")

st.title("⚽ Analiza uspešnosti napovednega modela Serie A")

uploaded_file = st.file_uploader("📤 Naloži CSV datoteko", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    st.info("Naloži CSV datoteko (npr. 'serie_a_value_betting_predictions_with_eval_featsel.csv').")
    st.stop()

# -------------------------------
# 🧮 2. Obdelava podatkov
# -------------------------------
# Predpostavimo, da CSV sledi tvojemu formatu
df.columns = [col.strip() for col in df.columns]

# Če je treba, lahko prilagodiš imena stolpcev tu
try:
    df['confidence'] = df.iloc[:, 13].astype(float)
    df['shouldi_bet'] = df.iloc[:, 15] == 'True'
    df['bet_outcome'] = df.iloc[:, 16]
except Exception as e:
    st.error(f"Napaka pri branju stolpcev: {e}")
    st.stop()

df = df[df['should_bet'] & df['bet_outcome'].notna()].copy()
df['isWin'] = df['bet_outcome'].str.contains('WIN', case=False, na=False)
df['units'] = df['bet_outcome'].str.extract(r'([+-]?\d+\.\d+)').astype(float).fillna(0)

# -------------------------------
# ⚙️ 3. Nastavitev praga zaupanjadh
# -------------------------------
confidence_threshold = st.slider("📊 Izberi prag zaupanja (confidence)", 0.4, 1.0, 0.6, 0.05)

filtered = df[df['confidence'] >= confidence_threshold]

# -------------------------------
# 📈 4. Izračun osnovnih statistik
# -------------------------------
total_bets = len(filtered)
wins = filtered['isWin'].sum()
losses = total_bets - wins
total_units = filtered['units'].sum()
win_rate = (wins / total_bets * 100) if total_bets > 0 else 0
roi = (total_units / total_bets * 100) if total_bets > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("💰 Št. stav", total_bets)
col2.metric("✅ Zmage", wins)
col3.metric("❌ Porazi", losses)
col4.metric("📈 Win rate", f"{win_rate:.1f}%")
col5.metric("💵 ROI", f"{roi:.1f}%")

# -------------------------------
# 📊 5. Analiza po območjih zaupanja
# -------------------------------
bins = [0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
labels = ["0.40–0.50", "0.50–0.60", "0.60–0.70", "0.70–0.80", "0.80–0.90", "0.90–1.00"]
df['bucket'] = pd.cut(df['confidence'], bins=bins, labels=labels, include_lowest=True)

bucket_stats = (
    df.groupby('bucket')
    .agg(wins=('isWin', 'sum'),
         total=('isWin', 'count'),
         units=('units', 'sum'))
    .reset_index()
)
bucket_stats['win_rate'] = (bucket_stats['wins'] / bucket_stats['total'] * 100).round(1)
bucket_stats['roi'] = (bucket_stats['units'] / bucket_stats['total'] * 100).round(1)

# -------------------------------
# 📉 6. Grafi
# -------------------------------
st.subheader("📊 Uspešnost po območjih zaupanja")

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(bucket_stats['bucket'], bucket_stats['win_rate'])
ax.set_xlabel("Confidence")
ax.set_ylabel("Win Rate (%)")
ax.set_title("Uspešnost modela po območjih zaupanja")
st.pyplot(fig)

fig2, ax2 = plt.subplots(figsize=(8, 4))
ax2.bar(bucket_stats['bucket'], bucket_stats['roi'], color='orange')
ax2.set_xlabel("Confidence")
ax2.set_ylabel("ROI (%)")
ax2.set_title("ROI po območjih zaupanja")
st.pyplot(fig2)

# -------------------------------
# 📄 7. Pregled surovih podatkov
# -------------------------------
st.subheader("📄 Podrobnosti posameznih stav")
st.dataframe(filtered[['confidence', 'bet_outcome', 'units', 'isWin']].sort_values(by='confidence', ascending=False))
