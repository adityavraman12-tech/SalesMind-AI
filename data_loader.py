import pandas as pd


def load_sales_data(file_path):
    """Load sales data from an Excel file."""

    try:
        df = pd.read_excel(file_path)

        # Convert date column
        if "Order Date" in df.columns:
            df["Order Date"] = pd.to_datetime(
                df["Order Date"],
                errors="coerce"
            )

        return df

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Could not find the file: {file_path}"
        )

    except Exception as e:
        raise Exception(
            f"Error loading sales data: {e}"
        )


def get_data_summary(df):
    """Return basic information about the dataset."""

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_values": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }