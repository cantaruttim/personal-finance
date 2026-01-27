import matplotlib.pyplot as plt
from report_builder import finantial_report, value, exp
from utils import select_columns

df = select_columns(
    finantial_report(exp, value),
    ["yearmonth", "variation_percent"]
)

# =====================================
# ======= VALUE SAVED PER MONTH =======
# =====================================

df = df.sort_values("yearmonth")

colors = ["green" if v >= 0 else "red" for v in df["variation_percent"]]

plt.figure(figsize=(10, 5))
bars = plt.bar(
    df["yearmonth"],
    df["variation_percent"],
    color=colors
)

plt.axhline(0)
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        height * 0.95 if height != 0 else 0,
        f"{height:.1f}%",
        ha="center",
        va="top" if height > 0 else "bottom",
        color="white",
        fontweight="bold"
    )

plt.title("Monthly Expense Variation (%)", fontweight="bold")
plt.ylabel("Variation (%)")

ax = plt.gca()
ax.spines["right"].set_visible(False)
ax.spines["top"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.set_yticks([])

plt.xticks(rotation=45)

plt.tight_layout()
plt.show()
