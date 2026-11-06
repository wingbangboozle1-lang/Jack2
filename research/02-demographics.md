# Research Notes — T2: Demographics & Housing (US Census Bureau QuickFacts)

Source (all rows below): U.S. Census Bureau QuickFacts, "Los Angeles city, California; Los Angeles County, California", vintage V2025 / ACS 2020-2024 where noted.
URL: https://www.census.gov/quickfacts/fact/table/losangelescitycalifornia,losangelescountycalifornia/PST045224
Fetched: 2026-11-06. Values verified directly from the fetched page.

## Population
| Metric | LA city | LA County |
|---|---|---|
| Population estimates, July 1, 2025 (V2025) | 3,869,089 | 9,694,934 |
| Population estimates base, April 1, 2020 (V2025) | 3,899,342 | 10,017,414 |
| Population, percent change 4/1/2020→7/1/2025 (V2025) | -0.8% | -3.2% |
| Population, Census, April 1, 2020 | 3,898,747 | 10,014,009 |
| Population, Census, April 1, 2010 | 3,792,621 | 9,818,605 |

## Age / households
| Metric | LA city | LA County |
|---|---|---|
| Persons under 18 years, percent | 19.2% | 19.2% |
| Persons 65 years and over, percent | 14.2% | 17.1% |
| Female persons, percent | 50.2% | 51.1% |
| Households, 2020-2024 | 1,439,097 | 3,416,449 |
| Persons per household, 2020-2024 | 2.61 | 2.81 |
| Foreign-born persons, percent, 2020-2024 | 35.7% | 33.4% |
| Hispanic or Latino, percent | 47.2% | 49.3% |
| Asian alone, percent | 12.1% | 16.6% |
| White alone not Hispanic, percent | 28.1% | 24.6% |
| Black alone, percent | 8.4% | 8.9% |

## Housing
| Metric | LA city | LA County |
|---|---|---|
| Owner-occupied housing unit rate, 2020-2024 | 36.0% | 45.9% |
| Median value of owner-occupied housing units, 2020-2024 | $921,200 | $834,200 |
| Median gross rent, 2020-2024 | $1,933 | $1,954 |
| Building permits, 2025 | [X not published for city] | 22,250 |

## Education
| Metric | LA city | LA County |
|---|---|---|
| High school graduate or higher, pct 25+, 2020-2024 | 79.6% | 80.9% |
| Bachelor's degree or higher, pct 25+, 2020-2024 | 38.5% | 36.0% |

## Economy / income (QuickFacts)
| Metric | LA city | LA County |
|---|---|---|
| In civilian labor force, pct 16+, 2020-2024 | 66.4% | 64.7% |
| Median household income (2024$), 2020-2024 | $81,939 | $90,112 |
| Per capita income (2024$), 2020-2024 | $47,685 | $45,792 |
| Persons in poverty, percent | 16.5% | 13.3% |
| Total accommodation & food services sales, 2022 ($1,000) | 17,366,966 | 44,000,801 |
| Total retail sales, 2022 ($1,000) | 81,351,523 | 213,932,785 |
| Total employment, 2023 (county) | n/a city | 3,987,736 |
| Total employment, percent change 2022-2023 (county) | n/a city | +2.3% |
| Mean travel time to work, 2020-2024 | 30.7 min | 30.4 min |

## Census API note (irregularity)
api.census.gov now requires an API key (returns "Missing Key" page), so ZCTA-level ACS
pulls were unavailable without a key. ZIP-level income is instead sourced from IRS SOI
(official) and rents from HUD FMR (official). City/county numbers above are from the
fetchable QuickFacts page.

## Context: "Central Los Angeles"
"Central Los Angeles" is not a Census place; it is a planning region used by the City of
Los Angeles (LA City Planning community plan areas such as Central City, Central City
North, Wilshire, Silver Lake–Echo Park–Elysian Valley) and by neighborhood mapping.
Property-level analysis therefore uses placeholders + city/county/ZIP official data.
