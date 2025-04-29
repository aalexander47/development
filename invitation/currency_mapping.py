from .variation_mapping import VARIATION_MAPPING
from .country_mapping import COUNTRIES

CURRENCY_MAPPING = {
    "AE": {"currency": "AED", "exchange_rate": 0.044, "symbol": "د.إ", "name": "UAE Dirham"},
    "AL": {"currency": "ALL", "exchange_rate": 1.16, "symbol": "Lek", "name": "Albanian Lek"},
    "AM": {"currency": "AMD", "exchange_rate": 4.82, "symbol": "֏", "name": "Armenian Dram"},
    "AR": {"currency": "ARS", "exchange_rate": 10.25, "symbol": "AR$", "name": "Argentine Peso"},
    "AU": {"currency": "AUD", "exchange_rate": 0.018, "symbol": "AU$", "name": "Australian Dollar"},
    "AW": {"currency": "AWG", "exchange_rate": 0.022, "symbol": "ƒ", "name": "Aruban Florin"},
    "BB": {"currency": "BBD", "exchange_rate": 0.024, "symbol": "Bds$", "name": "Barbadian Dollar"},
    "BD": {"currency": "BDT", "exchange_rate": 1.16, "symbol": "Tk", "name": "Bangladeshi Taka"},
    "BM": {"currency": "BMD", "exchange_rate": 0.012, "symbol": "$", "name": "Bermudian Dollar"},
    "BN": {"currency": "BND", "exchange_rate": 0.016, "symbol": "BN$", "name": "Brunei Dollar"},
    "BO": {"currency": "BOB", "exchange_rate": 0.083, "symbol": "Bs", "name": "Bolivian Boliviano"},
    "BS": {"currency": "BSD", "exchange_rate": 0.012, "symbol": "B$", "name": "Bahamian Dollar"},
    "BW": {"currency": "BWP", "exchange_rate": 0.16, "symbol": "P", "name": "Botswana Pula"},
    "BZ": {"currency": "BZD", "exchange_rate": 0.024, "symbol": "BZ$", "name": "Belize Dollar"},
    "CA": {"currency": "CAD", "exchange_rate": 0.016, "symbol": "CA$", "name": "Canadian Dollar"},
    "CN": {"currency": "CNY", "exchange_rate": 0.087, "symbol": "¥", "name": "Chinese Yuan"},
    "CO": {"currency": "COP", "exchange_rate": 48.50, "symbol": "CO$", "name": "Colombian Peso"},
    "CR": {"currency": "CRC", "exchange_rate": 6.25, "symbol": "₡", "name": "Costa Rican Colon"},
    "CU": {"currency": "CUP", "exchange_rate": 0.30, "symbol": "$", "name": "Cuban Peso"},
    "CZ": {"currency": "CZK", "exchange_rate": 0.28, "symbol": "Kč", "name": "Czech Koruna"},
    "DK": {"currency": "DKK", "exchange_rate": 0.083, "symbol": "kr", "name": "Danish Krone"},
    "DO": {"currency": "DOP", "exchange_rate": 0.70, "symbol": "RD$", "name": "Dominican Peso"},
    "DZ": {"currency": "DZD", "exchange_rate": 1.62, "symbol": "DA", "name": "Algerian Dinar"},
    "EG": {"currency": "EGP", "exchange_rate": 0.37, "symbol": "E£", "name": "Egyptian Pound"},
    "ET": {"currency": "ETB", "exchange_rate": 0.68, "symbol": "Br", "name": "Ethiopian Birr"},
    "FJ": {"currency": "FJD", "exchange_rate": 0.027, "symbol": "FJ$", "name": "Fijian Dollar"},
    "GI": {"currency": "GIP", "exchange_rate": 0.0096, "symbol": "£", "name": "Gibraltar Pound"},
    "GM": {"currency": "GMD", "exchange_rate": 0.64, "symbol": "D", "name": "Gambian Dalasi"},
    "GT": {"currency": "GTQ", "exchange_rate": 0.094, "symbol": "Q", "name": "Guatemalan Quetzal"},
    "GY": {"currency": "GYD", "exchange_rate": 2.50, "symbol": "G$", "name": "Guyanese Dollar"},
    "GH": {"currency": "GHS", "exchange_rate": 0.10, "symbol": "GH₵", "name": "Ghanaian Cedi"},
    "HK": {"currency": "HKD", "exchange_rate": 0.094, "symbol": "HK$", "name": "Hong Kong Dollar"},
    "HN": {"currency": "HNL", "exchange_rate": 0.30, "symbol": "L", "name": "Honduran Lempira"},
    "HR": {"currency": "HRK", "exchange_rate": 0.11, "symbol": "kn", "name": "Croatian Kuna"},
    "HT": {"currency": "HTG", "exchange_rate": 1.60, "symbol": "G", "name": "Haitian Gourde"},
    "HU": {"currency": "HUF", "exchange_rate": 4.30, "symbol": "Ft", "name": "Hungarian Forint"},
    "ID": {"currency": "IDR", "exchange_rate": 195.0, "symbol": "Rp", "name": "Indonesian Rupiah"},
    "IL": {"currency": "ILS", "exchange_rate": 0.045, "symbol": "₪", "name": "Israeli Shekel"},
    "IN": {"currency": "INR", "exchange_rate": 1.0, "symbol": "₹", "name": "Indian Rupee"},
    "JM": {"currency": "JMD", "exchange_rate": 1.86, "symbol": "J$", "name": "Jamaican Dollar"},
    "KE": {"currency": "KES", "exchange_rate": 1.60, "symbol": "Ksh", "name": "Kenyan Shilling"},
    "KG": {"currency": "KGS", "exchange_rate": 1.06, "symbol": "Лв", "name": "Kyrgyzstani Som"},
    "KH": {"currency": "KHR", "exchange_rate": 49.0, "symbol": "៛", "name": "Cambodian Riel"},
    "KY": {"currency": "KYD", "exchange_rate": 0.0098, "symbol": "$", "name": "Cayman Dollar"},
    "KZ": {"currency": "KZT", "exchange_rate": 5.60, "symbol": "₸", "name": "Kazakhstani Tenge"},
    "LA": {"currency": "LAK", "exchange_rate": 200.0, "symbol": "₭", "name": "Lao Kip"},
    "LB": {"currency": "LBP", "exchange_rate": 1800.0, "symbol": "ل.ل", "name": "Lebanese Pound"},
    "LK": {"currency": "LKR", "exchange_rate": 3.70, "symbol": "Rs", "name": "Sri Lankan Rupee"},
    "LR": {"currency": "LRD", "exchange_rate": 1.92, "symbol": "L$", "name": "Liberian Dollar"},
    "LS": {"currency": "LSL", "exchange_rate": 0.18, "symbol": "L", "name": "Lesotho Loti"},
    "MA": {"currency": "MAD", "exchange_rate": 0.12, "symbol": "DH", "name": "Moroccan Dirham"},
    "MD": {"currency": "MDL", "exchange_rate": 0.21, "symbol": "L", "name": "Moldovan Leu"},
    "MK": {"currency": "MKD", "exchange_rate": 0.68, "symbol": "ден", "name": "Macedonian Denar"},
    "MM": {"currency": "MMK", "exchange_rate": 25.0, "symbol": "K", "name": "Myanmar Kyat"},
    "MN": {"currency": "MNT", "exchange_rate": 42.0, "symbol": "₮", "name": "Mongolian Tugrik"},
    "MO": {"currency": "MOP", "exchange_rate": 0.096, "symbol": "MOP$", "name": "Macanese Pataca"},
    "MU": {"currency": "MUR", "exchange_rate": 0.55, "symbol": "Rs", "name": "Mauritian Rupee"},
    "MV": {"currency": "MVR", "exchange_rate": 0.19, "symbol": "Rf", "name": "Maldivian Rufiyaa"},
    "MW": {"currency": "MWK", "exchange_rate": 16.0, "symbol": "MK", "name": "Malawian Kwacha"},
    "MY": {"currency": "MYR", "exchange_rate": 0.057, "symbol": "RM", "name": "Malaysian Ringgit"},
    "MX": {"currency": "MXN", "exchange_rate": 0.20, "symbol": "MX$", "name": "Mexican Peso"},
    "NA": {"currency": "NAD", "exchange_rate": 0.18, "symbol": "N$", "name": "Namibian Dollar"},
    "NG": {"currency": "NGN", "exchange_rate": 16.0, "symbol": "₦", "name": "Nigerian Naira"},
    "NI": {"currency": "NIO", "exchange_rate": 0.44, "symbol": "C$", "name": "Nicaraguan Cordoba"},
    "NO": {"currency": "NOK", "exchange_rate": 0.13, "symbol": "kr", "name": "Norwegian Krone"},
    "NP": {"currency": "NPR", "exchange_rate": 1.60, "symbol": "Rs", "name": "Nepalese Rupee"},
    "NZ": {"currency": "NZD", "exchange_rate": 0.020, "symbol": "NZ$", "name": "New Zealand Dollar"},
    "PE": {"currency": "PEN", "exchange_rate": 0.045, "symbol": "S/", "name": "Peruvian Sol"},
    "PG": {"currency": "PGK", "exchange_rate": 0.045, "symbol": "K", "name": "Papua New Guinean Kina"},
    "PH": {"currency": "PHP", "exchange_rate": 0.70, "symbol": "₱", "name": "Philippine Peso"},
    "PK": {"currency": "PKR", "exchange_rate": 3.30, "symbol": "Rs", "name": "Pakistani Rupee"},
    "QA": {"currency": "QAR", "exchange_rate": 0.044, "symbol": "ر.ق", "name": "Qatari Riyal"},
    "RU": {"currency": "RUB", "exchange_rate": 1.10, "symbol": "₽", "name": "Russian Ruble"},
    "SA": {"currency": "SAR", "exchange_rate": 0.045, "symbol": "SR", "name": "Saudi Riyal"},
    "SE": {"currency": "SEK", "exchange_rate": 0.13, "symbol": "kr", "name": "Swedish Krona"},
    "SG": {"currency": "SGD", "exchange_rate": 0.016, "symbol": "S$", "name": "Singapore Dollar"},
    "TH": {"currency": "THB", "exchange_rate": 0.43, "symbol": "฿", "name": "Thai Baht"},
    "TT": {"currency": "TTD", "exchange_rate": 0.081, "symbol": "TT$", "name": "Trinidad Dollar"},
    "TZ": {"currency": "TZS", "exchange_rate": 31.0, "symbol": "TSh", "name": "Tanzanian Shilling"},
    "UY": {"currency": "UYU", "exchange_rate": 0.45, "symbol": "$U", "name": "Uruguayan Peso"},
    "UZ": {"currency": "UZS", "exchange_rate": 1500.0, "symbol": "so'm", "name": "Uzbekistani Som"},
    "US": {"currency": "USD", "exchange_rate": 0.012, "symbol": "$", "name": "US Dollar"},
    "ZA": {"currency": "ZAR", "exchange_rate": 0.23, "symbol": "R", "name": "South African Rand"},
    "DEFAULT": {"currency": "USD", "exchange_rate": 0.012, "symbol": "$", "name": "US Dollar"}
}


