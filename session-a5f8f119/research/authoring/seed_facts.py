import json
import os
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','..','data')
F=[]
def f(i,page,group,label,value,src,period='',geo='',kind='verified',note='',num=None,unit=''):
    d={'id':i,'page':page,'group':group,'label':label,'value':value,'unit':unit,'period':period,'geo':geo,'src':src if isinstance(src,list) else [src],'kind':kind,'note':note}
    if num is not None: d['num']=num
    F.append(d)
LA='Los Angeles County'; CITY='City of Los Angeles'; MSA='Los Angeles metro area (Los Angeles and Orange counties)'
# ---------------- PROPERTY AND LEASE ----------------
g='What the brief states'
f('P01','property',g,'Tenant brand','Jack in the Box','E12',geo='Subject property',kind='brief',note='Stated in the owner brief. The brand is a public company; its filings are the linked source. Nothing in a public record was matched to the property.')
f('P02','property',g,'Lease form','NNN (triple net)','E12',geo='Subject property',kind='brief',note='Stated in the brief. The tenant says its restaurant leases generally require it to pay real estate taxes, insurance and other expenses on top of rent.')
f('P03','property',g,'Lease expiry','Between 2030 and 2035','E12',geo='Subject property',kind='brief',note='A six-year window. The exact date is not known to this workbook and changes the answer; see the blank rows below.')
f('P04','property',g,'Location','Central Los Angeles','E03',geo='Subject property',kind='brief',note='A description, not a jurisdiction. Whether the parcel is inside the City of Los Angeles decides which transfer tax applies.')
g='What the tenant publishes about its own leases'
f('P05','property',g,'Jack in the Box restaurants on land the company leases from other owners','1,585 of 2,136','E12',period='September 28, 2025',geo='Jack in the Box system',kind='derived',num=1585,note='565 where the company owns the building on leased land plus 1,020 where it leases land and building.')
f('P06','property',g,'Sites where the company owns the building on leased land (ground leases)','565','E12',period='September 28, 2025',geo='Jack in the Box system',num=565,note='55 company-operated and 510 franchise-operated. If the subject is one of these, the owner holds land only and the building position at expiry is set by the lease.')
f('P07','property',g,'Sites where the company leases both land and building','1,020','E12',period='September 28, 2025',geo='Jack in the Box system',num=1020,note='87 company-operated and 933 franchise-operated.')
f('P08','property',g,'Sites the company owns outright (land and building)','164',['E12','E11'],period='September 28, 2025',geo='Jack in the Box system',num=164,note='The company says it pursues "the sale of our owned Jack in the Box properties" (Form 10-Q, liquidity). Those sales add competing supply of the same product.')
f('P09','property',g,'Sites owned or leased directly by franchisees','387','E12',period='September 28, 2025',geo='Jack in the Box system',num=387,note='If the subject is one of these, the tenant on the lease is a franchisee and not the public company.')
f('P10','property',g,'Rent structure the company describes','Fixed rent with cost-of-living index adjustments','E12',period='Fiscal 2025 Form 10-K',geo='Jack in the Box system',note='"Our restaurant leases generally provide for fixed rental payments (with cost-of-living index adjustments) plus real estate taxes, insurance, and other expenses."')
f('P11','property',g,'Leases that also carry percentage rent','About 13%','E12',period='Fiscal 2025 Form 10-K',geo='Jack in the Box system',num=13,unit='%',note='"between 1% and 10% of the restaurant\'s gross sales once certain thresholds are met".')
f('P12','property',g,'Company statement on renewals','"We have generally been able to renew our restaurant leases as they expire at then-current market rates."','E12',period='Fiscal 2025 Form 10-K',geo='Jack in the Box system',note='A general statement about the system. It is not a commitment about any one site.')
f('P13','property',g,'Prototype restaurant size','About 1,372 square feet','E12',period='Fiscal 2025 Form 10-K',geo='New-build prototype',num=1372,unit='sq ft',note='Describes new builds. The subject building size is blank below.')
f('P14','property',g,'Restaurants in California','941 of 2,136','E12',period='September 28, 2025',geo='California',num=941,note='96 company-operated and 845 franchise-operated. California is the largest state for the brand.')
g='Facts only the owner holds (blank until supplied)'
B=[('P20','Street address and parcel number','L02','Withheld by design and not known to this workbook.'),
('P21','Jurisdiction: inside the City of Los Angeles or another city','L01','Decides the transfer tax. Culver City and Santa Monica, for example, have their own schedules.'),
('P22','Annual base rent','L02','Every dollar figure in the model scales with this number.'),
('P23','Exact lease expiry date','L02','The brief gives 2030 to 2035.'),
('P24','Rent escalation clause (fixed steps, index, cap)','L02','With consumer prices up 3.7% in a year, a flat or capped lease is losing real value.'),
('P25','Renewal options: number, length, notice date and option rent','L02','Options belong to the tenant. An unexercised option notice date is the first hard signal.'),
('P26','Lease type: ground lease or land-and-building lease','L02','Decides who owns the building at expiry.'),
('P27','Tenant entity on the lease and any guarantor','L07','Public company, a subsidiary, or a franchisee. Ninety-three percent of the system is franchised.'),
('P28','Percentage rent, reported store sales and rent-to-sales ratio','L02','The best single predictor of renewal, and not public.'),
('P29','Purchase options, rights of first refusal or first offer','L02','Can cap the sale price or delay a sale.'),
('P30','Lot size, building size, year built, drive-through','L01','Sets land value and re-letting options.'),
('P31','Zoning, overlays and transit-area status','L01','Sets what could replace the restaurant.'),
('P32','Current assessed value and property tax bill','L02','A sale resets the assessed value for the buyer.'),
('P33','Owner tax basis, depreciation taken and holding entity','L02','Decides the tax on a sale. Never to be published.'),
('P34','Any loan on the property and its terms','L02','A prepayment penalty changes the sale arithmetic.'),
('P35','Environmental record for the parcel','L06','Fuel tanks and past uses nearby affect buyers and lenders.'),
('P36','Flood zone','L03','Parcel-level; not obtained.'),
('P37','Fault, liquefaction and landslide zone','L04','Parcel-level; not obtained.'),
('P38','Fire hazard severity zone','L05','Parcel-level; not obtained.'),
('P39','Insurance carrier, premium and who pays under the lease','L02','Under a triple-net lease the tenant usually pays, which makes it a renewal cost for the tenant.')]
for i,l,s,n in B: f(i,'property',g,l,'',s,geo='Subject property',kind='blank',note=n)
# ---------------- TENANT ----------------
g='Size and direction of the chain'
f('T01','tenant',g,'Jack in the Box restaurants','2,115','E11',period='July 5, 2026',geo='Jack in the Box system',num=2115,note='149 company-operated and 1,966 franchised.')
f('T02','tenant',g,'Restaurants a year earlier','2,168','E10',period='July 6, 2025',geo='Jack in the Box system',num=2168,note='142 company-operated and 2,026 franchised.')
f('T03','tenant',g,'Restaurants at fiscal 2025 year-end','2,136','E12',period='September 28, 2025',geo='Jack in the Box system',num=2136)
f('T04','tenant',g,'Restaurants at fiscal 2024 year-end','2,191','E12',period='September 29, 2024',geo='Jack in the Box system',num=2191)
f('T05','tenant',g,'Closures in fiscal 2025','86','E12',period='Fiscal 2025',geo='Jack in the Box system',num=86,note='11 company-operated and 75 franchised. Fiscal 2024: 25.')
f('T06','tenant',g,'Closures in the first 40 weeks of fiscal 2026','40','E11',period='40 weeks ended July 5, 2026',geo='Jack in the Box system',num=40,note='2 company-operated and 38 franchised; 19 openings.')
f('T07','tenant',g,'Guidance: restaurants at fiscal 2026 year-end','About 2,100','E10',period='Fiscal year ending September 27, 2026',geo='Jack in the Box system',num=2100,note='About 25 openings and about 50 to 60 closures, "most of which will be franchise restaurants".')
f('T08','tenant',g,'Share of restaurants run by franchisees','93%','E11',period='July 5, 2026',geo='Jack in the Box system',num=93,unit='%',note='The operator in most restaurants is a franchisee, whose finances are not public.')
f('T09','tenant',g,'Closure programme','"Restaurant closure program: Through block closure program, improving system health and encouraging franchisees to reinvest"','E12',period='Fiscal 2025 Form 10-K',geo='Jack in the Box system',note='Part of the "Jack on Track" plan. No list of sites is published.')
g='Sales'
f('T10','tenant',g,'System same-store sales, latest quarter','-1.1%','E10',period='12 weeks ended July 5, 2026',geo='Jack in the Box system',num=-1.1,unit='%',note='Against -7.1% in the same quarter a year earlier. "a decline in transactions, partially offset by an increase in price".')
f('T11','tenant',g,'System same-store sales, year to date','-4.2%','E11',period='40 weeks ended July 5, 2026',geo='Jack in the Box system',num=-4.2,unit='%',note='Printed in the Form 10-Q table; the earnings release prints the quarter only.')
f('T12','tenant',g,'Average sales per franchise restaurant','$1,874 thousand','E12',period='Fiscal 2025',geo='Jack in the Box franchise restaurants',num=1874,unit='USD thousand',note='Down from $1,949 thousand in fiscal 2024.')
f('T13','tenant',g,'Systemwide sales','$4,208.9 million','E12',period='Fiscal 2025',geo='Jack in the Box system',num=4208.937,unit='USD million',note='Fiscal 2024: $4,396.3 million.')
f('T14','tenant',g,'Wage inflation at company restaurants','About 7.6%','E12',period='Fiscal 2025',geo='Company-operated restaurants',num=7.6,unit='%',note='"primarily due to the wage increases required in California effective April 1, 2024 under AB 1228".')
f('T15','tenant',g,'Payroll and benefits as a share of company restaurant sales','33.8%','E12',period='Fiscal 2025',geo='Company-operated restaurants',num=33.8,unit='%',note='31.5% in fiscal 2024.')
g='Balance sheet and debt'
f('T20','tenant',g,'Total debt','$1,492.0 million','E11',period='July 5, 2026',geo='Jack in the Box Inc.',num=1491.984,unit='USD million',note='$1,715.6 million at September 28, 2025.')
f('T21','tenant',g,'Cash','$46.3 million','E11',period='July 5, 2026',geo='Jack in the Box Inc.',num=46.318,unit='USD million',note='Plus $25.5 million of restricted cash.')
f('T22','tenant',g,"Total stockholders' deficit",'($901.3 million)','E11',period='July 5, 2026',geo='Jack in the Box Inc.',num=-901.286,unit='USD million',note='Liabilities exceed assets.')
f('T23','tenant',g,'Operating cash flow, year to date','$56.6 million','E11',period='40 weeks ended July 5, 2026',geo='Continuing operations',num=56.553,unit='USD million',note='$118.1 million in the same period a year earlier.')
f('T24','tenant',g,'Cash flow lost to late franchisee payments','About $11.0 million','E11',period='40 weeks ended July 5, 2026',geo='Jack in the Box Inc.',num=11.0,unit='USD million',note='"delayed payments from franchisees, including amounts subject to payment deferral arrangements, a portion of which we have reserved against".')
f('T25','tenant',g,'New notes issued in June 2026','$500 million at 7.624%','E08',period='June 2026',geo='Securitization issuer',num=7.624,unit='%',note='They repaid notes carrying 4.476% and 3.445%.')
f('T26','tenant',g,'Leverage test, scheduled amortization','Leverage ratio greater than 5.0x','E11',period='July 5, 2026',geo='Securitization issuer',note='"accordingly, is making the scheduled amortization payments on its 2019, 2022 and 2026 Notes".')
f('T27','tenant',g,'Leverage test, cash sweep','Senior ABS Leverage Ratio greater than 5.25x','E11',period='July 5, 2026',geo='Securitization issuer',note='"cash sweeping prepayments of $23.3 million are included in \'Current maturities of long-term debt\'".')
f('T28','tenant',g,'Next large repayment dates','August 2029: $426.4 million; May 2031: $500.0 million; February 2032: $503.3 million','E11',period='July 5, 2026',geo='Securitization issuer',note='Anticipated repayment dates. All three fall inside or just before the 2030 to 2035 lease-expiry window.')
f('T29','tenant',g,'Dividend and share repurchases','Discontinued','E10',period='August 2026',geo='Jack in the Box Inc.',note='"the Company has discontinued its dividend and share repurchase program."')
f('T30','tenant',g,'Franchise rental revenue against franchise occupancy expense','$242.5 million against $166.0 million','E11',period='40 weeks ended July 5, 2026',geo='Jack in the Box Inc.',note='The company collects more rent from franchisees than it pays to landlords. A year earlier: $260.3 million against $169.9 million.')
f('T31','tenant',g,'Leadership','Interim chief executive; activist cooperation agreement extended','E09',period='September 2026',geo='Jack in the Box Inc.',note='Names are not recorded here.')
f('T32','tenant',g,'Fiscal 2026 fourth-quarter results','','E07',period='Fiscal year ended September 27, 2026',geo='Jack in the Box Inc.',kind='blank',note='Not filed by November 10, 2026. The Form 10-Q for July 5, 2026 is the latest periodic report.')
# ---------------- AREA: people ----------------
g='Population'
f('A01','area',g,'Population, July 1, 2025','3,869,089','E03',period='July 1, 2025 (Vintage 2025)',geo=CITY,num=3869089,note='Down 0.8% from the April 1, 2020 base.')
f('A02','area',g,'Population, July 1, 2025','9,694,934','E03',period='July 1, 2025 (Vintage 2025)',geo=LA,num=9694934,note='Down 3.2% from the April 1, 2020 base.')
f('A03','area',g,'State projection, July 1, 2026','9,811,358','E06',period='2026',geo=LA,num=9811358,note='A different series from the Census estimate; the two are not interchangeable (they differ by 158,501 for July 1, 2025).')
f('A04','area',g,'State projection, 2030','9,727,305','E06',period='2030',geo=LA,num=9727305)
f('A05','area',g,'State projection, 2035','9,708,647','E06',period='2035',geo=LA,num=9708647)
f('A06','area',g,'State projection, 2040','9,637,524','E06',period='2040',geo=LA,num=9637524)
f('A07','area',g,'State projection, 2050','9,390,823','E06',period='2050',geo=LA,num=9390823)
f('A08','area',g,'Regional plan forecast, 2030','10,214,000','E45',period='2030',geo=LA,num=10214000,note='Points the other way. A 2024 plan with a 2019 base year; the state series is two years newer.')
f('A09','area',g,'Regional plan forecast, 2050','10,793,000','E45',period='2050',geo=LA,num=10793000)
f('A10','area',g,'Change in state projection, 2026 to 2035','-102,711 (-1.0%)',['E06'],period='2026 to 2035',geo=LA,kind='derived',num=-102711,note='9,708,647 minus 9,811,358.')
g='Households, age and origin'
f('A11','area',g,'Households','1,439,097','E03',period='2020-2024',geo=CITY,num=1439097,note='2.61 persons per household.')
f('A12','area',g,'Households, state projection 2026','3,551,868','E41',period='January 1, 2026',geo=LA,num=3551868,note='Vintage 2025 release.')
f('A13','area',g,'Households, state projection 2035','3,711,086','E41',period='January 1, 2035',geo=LA,num=3711086,note='Households rise while population falls: smaller households.')
f('A14','area',g,'Persons under 18','19.2%','E03',period='July 1, 2025',geo=CITY,num=19.2,unit='%')
f('A15','area',g,'Persons 65 and over','14.2%','E03',period='July 1, 2025',geo=CITY,num=14.2,unit='%',note='County: 17.1%.')
f('A16','area',g,'Foreign-born persons','35.7%','E03',period='2020-2024',geo=CITY,num=35.7,unit='%')
g='Income and housing'
f('A20','area',g,'Median household income','$81,939','E03',period='2020-2024 (2024 dollars)',geo=CITY,num=81939,unit='USD',note='County: $90,112.')
f('A21','area',g,'Per capita income','$47,685','E03',period='2020-2024 (2024 dollars)',geo=CITY,num=47685,unit='USD')
f('A22','area',g,'Persons in poverty','16.5%','E03',period='QuickFacts current',geo=CITY,num=16.5,unit='%',note='County: 13.3%.')
f('A23','area',g,'Median gross rent','$1,933','E03',period='2020-2024',geo=CITY,num=1933,unit='USD per month')
f('A24','area',g,'Median value of owner-occupied homes','$921,200','E03',period='2020-2024',geo=CITY,num=921200,unit='USD')
f('A25','area',g,'Owner-occupied housing unit rate','36.0%','E03',period='2020-2024',geo=CITY,num=36.0,unit='%',note='Nearly two in three households rent.')
f('A26','area',g,'Building permits','22,250','E03',period='2025',geo=LA,num=22250)
f('A27','area',g,'Accommodation and food services sales','$17,366,966 thousand','E03',period='2022',geo=CITY,num=17366966,unit='USD thousand')
f('A28','area',g,'Trade-area figures (the blocks around the site)','','E03',geo='Subject trade area',kind='blank',note='City and county figures are the smallest geography read. The Census data service returned "Missing Key" to this session, so no tract or neighbourhood figure is shown.')
g='Schools'
f('A30','area',g,'Los Angeles Unified enrollment','497,105','E31',period='School year 2025-26',geo='Los Angeles Unified',num=497105,note='English learners: 81,328 (16.4%).')
f('A31','area',g,'Graduation rate (four- and five-year combined)','86.5%','E32',period='2025 Dashboard',geo='Los Angeles Unified',num=86.5,unit='%',note='Four-year 84.6%, fifth-year 1.8%. 86.7% on the 2024 Dashboard.')
f('A32','area',g,'Chronic absenteeism, kindergarten to grade 8','21.9%','E32',period='2025 Dashboard',geo='Los Angeles Unified',num=21.9,unit='%',note='18.2% in 2019; 39.8% in 2022; 23.3% in 2024.')
f('A33','area',g,'Projected change in county public school enrollment over ten years','-240,800 students','E33',period='2025-26 to 2035-36',geo=LA,num=-240800,note='"The biggest decline in enrollment is expected in Los Angeles County".')
f('A34','area',g,'State public school enrollment','5,731,300','E33',period='School year 2025-26',geo='California',num=5731300,note='Ninth consecutive yearly decrease.')
f('A35','area',g,'English and mathematics test results','','E32',period='2025 Dashboard',geo='Los Angeles Unified',kind='blank',note='The academic-performance page returned no figures to this session on the read date. Earlier workbooks print -17.8 and -48.9 points from standard; not re-read, so not repeated here.')
f('A36','area',g,'Schools serving the subject address','','E31',geo='Subject property',kind='blank',note='Needs the address, which this workbook does not hold.')
# ---------------- ECONOMY ----------------
g='Jobs'
f('J01','economy',g,'Unemployment rate, not seasonally adjusted','4.5%','E04',period='September 2026',geo=LA,num=4.5,unit='%',note='5.9% a year earlier. Seasonally adjusted: 4.8%.')
f('J02','economy',g,'Nonfarm jobs','4,593,800','E04',period='September 2026 (preliminary)',geo=LA,num=4593800,note='Up 20,300 (0.4%) in a year. Table value; the release narrative misprints it.')
f('J03','economy',g,'Labor force','5,031,000','E04',period='September 2026 (preliminary)',geo=LA,num=5031000,note='Down 1.8% in a year. Part of the fall in unemployment is people leaving the labor force.')
f('J04','economy',g,'Nonfarm jobs, metro area','6,282,100','E01',period='September 2026',geo=MSA,num=6282100,note='Up 30,200 (0.5%). Not seasonally adjusted. Includes Orange County.')
f('J05','economy',g,'Education and health services jobs','+49,100 (+3.8%)','E01',period='Year to September 2026',geo=MSA,num=3.8,unit='%',note='The source of nearly all net job growth.')
f('J06','economy',g,'Information jobs','-11,400 (-5.7%)','E01',period='Year to September 2026',geo=MSA,num=-5.7,unit='%',note='County motion picture and sound recording: -7.3% (EDD).')
f('J07','economy',g,'Leisure and hospitality jobs','+11,500 (+1.5%)','E01',period='Year to September 2026',geo=MSA,num=1.5,unit='%')
f('J08','economy',g,'Manufacturing jobs','-5,400 (-1.2%)','E01',period='Year to September 2026',geo=MSA,num=-1.2,unit='%')
f('J09','economy',g,'Government jobs','-8,400 (-1.1%)','E01',period='Year to September 2026',geo=MSA,num=-1.1,unit='%')
g='Wages and prices'
f('J10','economy',g,'Consumer prices, all items','+3.7%','E01',period='Year to September 2026',geo='Los Angeles area',num=3.7,unit='%',note='Food +2.8%; energy +20.3%.')
f('J11','economy',g,'Average weekly wage','$1,704','E01',period='First quarter 2026',geo=LA,num=1704,unit='USD')
f('J12','economy',g,'Employment cost index, wages and salaries','+3.9%','E01',period='Year to September 2026',geo='Los Angeles-Long Beach area',num=3.9,unit='%',note='United States: +3.1%.')
f('J13','economy',g,'State minimum wage','$16.90 per hour','E14',period='From January 1, 2026',geo='California',num=16.90,unit='USD per hour')
f('J14','economy',g,'Fast-food minimum wage','$20.00 per hour','E17',period='Since April 1, 2024',geo='California, chains of 60 or more',num=20.00,unit='USD per hour',note='Applies to franchisees as well. A council can raise it; no increase is shown on the page.')
f('J15','economy',g,'City minimum wage','$18.42 per hour','E18',period='From July 1, 2026',geo=CITY,num=18.42,unit='USD per hour',note='Reset each July 1 from the area consumer price index.')
g='Output, trade and visitors'
f('J20','economy',g,'Personal income','$818.5 billion','E05',period='2024',geo=LA,num=818.5,unit='USD billion',note='The largest of any United States county.')
f('J21','economy',g,'County gross domestic product','','E05',period='2024',geo=LA,kind='blank',note='Not printed in the release text; the table was not read.')
f('J22','economy',g,'Port container volume','1,042,652 TEUs','E37',period='September 2026',geo='Port of Los Angeles',num=1042652,note='The busiest month in the port\'s history. Loaded imports 545,696, up 19%.')
f('J23','economy',g,'Visitors','49.5 million','E38',period='2025',geo='Los Angeles',num=49.5,unit='million',note='$42.6 billion of business sales. The release itself mentions "headwinds impacting tourism nationally".')
g='Public finances and infrastructure'
f('J30','economy',g,'City reserve fund','$515.1 million (6.00% of General Fund revenues)','E40',period='Fiscal 2026-27 revised budget',geo=CITY,num=515.1,unit='USD million',note='The release still cites "real fiscal uncertainty, rising costs, and major threats to future City revenues".')
f('J31','economy',g,'Subway extension, first section','Opened May 8, 2026','E39',period='2026',geo='Wilshire corridor',note='Stations at Wilshire/La Brea, Wilshire/Fairfax and Wilshire/La Cienega. Two further sections under construction.')
f('J32','economy',g,'Neighbourhood crime rate','','E48',geo='Subject trade area',kind='blank',note='The legacy city dataset is frozen and its replacement was not read. No rate is shown.')
g='November 3, 2026 election (unofficial returns)'
f('J40','economy',g,'Proposition 43: two-thirds vote for voter-proposed local special taxes','Failing: 43.0% yes, 57.0% no','E34',period='As of November 9, 2026, 4:29 p.m.',geo='California',num=43.0,unit='% yes',note='If it fails, local special taxes proposed by voters, the route used for the city transfer-tax surcharge, can still pass by simple majority.')
f('J41','economy',g,'Proposition 3: high-income tax rates made permanent','Passing: 60.4% yes, 39.6% no','E34',period='As of November 9, 2026, 4:29 p.m.',geo='California',num=60.4,unit='% yes',note='Rates on income above about $371,000 would no longer expire in 2031.')
f('J42','economy',g,'Proposition 1: housing affordability bonds','Passing: 60.9% yes','E34',period='As of November 9, 2026, 4:29 p.m.',geo='California',num=60.9,unit='% yes')
f('J43','economy',g,'Proposition 45: modified environmental review for certain projects','Failing: 44.0% yes','E34',period='As of November 9, 2026, 4:29 p.m.',geo='California',num=44.0,unit='% yes')
# ---------------- MARKET ----------------
g='Interest rates'
f('M01','market',g,'10-year Treasury yield','4.88%','E02',period='November 9, 2026',geo='United States',num=4.88,unit='%',note='4.86% on November 6; 4.95% on November 3.')
f('M02','market',g,'30-year Treasury yield','5.26%','E02',period='November 9, 2026',geo='United States',num=5.26,unit='%')
f('M03','market',g,'2-year Treasury yield','4.56%','E02',period='November 9, 2026',geo='United States',num=4.56,unit='%')
f('M04','market',g,'1-year Treasury yield','4.38%','E02',period='November 9, 2026',geo='United States',num=4.38,unit='%')
f('M05','market',g,'Federal funds target range','3.75% to 4.00%','E15',period='October 28, 2026',geo='United States',num=4.0,unit='%',note='Held by 10 votes to 2. Both dissenters wanted an increase. "Inflation remains elevated."')
g='What large buyers paid for net-lease property'
f('M10','market',g,'NNN REIT: cap rate on acquisitions','7.3%','E28',period='Third quarter 2026',geo='United States, retail net lease',num=7.3,unit='%',note='$221.7 million; weighted average lease term 19.6 years.')
f('M11','market',g,'NNN REIT: cap rate on occupied properties it sold','7.8%',['E28','E27','E47'],period='Third quarter 2026',geo='United States, retail net lease',num=7.8,unit='%',note='21 properties, $37.3 million. Second quarter 2026: 5.6% on 7 properties. Full year 2025: 6.4%. Small samples swing widely.')
f('M12','market',g,'NNN REIT: cap rate on occupied properties sold, nine months','7.3%','E28',period='Nine months to September 30, 2026',geo='United States, retail net lease',num=7.3,unit='%',note='37 properties, $64.1 million.')
f('M13','market',g,'Realty Income: initial cash yield on property acquisitions','6.6%','E26',period='Third quarter 2026',geo='United States and Europe',num=6.6,unit='%',note='31.0% retail, 57.3% industrial, 11.7% data centers. Total investments including loans: 6.8%.')
f('M14','market',g,'Four Corners: initial cash yield on acquisitions','6.6%','E29',period='Third quarter 2026',geo='United States',num=6.6,unit='%',note='About 87% medical retail and 5% restaurants. "we have started to see new acquisitions being priced at higher cap rates."')
f('M15','market',g,'Four Corners: preference for buying its own shares','"we view share repurchases as delivering more value than property purchases"','E29',period='October 28, 2026',geo='United States',note='A specialist restaurant-property buyer stepping back from buying.')
f('M16','market',g,'Cap rate for this property','','E28',geo='Subject property',kind='blank',note='No official source prices a single restaurant site. Needs a broker opinion or an appraisal.')
g='What happens when net leases expire'
f('M20','market',g,'Expiring leases renewed by the same tenant','818 of 1,074 (76.2%)','E26',period='Nine months to September 30, 2026',geo='Realty Income portfolio',kind='derived',num=76.2,unit='%',note='A diversified portfolio, not Jack in the Box. Expirations include leases rejected in bankruptcy.')
f('M21','market',g,'Expiring leases re-let to a new tenant','66 of 1,074 (6.1%)','E26',period='Nine months to September 30, 2026',geo='Realty Income portfolio',kind='derived',num=6.1,unit='%')
f('M22','market',g,'Properties sold vacant','181 against 1,074 expirations (16.9%)','E26',period='Nine months to September 30, 2026',geo='Realty Income portfolio',kind='derived',num=16.9,unit='%')
f('M23','market',g,'Rent on re-leased space against the old rent','103.1%','E26',period='Nine months to September 30, 2026',geo='Realty Income portfolio',num=103.1,unit='%',note='$251.1 million new against $243.5 million previous.')
g='Tax on a sale'
f('M30','market',g,'City transfer tax, base','0.45% ($2.25 per $500)','E13',period='Current',geo=CITY,num=0.45,unit='%')
f('M31','market',g,'County transfer tax','0.11% ($0.55 per $500)','E25',period='Current',geo=LA,num=0.11,unit='%')
f('M32','market',g,'City surcharge, lower band','4.0% of the whole price above $5,400,000 and below $10,900,000','E13',period='Closings after June 30, 2026',geo=CITY,num=4.0,unit='%',note='On the whole price, not only the excess.')
f('M33','market',g,'City surcharge, upper band','5.5% of the whole price at $10,900,000 or more','E13',period='Closings after June 30, 2026',geo=CITY,num=5.5,unit='%')
f('M34','market',g,'Federal long-term capital gains rate, top','20%','E22',period='Taxable year 2025',geo='United States',num=20,unit='%')
f('M35','market',g,'Federal rate on gain from past depreciation','Up to 25%','E22',period='Taxable year 2025',geo='United States',num=25,unit='%',note='"unrecaptured section 1250 gain".')
f('M36','market',g,'Net investment income tax','3.8%','E23',period='Current',geo='United States',num=3.8,unit='%',note='Above $200,000 single or $250,000 joint; covers rents and gains on real estate.')
f('M37','market',g,'California top rate on the schedule','12.3%','E49',period='Taxable year 2025',geo='California',num=12.3,unit='%',note='Over $742,953 single or $1,485,906 joint. A further 1% surcharge above $1 million was not read and is not included.')
f('M38','market',g,'California treatment of capital gains','Taxed as ordinary income','E50',period='Current',geo='California',note='"California does not have a lower rate for capital gains."')
f('M39','market',g,'Highest combined rate on a long-term gain, from the four rows above','36.1%',['E22','E23','E49'],period='Taxable year 2025',geo='Federal plus California',kind='derived',num=36.1,unit='%',note='20% + 3.8% + 12.3%. 41.1% on the part taxed at 25%. A ceiling, not the owner\'s rate.')
g='Deferring the tax'
f('M40','market',g,'Like-kind exchange: time to identify a replacement','45 days','E36',period='2025 instructions',geo='United States',num=45,unit='days')
f('M41','market',g,'Like-kind exchange: time to receive the replacement','180 days, or the tax return due date if earlier','E36',period='2025 instructions',geo='United States',num=180,unit='days')
f('M42','market',g,'What does not qualify as replacement','Stock, bonds, notes, partnership interests, certificates of trust','E36',period='2025 instructions',geo='United States',note='Ordinary shares of a property company are not real property for this purpose.')
f('M43','market',g,'Exchange into property outside California','Annual California filing until the deferred gain is recognised','E43',period='2025 instructions',geo='California',note='Form FTB 3840. California keeps its claim on the gain.')
g='Property tax'
f('M50','market',g,'General property tax limit','1% of full cash value','E20',period='Current',geo='California',num=1,unit='%',note='Voter-approved debt is added on top.')
f('M51','market',g,'Yearly limit on assessed-value growth','2%','E20',period='Current',geo='California',num=2,unit='%',note='"not to exceed 2 percent for any given year".')
f('M52','market',g,'Reassessment','On purchase, new construction or change in ownership','E20',period='Current',geo='California',note='A buyer pays tax on the sale price; a long-time owner pays on a much older value.')
# ---------------- HAZARDS ----------------
g='Earthquake'
f('H01','hazard',g,'Chance of a magnitude 6.7 earthquake in the region within 30 years','60%','E16',period='UCERF3',geo='Los Angeles region',num=60,unit='%')
f('H02','hazard',g,'Chance of a magnitude 7 earthquake within 30 years','46%','E16',period='UCERF3',geo='Los Angeles region',num=46,unit='%')
f('H03','hazard',g,'Chance of a magnitude 7.5 earthquake within 30 years','31%','E16',period='UCERF3',geo='Los Angeles region',num=31,unit='%')
g='Wildfire'
f('H10','hazard',g,'Structures destroyed, Eaton and Palisades fires','16,251','E30',period='January 2025',geo=LA,kind='derived',num=16251,note='9,414 plus 6,837.')
f('H11','hazard',g,'Economic output lost','$5.2 billion to $10.1 billion','E30',period='2025',geo=LA,note='About 6,800 businesses and 47,000 workers affected.')
f('H12','hazard',g,'Insurer-of-last-resort assessment','$1 billion','E44',period='February 2025',geo='California',num=1.0,unit='USD billion',note='The first in over 30 years. Insurers may recover half from their policyholders.')
g='Flood'
f('H20','hazard',g,'Statewide winter-storm scenario, total cost','About $725 billion','E42',period='2011 scenario',geo='California',num=725,unit='USD billion',note='A hypothetical. "Serious flooding also occurs in ... Los Angeles County".')
g='Parcel level'
f('H30','hazard',g,'Hazard zones for the subject parcel','',['L03','L04','L05'],geo='Subject property',kind='blank',note='Flood, fault, liquefaction and fire zone all need the address.')
json.dump({'meta':{'session':'session-a5f8f119','as_of':'2026-11-10','kinds':{'verified':'Read by this session from the linked official page on the as-of date.','derived':'Arithmetic on verified values; the inputs are linked.','brief':'Stated in the owner brief; not confirmed in any public record.','blank':'Could not be confirmed. Left empty and listed on Flagged for Review.'}},'rows':F},open(OUT+'/facts.json','w'),indent=1,ensure_ascii=False)
from collections import Counter
print(len(F),Counter(x['kind'] for x in F),Counter(x['page'] for x in F))
