import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from matplotlib.patches import Ellipse
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# =========================
# Config
# =========================
CSV_FILE = "biotools_with_metrics_and_maturity.csv"
PCA_FIGURE = "PCA.svg"

PLOT_NONE = False  # whether to plot "None" maturity (should be False for your case)
POINT_SIZE = 50
ELLIPSE_95K = 2.4477  # sqrt(chi2.ppf(0.95, df=2))
ELLIPSE_LW = 2
ELLIPSE_ALPHA = 0.9

NUMERIC_COLS = [
    "repo.stargazers_count",
    "repo.watchers_count",
    "repo.subscribers_count",
    "repo.forks_count",
    "repo.open_issues_count",
    "repo.network_count",
    "num_contributors",
    "num_releases",
    "num_commits",
    "num_pulls",
    "avg_time_to_close_days",
]

MATURITY_CANONICAL = {
    "mature": "Mature",
    "emerging": "Emerging",
    "legacy": "Legacy",
}

MATURITY_ORDER = ["Emerging", "Mature", "Legacy"]  # fixed display order


# =========================
# Helper: covariance ellipse
# =========================
def add_cov_ellipse(
    ax,
    x,
    y,
    edgecolor="k",
    k=ELLIPSE_95K,
    lw=ELLIPSE_LW,
    alpha=ELLIPSE_ALPHA,
):
    """Add a covariance ellipse for points (x, y) onto ax."""
    if len(x) < 2:
        return
    xy = np.column_stack([x, y])
    mu = xy.mean(axis=0)
    cov = np.cov(xy, rowvar=False)
    if not np.all(np.isfinite(cov)) or np.linalg.matrix_rank(cov) < 2:
        return

    vals, vecs = np.linalg.eigh(cov)
    order = vals.argsort()[::-1]
    vals, vecs = vals[order], vecs[:, order]
    width, height = 2 * k * np.sqrt(np.maximum(vals, 0))
    angle = np.degrees(np.arctan2(vecs[1, 0], vecs[0, 0]))

    ell = Ellipse(
        xy=mu,
        width=width,
        height=height,
        angle=angle,
        fill=False,
        lw=lw,
        edgecolor=edgecolor,
        alpha=alpha,
    )
    ax.add_patch(ell)


# =========================
# 1) Load & normalize
# =========================
df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

# Normalize maturity field early, once
df["maturity"] = df.get("maturity", np.nan).astype(str).str.strip().str.lower()

df["maturity"] = df["maturity"].replace({"": "none", "na": "none", "nan": "none"})
df["maturity"] = df["maturity"].map(MATURITY_CANONICAL).fillna("None")

# Normalize biotoolsID
df["biotoolsID"] = df.get("biotoolsID", np.nan).fillna("unknown")

# Convert numeric columns
for c in NUMERIC_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# =========================
# 2) Basic counts (GitHub / metrics)
# =========================
with_github = df[df["repo_url"].str.contains("github.com", case=False, na=False)]
n_with_github = len(with_github)

valid_mask = df[NUMERIC_COLS].notna().any(axis=1)
valid_repos = df[
    valid_mask & df["repo_url"].str.contains("github.com", case=False, na=False)
]
n_valid = len(valid_repos)

print(f"bio.tools entries total:                     {len(df):,}")
print(f"Entries with any GitHub URL:                 {n_with_github:,}")
print(f"Entries with valid GitHub repo metrics:      {n_valid:,}")
if n_with_github:
    print(
        f"→ Fraction of valid among GitHub entries:    {n_valid / n_with_github * 100:.1f}%"
    )

# =========================
# 3) Classification: predict maturity from metrics
# =========================
# Restrict to Emerging / Mature / Legacy with valid metrics + GitHub

df_clf = df[
    df["maturity"].isin(MATURITY_ORDER)
    & df["repo_url"].str.contains("github.com", case=False, na=False)
    & valid_mask
].copy()

print("\nDataset sizes:")
print("Rows total:", len(df))
print(
    "Rows after filtering (Emerging/Mature/Legacy + GitHub + valid metrics):",
    len(df_clf),
)
print(df_clf["maturity"].value_counts())

print("\nClass distribution (for modeling):")
class_counts = df_clf["maturity"].value_counts().reindex(MATURITY_ORDER)
print(class_counts)

X = df_clf[NUMERIC_COLS].fillna(0.0)
y = df_clf["maturity"]

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    stratify=y,
    random_state=42,
)

