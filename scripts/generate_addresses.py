import pandas as pd
import random
import re

from pathlib import Path


def normalize_via(raw: str) -> str:
    """
    Normalize street names:
    - 'CABOTO 5. (Via)' -> 'Via Caboto 5'
    - 'CACCIA DOMINIONI C. (Largo)' -> 'Largo Caccia Domini'
    - 'ABBA G. C. (Via)' -> 'Via Abba'
    - 'ABBIATEGRASSO (Piazza)' -> 'Piazza Abbiategrasso'
    """
    if not isinstance(raw, str):
        return None

    # Regex to split "Name (Type)"
    match = re.match(r"(.+)\(([^)]+)\)", raw)
    if not match:
        return raw.strip().title()

    name_part = match.group(1).strip().title()
    street_type = match.group(2).strip().title()

    # Remove dots and extra spaces
    name_part = name_part.replace(".", "").strip()
    name_part = re.sub(r"\s+", " ", name_part)

    # Remove trailing initials (e.g. "Schiller F" -> "Schiller")
    words = name_part.split()
    if len(words) > 1 and re.fullmatch(r"[A-Z]", words[-1]):
        words = words[:-1]  # drop last initial

    clean_name = " ".join(words)

    return f"{street_type} {clean_name}"


def sample_addresses(file_path, N=2, M=3, seed: int = None):
    """
    Load the file, clean rows, group by CAP,
    and sample N postal codes each with M random streets.
    If seed is provided, sampling is reproducible.
    """
    # Set random seed if given
    if seed is not None:
        random.seed(seed)

    # Load file (supports CSV or Excel)
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path, sep="\t", header=None)
    else:
        df = pd.read_excel(file_path, header=None)

    # Keep only CAP and Street columns (assuming 2nd and 3rd columns)
    df = df[[1, 2]].copy()
    df.columns = ["CAP", "VIA"]

    # Drop invalid rows
    df = df.dropna()
    df = df[~df["CAP"].astype(str).str.contains("#VALUE!", na=False)]
    df = df[~df["VIA"].astype(str).str.contains("#VALUE!", na=False)]
    df = df[df["CAP"].str.strip().str.isnumeric()]

    # Normalize street names
    df["VIA"] = df["VIA"].apply(normalize_via)

    # Group by CAP
    grouped = df.groupby("CAP")["VIA"].apply(list).to_dict()

    # Sample N CAPs
    sampled_caps = random.sample(list(grouped.keys()), min(N, len(grouped)))

    result = {}
    for cap in sampled_caps:
        vie = grouped[cap]
        sampled_vie = random.sample(vie, min(M, len(vie)))
        result[cap] = sampled_vie

    return result


NUM_POSTAL_CODE = 1
NUM_STREETS = 10

file_path = Path(__file__).parent.parent / "data" / "italy_milano.xlsx"
assert file_path.exists(), f"Path {file_path} does not exist"
GENERATED_ADDRESSES = sample_addresses(
    file_path.as_posix(), N=NUM_POSTAL_CODE, M=NUM_STREETS, seed=63
)
if __name__ == "__main__":
    print(GENERATED_ADDRESSES)
