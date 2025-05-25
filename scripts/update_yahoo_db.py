import argparse
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

from ami2py import AmiDataBase, SymbolEntry


def get_last_date(db: AmiDataBase, symbol: str) -> date:
    data = db.get_dict_for_symbol(symbol)
    if len(data["Day"]) == 0:
        # no data, download all available history
        return date.today() - timedelta(days=365 * 50)
    return date(
        data["Year"][-1], data["Month"][-1], data["Day"][-1]
    )


def download_symbol(symbol: str, start_date: date) -> pd.DataFrame:
    # yfinance expects start as string in ISO format
    return yf.download(symbol, start=start_date.isoformat(), progress=False)


def append_data(db: AmiDataBase, symbol: str, df: pd.DataFrame):
    for ts, row in df.iterrows():
        entry = SymbolEntry(
            Day=ts.day,
            Month=ts.month,
            Year=ts.year,
            Close=float(row["Close"]),
            High=float(row["High"]),
            Low=float(row["Low"]),
            Open=float(row["Open"]),
            Volume=float(row["Volume"]),
        )
        db.append_symbol_entry(symbol, entry)


def update_database(db_path: Path):
    db = AmiDataBase(str(db_path))
    for symbol in db.get_symbols():
        last_date = get_last_date(db, symbol)
        start = last_date + timedelta(days=1)
        if start > date.today():
            continue
        df = download_symbol(symbol, start)
        if not df.empty:
            append_data(db, symbol, df)
    db.write_database()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update AmiBroker DB from Yahoo")
    parser.add_argument("db", type=Path, help="Path to AmiBroker database")
    args = parser.parse_args()
    update_database(args.db)