clf = RandomForestClassifier(
    n_estimators=300,
    max_depth=None,
    class_weight="balanced",
    random_state=42,
)
clf.fit(X_train, y_train)

y_pred = clf.predict(X_test)

print("\nClassification report:")
print(classification_report(y_test, y_pred, labels=MATURITY_ORDER))

# -------------------------
# Labeled confusion matrix
# -------------------------
labels_present = [l for l in MATURITY_ORDER if l in y_test.unique()]
cm_present = confusion_matrix(y_test, y_pred, labels=labels_present)

# build full 3×3 (Emerging/Mature/Legacy), zero where missing
cm_full = np.zeros((len(MATURITY_ORDER), len(MATURITY_ORDER)), dtype=int)
for i_t, t_lab in enumerate(labels_present):
    for i_p, p_lab in enumerate(labels_present):
        cm_full[MATURITY_ORDER.index(t_lab), MATURITY_ORDER.index(p_lab)] = cm_present[
            i_t, i_p
        ]

cm_df = pd.DataFrame(
    cm_full,
    index=[f"True {l}" for l in MATURITY_ORDER],
    columns=[f"Pred {l}" for l in MATURITY_ORDER],
)

print("\nConfusion matrix (counts):")
print(cm_df)

# -------------------------
# Feature importances
# -------------------------
imp = pd.Series(clf.feature_importances_, index=NUMERIC_COLS)
print("\nFeature importances (RandomForest):")
print(imp.sort_values(ascending=False))


# =========================
# 4) PCA on metrics, colored by maturity
# =========================
df_pca = df[df["maturity"].isin(MATURITY_ORDER)].copy()
X_pca_input = df_pca[NUMERIC_COLS].fillna(0.0).values
X_pca_input = np.log1p(X_pca_input)  # shrink heavy tails
X_scaled = StandardScaler().fit_transform(X_pca_input)

pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

df_pca["PC1"] = X_pca[:, 0]
df_pca["PC2"] = X_pca[:, 1]

print("\nPCA explained variance ratio (PC1, PC2):")
print(pca.explained_variance_ratio_)

fig, ax = plt.subplots(figsize=(8, 8))

maturity_colors = {
    "Emerging": "green",
    "Legacy": "red",
    "Mature": "blue",
}
default_color = "gray"

all_levels = df_pca["maturity"].unique().tolist()
if not PLOT_NONE:
    all_levels = [m for m in all_levels if m != "None"]

legend_order = [m for m in MATURITY_ORDER if m in all_levels]
if "None" in all_levels and PLOT_NONE:
    legend_order.append("None")

for level in legend_order:
    subset = df_pca[df_pca["maturity"] == level]
    ax.scatter(
        subset["PC1"],
        subset["PC2"],
        label=level,
        s=POINT_SIZE,
        alpha=0.3,
        color=maturity_colors.get(level, default_color),
    )
    if len(subset) >= 3:
        add_cov_ellipse(
            ax,
            subset["PC1"].to_numpy(dtype=float),
            subset["PC2"].to_numpy(dtype=float),
            edgecolor=maturity_colors.get(level, default_color),
        )

ax.autoscale(enable=True, tight=True)
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}% var)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}% var)")
ax.set_title("PCA of GitHub repository maturity-related metrics by bio.tools maturity")
ax.legend(title="Maturity level", loc="best", frameon=False)
ax.grid(True, linestyle="--", alpha=0.3)
ax.set_xlim(-3, 15)
ax.set_ylim(-4, 4)

plt.savefig(PCA_FIGURE, format="svg", bbox_inches="tight")
plt.close(fig)

# =========================
# PCA loadings (PC1 and PC2)
# =========================
loadings = pd.DataFrame(
    pca.components_.T, index=NUMERIC_COLS, columns=["PC1_loading", "PC2_loading"]
)

print("\nPCA loadings (PC1, PC2):")
print(loadings)

# =========================
# 6) Area-proportional Venn diagram (GitHub vs bio.tools)
#     - true area proportions
#     - GitHub circle mostly off-frame (only a small arc visible)
# =========================
import math
from matplotlib.patches import Circle

VENN_FIGURE = "venn_github_biotools_truncated.svg"

# True counts
GITHUB_TOTAL = 395_000_000
BIOTOOLS_TOTAL = 30_608
OVERLAP_TOTAL = 13_391


def circle_intersection_area(r1: float, r2: float, d: float) -> float:
    """Area of intersection of two circles with radii r1, r2 and center distance d."""
    if d >= r1 + r2:
        return 0.0
    if d <= abs(r1 - r2):
        return math.pi * min(r1, r2) ** 2

    alpha = math.acos((d * d + r1 * r1 - r2 * r2) / (2 * d * r1))
    beta = math.acos((d * d + r2 * r2 - r1 * r1) / (2 * d * r2))
    term = max(
        0.0,
        (-d + r1 + r2) * (d + r1 - r2) * (d - r1 + r2) * (d + r1 + r2),
    )
    area = r1 * r1 * alpha + r2 * r2 * beta - 0.5 * math.sqrt(term)
    return area


def find_distance_for_intersection(r1: float, r2: float, target_area: float) -> float:
    """Binary search for d such that intersection area ~= target_area."""
    max_intersection = math.pi * min(r1, r2) ** 2
    if target_area >= max_intersection:
        # smaller circle completely inside larger
        return abs(r1 - r2)
    if target_area <= 0:
        # disjoint
        return r1 + r2

    lo = abs(r1 - r2) + 1e-6
    hi = r1 + r2 - 1e-6
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        area_mid = circle_intersection_area(r1, r2, mid)
        if area_mid > target_area:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


# -------------------------------------------------
# 1) Radii in "size units": area = count
#    => pi * r^2 = count => r = sqrt(count / pi)
# -------------------------------------------------
rG0 = math.sqrt(GITHUB_TOTAL / math.pi)
rB0 = math.sqrt(BIOTOOLS_TOTAL / math.pi)

# Distance between centers so that intersection area = OVERLAP_TOTAL
d0 = find_distance_for_intersection(rG0, rB0, OVERLAP_TOTAL)

# -------------------------------------------------
# 2) Rescale so that bio.tools circle has a convenient radius (e.g. 1)
#    Geometry (relative sizes, overlap) is preserved under uniform scaling.
# -------------------------------------------------
desired_rB = 1.0
scale = desired_rB / rB0

r_biotools = rB0 * scale
r_github = rG0 * scale
d = d0 * scale

# Place bio.tools at origin, GitHub far to the left at (-d, 0)
biotools_center = (0.0, 0.0)
github_center = (0.0, -d)

fig, ax = plt.subplots(figsize=(8, 8))  # same proportions as PCA

github_circle = Circle(
    github_center,
    r_github,
    facecolor="#181717",
    edgecolor="#0E0E0E",
    alpha=0.5,
    linewidth=1.5 * 0,
)
biotools_circle = Circle(
    biotools_center,
    r_biotools,
    facecolor="#005472",  # bio.tools blue
    edgecolor="#003346",
    alpha=0.7,
    linewidth=1.5 * 0,
)

ax.add_patch(github_circle)
ax.add_patch(biotools_circle)

# -------------------------------------------------
# 3) Crop view so that:
#    - full bio.tools circle is visible
#    - overlap region is visible
#    - only a small arc of the huge GitHub circle is shown
# -------------------------------------------------
margin = 3.0 * r_biotools
ax.set_xlim(-4 * r_biotools, 4 * r_biotools)
ax.set_ylim(-6 * r_biotools, 2 * r_biotools)
ax.set_aspect("equal", adjustable="box")
ax.axis("off")

# Text labels
# ax.text(
#    biotools_center[0],
#    biotools_center[1],
#    f"bio.tools\n{BIOTOOLS_TOTAL:,} tools",
#    ha="center",
#    va="center",
#    fontsize=10,
#    color="black",
# )

# ax.text(
#    -2.5 * r_biotools,
#    3.2 * r_biotools,
#    f"GitHub\n{GITHUB_TOTAL:,} repositories\n(circle mostly off-frame)",
#    ha="right",
#    va="top",
#    fontsize=9,
# )

# ax.text(
#    0.0,
#    -2.5 * r_biotools,
#    f"Overlap\n{OVERLAP_TOTAL:,} repositories",
#    ha="center",
#    va="top",
#    fontsize=9,
#    fontweight="bold",
# )

# ax.set_title(
#    "Area-proportional Venn diagram (truncated view)\n"
#    "GitHub vs bio.tools repositories",
#    fontsize=12,
# )

plt.savefig(VENN_FIGURE, format="svg", bbox_inches="tight")
plt.close(fig)
