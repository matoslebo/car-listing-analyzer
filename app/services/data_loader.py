import pandas as pd
from app.models.listing import CarListing

def load_listings(csv_path: str) -> list[CarListing]:
    """
    Loads and cleans car listings from CSV.
    Returns a list of CarListing domain objects.
    """

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    before = len(df)
    df = df.dropna(subset=['Make', 'Model', 'Year', 'Mileage_km', 'Price'])
    print(f"Dropped {before - len(df)} rows with NaN in core columns. Remaining: {len(df)}")

    before = len(df)
    df = df[df['Mileage_km'] != 16777215]
    print(f"Dropped {before - len(df)} technical artifacts (Mileage_km == 16777215). Remaining: {len(df)}")

    before = len(df)
    df = df[
        (df['Year'] >= 1950) & (df['Year'] <= 2026) &
        (df['Price'] >= 100) & (df['Price'] <= 300_000) &
        (df['Mileage_km'] >= 0) & (df['Mileage_km'] <= 500_000)
    ]
    print(f"Dropped {before - len(df)} outliers. Remaining: {len(df)}")

    df['Year'] = df['Year'].astype(int)
    df['Mileage_km'] = df['Mileage_km'].astype(int)

    before = len(df)
    df = df.drop_duplicates()
    print(f"Dropped {before - len(df)} duplicates. Remaining: {len(df)}")

    listings = []
    for _, row in df.iterrows():
        listing = CarListing(
            make=row['Make'],
            model=row['Model'],
            year=row['Year'],
            km=row['Mileage_km'],
            price=row['Price']
        )
        listings.append(listing)

    print(f"Converted to {len(listings)} CarListing objects")

    # Sanity check
    if len(listings) == 0:
        raise ValueError(f"No listings remaining after cleaning. Check thresholds.")
    
    return listings