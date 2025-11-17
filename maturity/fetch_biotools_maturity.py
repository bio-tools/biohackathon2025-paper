import pandas as pd
import requests

# Input / output paths
IN_CSV = "biotools_with_metrics.csv"
OUT_CSV = "biotools_with_metrics_and_maturity.csv"

# Base URL for bio.tools API
BASE_URL = "https://bio.tools/api/tool"


def fetch_maturity(biotools_id: str) -> str:
    if not isinstance(biotools_id, str) or biotools_id.strip() == "":
        return "None"

    biotools_id = biotools_id.strip()
    url = f"{BASE_URL}/{biotools_id}/?format=json"

    try:
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            # tool not found or other error
            return "None"

        data = r.json()
        # "maturity" is a top-level attribute; may be absent
        maturity = data.get("maturity", None)
        if not maturity:
            return "None"
        return maturity
    except Exception:
        return "None"


def main():
    df = pd.read_csv(IN_CSV)

    # Make sure the column name matches your header exactly
    if "biotoolsID" not in df.columns:
        raise ValueError("CSV must contain a 'biotoolsID' column")

    df["maturity"] = df["biotoolsID"].apply(fetch_maturity)

    df.to_csv(OUT_CSV, index=False)
    print(f"Wrote {OUT_CSV}")


if __name__ == "__main__":
    main()
