"""
Master universe of ~100 S&P 500 tickers for public comps benchmarking.

Each entry includes GICS sector, GICS industry, and market cap category.
This module is the single source of truth for which companies are tracked
across all ingestion scripts.
"""

UNIVERSE = [
    # ──────────────────────────────────────────────────────────────────────
    # INFORMATION TECHNOLOGY (10)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "AAPL",  "name": "Apple Inc.",                    "gics_sector": "Information Technology", "gics_industry": "Technology Hardware, Storage & Peripherals", "market_cap_category": "large"},
    {"ticker": "MSFT",  "name": "Microsoft Corp.",               "gics_sector": "Information Technology", "gics_industry": "Systems Software",                          "market_cap_category": "large"},
    {"ticker": "NVDA",  "name": "NVIDIA Corp.",                  "gics_sector": "Information Technology", "gics_industry": "Semiconductors",                            "market_cap_category": "large"},
    {"ticker": "AVGO",  "name": "Broadcom Inc.",                 "gics_sector": "Information Technology", "gics_industry": "Semiconductors",                            "market_cap_category": "large"},
    {"ticker": "CRM",   "name": "Salesforce Inc.",               "gics_sector": "Information Technology", "gics_industry": "Application Software",                      "market_cap_category": "large"},
    {"ticker": "ADBE",  "name": "Adobe Inc.",                    "gics_sector": "Information Technology", "gics_industry": "Application Software",                      "market_cap_category": "large"},
    {"ticker": "ACN",   "name": "Accenture plc",                 "gics_sector": "Information Technology", "gics_industry": "IT Consulting & Other Services",            "market_cap_category": "large"},
    {"ticker": "INTC",  "name": "Intel Corp.",                   "gics_sector": "Information Technology", "gics_industry": "Semiconductors",                            "market_cap_category": "large"},
    {"ticker": "CDNS",  "name": "Cadence Design Systems Inc.",   "gics_sector": "Information Technology", "gics_industry": "Application Software",                      "market_cap_category": "large"},
    {"ticker": "FFIV",  "name": "F5 Inc.",                       "gics_sector": "Information Technology", "gics_industry": "Communications Equipment",                  "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # HEALTH CARE (10)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "UNH",   "name": "UnitedHealth Group Inc.",       "gics_sector": "Health Care", "gics_industry": "Managed Health Care",                "market_cap_category": "large"},
    {"ticker": "JNJ",   "name": "Johnson & Johnson",             "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals",                    "market_cap_category": "large"},
    {"ticker": "LLY",   "name": "Eli Lilly and Co.",             "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals",                    "market_cap_category": "large"},
    {"ticker": "ABT",   "name": "Abbott Laboratories",           "gics_sector": "Health Care", "gics_industry": "Health Care Equipment",              "market_cap_category": "large"},
    {"ticker": "TMO",   "name": "Thermo Fisher Scientific Inc.", "gics_sector": "Health Care", "gics_industry": "Life Sciences Tools & Services",     "market_cap_category": "large"},
    {"ticker": "DHR",   "name": "Danaher Corp.",                 "gics_sector": "Health Care", "gics_industry": "Life Sciences Tools & Services",     "market_cap_category": "large"},
    {"ticker": "BMY",   "name": "Bristol-Myers Squibb Co.",      "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals",                    "market_cap_category": "large"},
    {"ticker": "SYK",   "name": "Stryker Corp.",                 "gics_sector": "Health Care", "gics_industry": "Health Care Equipment",              "market_cap_category": "large"},
    {"ticker": "ZBH",   "name": "Zimmer Biomet Holdings Inc.",   "gics_sector": "Health Care", "gics_industry": "Health Care Equipment",              "market_cap_category": "mid"},
    {"ticker": "VTRS",  "name": "Viatris Inc.",                  "gics_sector": "Health Care", "gics_industry": "Pharmaceuticals",                    "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # CONSUMER DISCRETIONARY (10)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "AMZN",  "name": "Amazon.com Inc.",               "gics_sector": "Consumer Discretionary", "gics_industry": "Broadline Retail",                  "market_cap_category": "large"},
    {"ticker": "TSLA",  "name": "Tesla Inc.",                    "gics_sector": "Consumer Discretionary", "gics_industry": "Automobile Manufacturers",            "market_cap_category": "large"},
    {"ticker": "HD",    "name": "The Home Depot Inc.",           "gics_sector": "Consumer Discretionary", "gics_industry": "Home Improvement Retail",             "market_cap_category": "large"},
    {"ticker": "MCD",   "name": "McDonald's Corp.",              "gics_sector": "Consumer Discretionary", "gics_industry": "Restaurants",                         "market_cap_category": "large"},
    {"ticker": "NKE",   "name": "NIKE Inc.",                     "gics_sector": "Consumer Discretionary", "gics_industry": "Footwear",                            "market_cap_category": "large"},
    {"ticker": "LOW",   "name": "Lowe's Companies Inc.",         "gics_sector": "Consumer Discretionary", "gics_industry": "Home Improvement Retail",             "market_cap_category": "large"},
    {"ticker": "SBUX",  "name": "Starbucks Corp.",               "gics_sector": "Consumer Discretionary", "gics_industry": "Restaurants",                         "market_cap_category": "large"},
    {"ticker": "TJX",   "name": "The TJX Companies Inc.",        "gics_sector": "Consumer Discretionary", "gics_industry": "Apparel Retail",                      "market_cap_category": "large"},
    {"ticker": "GM",    "name": "General Motors Co.",            "gics_sector": "Consumer Discretionary", "gics_industry": "Automobile Manufacturers",            "market_cap_category": "mid"},
    {"ticker": "POOL",  "name": "Pool Corp.",                    "gics_sector": "Consumer Discretionary", "gics_industry": "Distributors",                        "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # COMMUNICATION SERVICES (8)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "GOOGL", "name": "Alphabet Inc.",                 "gics_sector": "Communication Services", "gics_industry": "Interactive Media & Services",        "market_cap_category": "large"},
    {"ticker": "META",  "name": "Meta Platforms Inc.",           "gics_sector": "Communication Services", "gics_industry": "Interactive Media & Services",        "market_cap_category": "large"},
    {"ticker": "NFLX",  "name": "Netflix Inc.",                  "gics_sector": "Communication Services", "gics_industry": "Movies & Entertainment",              "market_cap_category": "large"},
    {"ticker": "DIS",   "name": "The Walt Disney Co.",           "gics_sector": "Communication Services", "gics_industry": "Movies & Entertainment",              "market_cap_category": "large"},
    {"ticker": "CMCSA", "name": "Comcast Corp.",                 "gics_sector": "Communication Services", "gics_industry": "Cable & Satellite",                   "market_cap_category": "large"},
    {"ticker": "TMUS",  "name": "T-Mobile US Inc.",              "gics_sector": "Communication Services", "gics_industry": "Wireless Telecommunication Services", "market_cap_category": "large"},
    {"ticker": "VZ",    "name": "Verizon Communications Inc.",   "gics_sector": "Communication Services", "gics_industry": "Integrated Telecommunication Services", "market_cap_category": "large"},
    {"ticker": "OMC",   "name": "Omnicom Group Inc.",            "gics_sector": "Communication Services", "gics_industry": "Advertising",                         "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # INDUSTRIALS (10)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "CAT",   "name": "Caterpillar Inc.",              "gics_sector": "Industrials", "gics_industry": "Construction Machinery & Heavy Transportation Equipment", "market_cap_category": "large"},
    {"ticker": "UNP",   "name": "Union Pacific Corp.",           "gics_sector": "Industrials", "gics_industry": "Railroads",                          "market_cap_category": "large"},
    {"ticker": "HON",   "name": "Honeywell International Inc.",  "gics_sector": "Industrials", "gics_industry": "Industrial Conglomerates",            "market_cap_category": "large"},
    {"ticker": "RTX",   "name": "RTX Corp.",                     "gics_sector": "Industrials", "gics_industry": "Aerospace & Defense",                 "market_cap_category": "large"},
    {"ticker": "DE",    "name": "Deere & Co.",                   "gics_sector": "Industrials", "gics_industry": "Agricultural & Farm Machinery",       "market_cap_category": "large"},
    {"ticker": "LMT",   "name": "Lockheed Martin Corp.",         "gics_sector": "Industrials", "gics_industry": "Aerospace & Defense",                 "market_cap_category": "large"},
    {"ticker": "WM",    "name": "Waste Management Inc.",         "gics_sector": "Industrials", "gics_industry": "Environmental & Facilities Services", "market_cap_category": "large"},
    {"ticker": "GE",    "name": "GE Aerospace",                  "gics_sector": "Industrials", "gics_industry": "Aerospace & Defense",                 "market_cap_category": "large"},
    {"ticker": "FTV",   "name": "Fortive Corp.",                 "gics_sector": "Industrials", "gics_industry": "Industrial Machinery & Supplies & Components", "market_cap_category": "mid"},
    {"ticker": "XYL",   "name": "Xylem Inc.",                    "gics_sector": "Industrials", "gics_industry": "Industrial Machinery & Supplies & Components", "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # CONSUMER STAPLES (9)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "PG",    "name": "Procter & Gamble Co.",          "gics_sector": "Consumer Staples", "gics_industry": "Household Products",              "market_cap_category": "large"},
    {"ticker": "KO",    "name": "The Coca-Cola Co.",             "gics_sector": "Consumer Staples", "gics_industry": "Soft Drinks & Non-alcoholic Beverages", "market_cap_category": "large"},
    {"ticker": "PEP",   "name": "PepsiCo Inc.",                  "gics_sector": "Consumer Staples", "gics_industry": "Soft Drinks & Non-alcoholic Beverages", "market_cap_category": "large"},
    {"ticker": "COST",  "name": "Costco Wholesale Corp.",        "gics_sector": "Consumer Staples", "gics_industry": "Consumer Staples Merchandise Retail",   "market_cap_category": "large"},
    {"ticker": "WMT",   "name": "Walmart Inc.",                  "gics_sector": "Consumer Staples", "gics_industry": "Consumer Staples Merchandise Retail",   "market_cap_category": "large"},
    {"ticker": "PM",    "name": "Philip Morris International",   "gics_sector": "Consumer Staples", "gics_industry": "Tobacco",                         "market_cap_category": "large"},
    {"ticker": "CL",    "name": "Colgate-Palmolive Co.",         "gics_sector": "Consumer Staples", "gics_industry": "Household Products",              "market_cap_category": "large"},
    {"ticker": "ADM",   "name": "Archer-Daniels-Midland Co.",    "gics_sector": "Consumer Staples", "gics_industry": "Agricultural Products & Services", "market_cap_category": "mid"},
    {"ticker": "SJM",   "name": "The J.M. Smucker Co.",          "gics_sector": "Consumer Staples", "gics_industry": "Packaged Foods & Meats",          "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # ENERGY (8)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "XOM",   "name": "Exxon Mobil Corp.",             "gics_sector": "Energy", "gics_industry": "Integrated Oil & Gas",                      "market_cap_category": "large"},
    {"ticker": "CVX",   "name": "Chevron Corp.",                 "gics_sector": "Energy", "gics_industry": "Integrated Oil & Gas",                      "market_cap_category": "large"},
    {"ticker": "COP",   "name": "ConocoPhillips",               "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production",        "market_cap_category": "large"},
    {"ticker": "SLB",   "name": "Schlumberger NV",               "gics_sector": "Energy", "gics_industry": "Oil & Gas Equipment & Services",            "market_cap_category": "large"},
    {"ticker": "EOG",   "name": "EOG Resources Inc.",            "gics_sector": "Energy", "gics_industry": "Oil & Gas Exploration & Production",        "market_cap_category": "large"},
    {"ticker": "PSX",   "name": "Phillips 66",                   "gics_sector": "Energy", "gics_industry": "Oil & Gas Refining & Marketing",            "market_cap_category": "mid"},
    {"ticker": "VLO",   "name": "Valero Energy Corp.",           "gics_sector": "Energy", "gics_industry": "Oil & Gas Refining & Marketing",            "market_cap_category": "mid"},
    {"ticker": "HAL",   "name": "Halliburton Co.",               "gics_sector": "Energy", "gics_industry": "Oil & Gas Equipment & Services",            "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # MATERIALS (8)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "LIN",   "name": "Linde plc",                    "gics_sector": "Materials", "gics_industry": "Industrial Gases",                       "market_cap_category": "large"},
    {"ticker": "APD",   "name": "Air Products and Chemicals",    "gics_sector": "Materials", "gics_industry": "Industrial Gases",                       "market_cap_category": "large"},
    {"ticker": "SHW",   "name": "The Sherwin-Williams Co.",      "gics_sector": "Materials", "gics_industry": "Specialty Chemicals",                    "market_cap_category": "large"},
    {"ticker": "ECL",   "name": "Ecolab Inc.",                   "gics_sector": "Materials", "gics_industry": "Specialty Chemicals",                    "market_cap_category": "large"},
    {"ticker": "FCX",   "name": "Freeport-McMoRan Inc.",         "gics_sector": "Materials", "gics_industry": "Copper",                                "market_cap_category": "large"},
    {"ticker": "NEM",   "name": "Newmont Corp.",                 "gics_sector": "Materials", "gics_industry": "Gold",                                  "market_cap_category": "large"},
    {"ticker": "VMC",   "name": "Vulcan Materials Co.",          "gics_sector": "Materials", "gics_industry": "Construction Materials",                 "market_cap_category": "mid"},
    {"ticker": "BLL",   "name": "Ball Corp.",                    "gics_sector": "Materials", "gics_industry": "Metal, Glass & Plastic Containers",     "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # REAL ESTATE (8)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "PLD",   "name": "Prologis Inc.",                 "gics_sector": "Real Estate", "gics_industry": "Industrial REITs",                    "market_cap_category": "large"},
    {"ticker": "AMT",   "name": "American Tower Corp.",          "gics_sector": "Real Estate", "gics_industry": "Telecom Tower REITs",                 "market_cap_category": "large"},
    {"ticker": "EQIX",  "name": "Equinix Inc.",                  "gics_sector": "Real Estate", "gics_industry": "Data Center REITs",                   "market_cap_category": "large"},
    {"ticker": "SPG",   "name": "Simon Property Group Inc.",     "gics_sector": "Real Estate", "gics_industry": "Retail REITs",                        "market_cap_category": "large"},
    {"ticker": "PSA",   "name": "Public Storage",                "gics_sector": "Real Estate", "gics_industry": "Self-Storage REITs",                  "market_cap_category": "large"},
    {"ticker": "O",     "name": "Realty Income Corp.",           "gics_sector": "Real Estate", "gics_industry": "Retail REITs",                        "market_cap_category": "large"},
    {"ticker": "WELL",  "name": "Welltower Inc.",                "gics_sector": "Real Estate", "gics_industry": "Health Care REITs",                   "market_cap_category": "large"},
    {"ticker": "ARE",   "name": "Alexandria Real Estate Equities", "gics_sector": "Real Estate", "gics_industry": "Office REITs",                     "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # UTILITIES (8)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "NEE",   "name": "NextEra Energy Inc.",           "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "large"},
    {"ticker": "DUK",   "name": "Duke Energy Corp.",             "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "large"},
    {"ticker": "SO",    "name": "The Southern Co.",              "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "large"},
    {"ticker": "D",     "name": "Dominion Energy Inc.",          "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "mid"},
    {"ticker": "SRE",   "name": "Sempra",                       "gics_sector": "Utilities", "gics_industry": "Multi-Utilities",                       "market_cap_category": "large"},
    {"ticker": "AEP",   "name": "American Electric Power Co.",   "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "mid"},
    {"ticker": "EXC",   "name": "Exelon Corp.",                  "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "mid"},
    {"ticker": "WEC",   "name": "WEC Energy Group Inc.",         "gics_sector": "Utilities", "gics_industry": "Electric Utilities",                    "market_cap_category": "mid"},

    # ──────────────────────────────────────────────────────────────────────
    # FINANCIALS (9) — exchanges, data vendors, fintech only (no banks/insurance)
    # ──────────────────────────────────────────────────────────────────────
    {"ticker": "V",     "name": "Visa Inc.",                     "gics_sector": "Financials", "gics_industry": "Transaction & Payment Processing Services", "market_cap_category": "large"},
    {"ticker": "MA",    "name": "Mastercard Inc.",               "gics_sector": "Financials", "gics_industry": "Transaction & Payment Processing Services", "market_cap_category": "large"},
    {"ticker": "SPGI",  "name": "S&P Global Inc.",               "gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "large"},
    {"ticker": "ICE",   "name": "Intercontinental Exchange Inc.","gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "large"},
    {"ticker": "CME",   "name": "CME Group Inc.",                "gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "large"},
    {"ticker": "MCO",   "name": "Moody's Corp.",                 "gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "large"},
    {"ticker": "MSCI",  "name": "MSCI Inc.",                     "gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "mid"},
    {"ticker": "FIS",   "name": "Fidelity National Information Services", "gics_sector": "Financials", "gics_industry": "Transaction & Payment Processing Services", "market_cap_category": "mid"},
    {"ticker": "NDAQ",  "name": "Nasdaq Inc.",                   "gics_sector": "Financials", "gics_industry": "Financial Exchanges & Data",          "market_cap_category": "mid"},
]


# ── Convenience exports ──────────────────────────────────────────────────

TICKERS = [t["ticker"] for t in UNIVERSE]

SECTORS = sorted(set(t["gics_sector"] for t in UNIVERSE))


def get_tickers_by_sector(sector: str) -> list[str]:
    """Return list of tickers belonging to a given GICS sector."""
    return [t["ticker"] for t in UNIVERSE if t["gics_sector"] == sector]


def get_universe_by_sector(sector: str) -> list[dict]:
    """Return full universe entries for a given GICS sector."""
    return [t for t in UNIVERSE if t["gics_sector"] == sector]