def get_currency_info(country_code):
    return CURRENCY_MAPPING.get(country_code, CURRENCY_MAPPING["DEFAULT"])

# def calculate_price(base_price, country_code):
#     currency_info = get_currency_info(country_code)
#     final_price = base_price * currency_info["variation"]
#     return {
#         "price": round(final_price, 2),
#         "currency": currency_info["currency"],
#         "symbol": currency_info["symbol"],
#         "name": currency_info["name"]
#     }

def calculate_price(base_price_inr, country_code):
    """
    Calculate the adjusted price with resistance for higher variations.
    
    Args:
        base_price_inr (float): Base price in Indian Rupees (INR)
        country_code (str): 2-letter country code (e.g., "US", "SG")
    
    Returns:
        dict: {
            "original_price_inr": base_price_inr,
            "adjusted_price_inr": adjusted_price_inr,
            "converted_price": converted_price,
            "currency": currency_code,
            "symbol": currency_symbol,
            "exchange_rate": exchange_rate,
            "variation": variation,
            "resistance": resistance,
            "country_code": country_code
        }
    """
    # Get currency and variation data
    country_currency = CURRENCY_MAPPING.get(country_code, CURRENCY_MAPPING["DEFAULT"])
    variation = VARIATION_MAPPING.get(country_code, 1.0)
    
    # Calculate resistance (only for variation > 1)
    resistance = 0
    if variation > 1:
        # Resistance formula: starts at 1 for variation=5, scales proportionally
        resistance = min(0.8 * variation, variation - 1)  # Caps resistance to prevent negative prices
        resistance = round(resistance, 2)
    
    # Calculate adjusted price with resistance
    adjusted_price_inr = base_price_inr * (variation - resistance)
    
    # Convert to target currency
    exchange_rate = country_currency["exchange_rate"]
    converted_price = adjusted_price_inr * exchange_rate
    
    data = {
        "original_price_inr": base_price_inr,
        "adjusted_price_inr": round(adjusted_price_inr, 2),
        "converted_price": round(converted_price, 2),
        "currency": country_currency["currency"],
        "symbol": country_currency["symbol"],
        "exchange_rate": exchange_rate,
        "variation": variation,
        "resistance": resistance,
        "country_code": country_code
    }
    return data
