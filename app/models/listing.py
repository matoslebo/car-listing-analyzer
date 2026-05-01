HIGH_MILEAGE_THRESHOLD = 20_000

class CarListing:

    def __init__(self, make: str, model:str, year: int, km: int, price:int):
        self.make = make
        self.model = model
        self.year = year
        self.km = km
        self.price = price

    def age_in_years(self, current_year: int) -> int:
        return current_year - self.year
    
    def km_per_year(self, current_year: int) -> float:
        age = self.age_in_years(current_year)
        if age > 0:
            return self.km / age
        return 0.0

    def is_high_mileage(self, current_year: int) -> bool:
        return self.km_per_year(current_year) > HIGH_MILEAGE_THRESHOLD
    
    def to_dict(self, current_year: int) -> dict:
        return {
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "km": self.km,
            "price": self.price,
            "age_years": self.age_in_years(current_year),
            "km_per_year": self.km_per_year(current_year),
            "high_mileage": self.is_high_mileage(current_year)
        }


