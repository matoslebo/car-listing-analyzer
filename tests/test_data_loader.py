import pytest
from pathlib import Path

from app.models.listing import CarListing
from app.services.data_loader import load_listings


# Path to test fixtures
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "test_data.csv"


def test_load_listings_returns_list_of_carlisting():
    """Happy path: returns a list of CarListing instances."""
    listings = load_listings(str(FIXTURE_PATH))
    
    assert isinstance(listings, list)
    assert len(listings) == 2
    assert all(isinstance(l, CarListing) for l in listings)


def test_load_listings_drops_nan_rows():
    """Rows with NaN in core columns must be dropped."""
    listings = load_listings(str(FIXTURE_PATH))
    
    # The CSV has 1 row with NaN in Make column.
    # After cleaning, no listing should have NaN/None as a Make.
    for listing in listings:
        assert listing.make is not None
        assert isinstance(listing.make, str)
        assert len(listing.make) > 0

def test_load_listings_drops_technical_artifacts():
    """Rows with Mileage_km == 16777215 must be dropped."""
    listings = load_listings(str(FIXTURE_PATH))
    
    # No listing should have km == 16777215
    assert all(l.km != 16777215 for l in listings)


def test_load_listings_filters_outliers():
    """Outlier prices and mileages must be filtered."""
    listings = load_listings(str(FIXTURE_PATH))
    
    # Bugatti at 2.5M EUR and Honda at 1 EUR should both be filtered
    assert all(100 <= l.price <= 300_000 for l in listings)


def test_load_listings_raises_when_no_data_remains(tmp_path):
    """Sanity check: empty CSV after cleaning must raise ValueError."""
    # Create a CSV that will be fully filtered out (all outliers)
    bad_csv = tmp_path / "bad.csv"
    bad_csv.write_text(
        "Make,Model,Body,Mileage_km,Price,Year,Country,Condition,Fuel_Type,"
        "Fuel_Consumption_l,Drivetrain,Gearbox,Gears,Power_hp,Engine_Size_cc,"
        "Cylinders,Seats,Doors,Color,Upholstery,Full_Service_History,"
        "Non_Smoker_Vehicle,Previous_Owners,Seller,Image_url\n"
        "BMW,X,Y,999999,1,2018,DE,Used,Diesel,5,RWD,Manual,6,184,1995,4,5,4,Black,Cloth,True,True,2,Dealer,\n"
    )
    
    with pytest.raises(ValueError, match="No listings remaining"):
        load_listings(str(bad_csv))