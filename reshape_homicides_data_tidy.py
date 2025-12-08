import pandas as pd


def categorize_columns(df):
    """
    Categorize each column as either a state or municipality.
    Uses the pattern: State -> Municipalities -> No especificado (repeat)
    """
    # Filter out empty columns, Total, and columns that are just spaces
    columns = [col for col in df.columns if col.strip() not in ["", "Total"]]

    column_info = []
    current_state = None

    for col in columns:
        col_clean = col.strip()

        # Check if this is a "No especificado" (end of state section)
        if "No especificado" in col:
            column_info.append(
                {
                    "column": col,
                    "state": current_state,
                    "municipality": "No especificado",
                    "type": "municipality",
                }
            )
            current_state = None  # Reset for next state

        # Check if this is a state (no .# suffix and current_state is None)
        elif current_state is None:
            current_state = col_clean.split(".")[0]
            column_info.append(
                {
                    "column": col,
                    "state": current_state,
                    "municipality": None,
                    "type": "state",
                }
            )

        # Otherwise it's a municipality
        else:
            # Clean up the .# suffix if it exists (pandas feauture to
            # avoid duplicate column names)
            clean_name = col_clean.split(".")[0]
            column_info.append(
                {
                    "column": col,
                    "state": current_state,
                    "municipality": clean_name,
                    "type": "municipality",
                }
            )

    return column_info


def reshape_to_tidy(df, col_info):
    """
    Transform wide format data to tidy (long) format.
    Each row will represent one location (state or municipality) in one year.
    """
    rows = []

    # Find the year column
    year_col = df.columns[0]

    # Iterate through each year in the dataframe
    for _, row in df.iterrows():
        year = row[year_col]

        # Process each column based on its type
        for info in col_info:
            homicides = row[info["column"]]

            rows.append(
                {
                    "Year": year,
                    "State": info["state"],
                    "Municipality": info["municipality"]
                    if info["municipality"]
                    else info["state"],
                    "Type": info["type"],
                    "Homicides": homicides,
                }
            )

    return pd.DataFrame(rows)


def main():
    """
    Main function to run the reshaping process.
    """
    # Load the CSV with latin-1 encoding (Spanish characters)
    df = pd.read_csv("homicides_by_state_municipality.csv", encoding="latin-1")

    col_info = categorize_columns(df)

    states = [info["state"] for info in col_info if info["type"] == "state"]
    municipalities = [info for info in col_info if info["type"] == "municipality"]

    print(f"Found {len(states)} states")
    print(f"Found {len(municipalities)} municipalities")

    tidy_df = reshape_to_tidy(df, col_info)

    tidy_df.to_csv("homicides_locations_tidy.csv", index=False)

    print("Saved to 'homicides_locations_tidy.csv'")

    print(f"   State-level records: {len(tidy_df[tidy_df['Type'] == 'state'])}")
    print(
        f"   Municipality-level records: {len(tidy_df[tidy_df['Type'] == 'municipality'])}"
    )


if __name__ == "__main__":
    main()
