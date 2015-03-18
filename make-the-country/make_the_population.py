'''
module1.py

Project: United States Trip File Generation
Author: A.P. Hill Wyrough
version date: 3/15/2014
Python 3.3

Purpose: Create residents within households for block in every sate within the United States. 
Gives each resident unique geographical identifiers, numeric ID's, latitude/longitude of home, 
sex, age, household identifier, household type, traveler type, and income bracket and amount.
Creates a master resident file for state input. 

Relies on significant data sets from U.S. Census - demographic, group quarters, households. 
See accompanying documentation (i.e. Thesis 2014)

Dependencies: None

Notes: This code is adapted from Talal Mufti and Jake Gao. Mufti wrote the initial New Jersey specific synthesizer for his
Masters Thesis in 2012 for the state of NJ. Aside from adapting the code for a more general input (any state),
more data, and 51 states instead of several hard coded counties, the bulk of the original changes
include:

- Selection with replacement
- Creation of Households (see: householdhelper and build_households)
- Data input and output
          '''
###################################################################################################
# IMPORTS
###################################################################################################       
import csv
import random as rd
import numpy as np
from numpy import * 
from datetime import datetime
from itertools import chain
###################################################################################################
# STATIC DATA DEFINITIONS
################################################################################################### 

'MAIN PATH ON MY COMPUTER TOWARDS FILES OF USE'
M_PATH = "C:\\Users\\Hill\\Desktop\\Thesis\\Data"
'DEFINE AGE RANGES FROM CENSUS'
ageRanges = [(0,4) , (5,9) , (10,14) , (15,17), (18,19), (20,20), (21,21), (22,24), (25,29), (30,34),\
            (35,39), (40,44), (45,49), (50,54), (55,59), (60,61), (62,64), (65,66), (67,69) , (70, 74), (75,79), (80,84), (85,100) ]
'DEFINE INCOME BRACKET RANGES'
INCOME_BRACKETS = {     1: (0, 9999),
                        2: (10000,14999),
                        3: (15000,24999),
                        4: (25000,34999),
                        5: (35000,49999),
                        6: (50000,74999),
                        7: (75000,99999),
                        8: (100000,149999),
                        9: (150000,199999),
                        10:(200000,1000000)}

'INDICES IN DATA FILE'
'IMPORTANT: REMEMBER range(2,5) = 2, 3, 4 - DOES NOT INCLUDE LAST INDEX'

'ALL MEN AT EACH AGE GROUP (DEMOGRAPHIC QUERY FILE'
M_AGE_DIST = range(10, 33)
'ALL WOMEN AT EACH AGE GROUP (DEMOGRAPHIC QUERY FILE'
F_AGE_DIST = range(34, 57)
'MEN:WOMEN RATIO (TOTAL MEN, TOTAL WOMEN'
SEX_DIST = [9,33]
'UNDER/OVER 18 YEARS OLD (FAMILY QUERY FILE)'
UNDER_OVER_EIGHTEEN = range(31, 33)
'GROUP QUARTERS BY AGE BY TYPE (GROUP QUARTERS FILE)'
GROUP_QUARTERS = range(6, 48)
'HOUSEHOLD SIZE DISTRIBUTION'
HH_DIST = range(58,65)
'HOUSEHOLD RELATIONSHIP DISTRIBUTION'
HH_REL_DIST = range(6,31)
'NON-FAMILY TO FAMILY RATIO (FAM_NOFAM[0] = # of NONFAM, FAM_NOFAM[1] = # of FAM)'
FAM_NOFAM = [17,2]


'GLOBAL DEFINITIONS OF COUNTERS AND ARRAYS'
# ALL MALE CHILDREN
mchildren = []
# ALL FEMALE CHILDREN
fchildren = []
# ALL MALE ADULTS
madults = []
# ALL FEMALE ADULTS
fadults = []
# POPULATION COUNT IN STATE DURING SIMULATION
pop = 0
# DUMMY POPULATION COUNT
poptwo = 0
# GROUP QUARTER POP COUNT
gpop = 0
hpop = 0
spop = 0
femaleadultcount = 0
maleadultcount = 0
femalechildrencount = 0
malechildrencount = 0



###################################################################################################
# FUNCTION DEFINITIONS
################################################################################################### 

###################################################################################################
'DATA INPUT HELPER FUNCTIONS'
################################################################################################### 

'RECONCILES READING INPUTS AS BYTES OR AS UNICODE CHARACTERS'
def remove_b(teststring):
    if teststring[0] == 'b':
        newstr = teststring[1:100]
    else:
        newstr = teststring
    return newstr
'EXTRACTS THE CENSUS TRACT NUMBER FROM GEOID_2 INCLUDED IN CENSUS INCOME DATA'
def convert_tract(tract):
    sample = tract[5:11]
    sample2 = tract[4:11]
    if len(sample) == 6:
        return sample
    else:
        return sample2
'CONVERTS A TRACT NUMBER AS AN INTEGER TO A STRING FOR THE BASIS OF COMPARISON'
def tract_to_string(tract):
    return str(tract)
'RETURNS THE COLUMN INDICES USED IN THE GROUP QUERY RAW TEXT FILE'
def group_ranges():
    seq = chain(range(6),range(10,14),range(15,18),range(20,24),range(25,28),range(30,34),range(35,38),range(41,45),range(46,49),range(51,55),range(56,59),range(61,65),range(66,69))
    return seq
'RETURNS THE COLUMN INDICES USED IN THE DEMO QUERY RAW TEXT FILE'
def demo_ranges():
    seq = chain(range(8), range(12, 69))
    return seq

###################################################################################################
'DATA INPUT AND READING FROM DATA FILES'
################################################################################################### 

'READ CENSUS MATRIX FOR A SPECIFIC STATE AND RETURN MATRIX/ARRAY OF ALL DATA (BLOCKS), ALONG WITH FULL TRACT EXPRESSION'
def read_census_matrix(state):
    censusFileLocation = M_PATH + '\\DemographicQueries\\'
    fname = censusFileLocation + state + 'Query.txt'
    tra = np.loadtxt(fname, delimiter=",", skiprows = 1, dtype = str, usecols=[3], converters = {3:remove_b})
    uni = np.loadtxt(fname, delimiter=",", skiprows = 1, dtype = str, usecols=[2], converters = {2:remove_b})
    mydata = np.recfromcsv(fname, delimiter=',', usecols = demo_ranges(), filling_values=np.nan, case_sensitive=True, deletechars='', replace_space=' ')
    return mydata, tra, uni
'READ GROUP QUARTERS MATRIX FOR A SPECIFIC STATE AND RETURN MATRIX/ARRAY OF ALL DATA (BLOCKS)'
def read_group_matrix(state):
    groupQuartersFileLocation = M_PATH + '\\GroupQuarterQueries\\'
    fname = groupQuartersFileLocation + state + 'GQuery.txt'
    mydata = np.recfromcsv(fname, delimiter=',', usecols = group_ranges(), filling_values=np.nan, case_sensitive=True, deletechars='', replace_space=' ')
    return mydata
'READ FAMILY RELATIVE DISTRIBUTION FOR A SPECIFIC STATE AND RETURN MATRIX OF ALL DATA (BLOCKS)'
def read_family_matrix(state):
    familyFileLocation = M_PATH + '\\FamilyQueries\\'
    fname = familyFileLocation + state + 'FQuery.txt'
    mydata = np.recfromcsv(fname, delimiter=',', filling_values=np.nan, case_sensitive=True, deletechars='', replace_space=' ')
    unidata = np.loadtxt(fname, delimiter=",", usecols=range(2,6), dtype=str, skiprows=1)
    return mydata, unidata
'READ INCOME MATRIX FOR A SPECIFIC STATE AND RETURN MATRIX ARRAY OF ALL DATA (TRACTS) AND RETURN CENSUS TRACT LOOK UP TABLE \
ALONG WITH FAMILY INCOME AND NON FAMILY INCOME ESTIMATES FOR EACH BRACKET IN ASCENDING ORDER'
def read_income_matrix(state):
    incomeFileLocation = M_PATH + '\\IncomeQueries\\'
    fname = incomeFileLocation + state + 'Income.csv'
    tra = np.loadtxt(fname, delimiter=",", dtype = str, skiprows=1, usecols=[1], converters = {1:convert_tract})
    faminco = genfromtxt(fname, delimiter=",", dtype = double, usecols=range(15,88,8), skiprows =1)
    nonfaminco = genfromtxt(fname, delimiter=",", dtype = double, usecols=range(19, 19 + (88 - 15), 8), skiprows = 1)
    whereAreNaNs = isnan(faminco)
    faminco[whereAreNaNs] = 0
    whereAreNaNs = isnan(nonfaminco)
    nonfaminco[whereAreNaNs] = 0
    return faminco, nonfaminco, tra
'READ IN LATITUDES AND LONGITUDES OF EVERY BLOCK IN STATE AND RETURN ARRAY (BLOCKS)'
def read_lat_lons(state):
    censusFileLocation = M_PATH + '\\DemographicQueries\\'
    fname = censusFileLocation + state + 'Query.txt'
    mydata = np.recfromcsv(fname, delimiter=",", filling_values=np.nan, case_sensitive=True, usecols = (8,9), deletechars='', replace_space=' ')
    return mydata

###################################################################################################
'ASSIGNING AGE AND GENDER TO POPULATION'
################################################################################################### 

'ACCEPT AGE RANGE INDEX (0, 1, 2, ... 23) AND IT RETURNS A RANDOM INTEGER BETWEEN THE ENDPOINTS OF \
THAT AGE RANGE. EX: get_age(1) will return a random integer between 5 and 9, inclusive'
def get_age(g = -1):
    return rd.randint(ageRanges[g][0], ageRanges[g][1]) if g != -1 else -1
'ACCEPT ARRAY OF ALL MALE RESIDENTS BY AGE AND ALL FEMALE RESIDENTS BY AGE AND BEGINS TO POPULATE \
4 GLOBAL LIST OF MALE AND FEMALE AND ADULT AND CHILDREN RESIDENTS OF STATE \
each resident is populated with an age and a sex (1 for male, 0 for female)'
def createResidents(maleAgeGroup, femaleAgeGroup):
    global mchildren, madults, fchildren, fadults, poptwo
    # ITERATE OVER EACH AGE GROUP FOR MEN IN THAT BLOCK
    for i, agepop in enumerate(maleAgeGroup):
        poptwo += agepop
        for j in range(agepop):
            x = get_age(i)
            if x <= 17:
                mchildren.append([x, 1, -1])
            else:
                madults.append([x, 1, -1])
    # ITERATE OVER EACH AGE GROUP FOR WOMEN IN THAT BLOCK
    for i, agepop in enumerate(femaleAgeGroup):
        poptwo += agepop
        for j in range(agepop):
            x = get_age(i)
            if x <= 17:
                fchildren.append([x, 0, -1])
            else:
                fadults.append([x, 0, -1]) 
                
###################################################################################################
'ACCOUNT FOR GROUP QUARTERS POPULATION'
###################################################################################################  
'Using the total population of male and female adults/children, move some into group quarters to account \
for the population in each block living in group quarters. This requires separate data that has the pop \
of each quarter type in each block by age and by gender. It uses the listed indexes for quarter type'
## HOUSEHOLD TYPES
## 0: Family ## 1: Non-family ## 2: Correctional Facilities ## 3: Juvenile Detentions ## 4: Nursing homes
## 5: Other institutionalized quarters ## 6: Student housing ## 7: Military ## 8: Other non institutionalized quarters
'Pass it row of Group Quarter data'
def get_group_quarters(r):
    global mchildren, madults, fchildren, fadults, gpop
    cfa = []; j = []; nh = []; oiq = []; sh = []; m = []; oniq = []
    l = [cfa, j, nh, oiq, sh, m, oniq]
    gqlist = [r[x] for x in GROUP_QUARTERS]
    for i, gqsize in enumerate(gqlist):
        mod = i%7
        if i in range(0,7):
            popList = mchildren
            popRange = (14, 17)
        elif i in range(7,14):
            popList = madults
            popRange = (18, 64)
        elif i in range(14,21):
            popList = madults
            popRange = (65,120)
        elif i in range(21, 28):
            popList = fchildren
            popRange =(14, 17)
        elif i in range(28,35):
            popList = fadults
            popRange = (18, 64)
        elif i in range(34,42):
            popList = fadults
            popRange = (65,120)
        'Add them to the right group housing list if they are in the right age'             
        for j in range(gqsize):
            pll = len(popList)
            if pll>0:
                for c in range(pll):
                    z = np.random.randint(0, len(popList))
                    popped = popList.pop(z)
                    
                    if popped[0]>=popRange[0] and popped[0]<=popRange[1]:
                        break
                    else:
                        popList.insert(0, popped)
                        popped = -1
                if popped == -1:
                    break
                else:
                    gpop+=1
                    popped[2] = mod+2
                    l[mod].append(popped)
    return l

###################################################################################################
'HOUSEHOLD, INCOME ASSIGNMENT HELPER FUNCTIONS'
###################################################################################################  
'returns list that repeats each element index of dist "freq" times where "freq" is the value of that element'
def expand_distribution(dist):
    vec = [[i]*int(round(x)) for i, x in enumerate(dist)]
    return [num for elem in vec for num in elem]
'way to randomly select a single item from list after expanding it. especially convenient for binary dist (True/False, fam/non-fam, under/over 18)'
''' note that when an index has freq zero, it is not represented at all, which causes a problem whern there are only two indeces, one with freq 0'''
'Selection from Distribution: WITH REPLACEMENT'
def select_one(l):
    r = np.random.randint(0,len(l)) if len(l)>1 else 0
    if not l:
        return 0, l
    else:
        val = l.pop(r)
        return val, l 
'Expand Distribution for household size, noting that household size starts at 1, not 0'
def expand_household_size(dist):
    vec = [[i]*int(round(x)) for i, x in enumerate(dist)]
    return [(num+1) for elem in vec for num in elem]
'returns the appropriate income bracket code for a given income'
def income_amount_to_code(income):
    for k in INCOME_BRACKETS.keys():
        if income<=INCOME_BRACKETS[k][1] and income>=INCOME_BRACKETS[k][0] and income != 0:
            return k
        elif income == 0:
            return 0
'Match Census Tract in Demo Data to Census tract in Income Data'
'Deprecated: Unused'
def find_matching_tract(rownum, tra, traIncome, currentTract):
    for i in range(0, len(traIncome)):
        if traIncome[i] == tra[rownum]:
            return i
    return -1
'Created Unique Identifier for Given Family Row'
'Deprecated: Unused'
def create_unique_ID(family_uni_row):
    county = family_uni_row[0]
    county = county[1:10]
    tract = family_uni_row[1]
    tract = tract[1:10]
    blockg = family_uni_row[2]
    blockg = blockg[1:10]
    block = family_uni_row[3]
    block = block[1:10]
    seq = (county, tract, blockg, block)
    return seq
'Match Two Unique Identifiers, Return True or False'
'Deprecated: Unused'
def matching_value(seq1, seq2):
    if (seq1[0] == seq2[0]) and (seq1[1]==seq2[1]) and (seq1[2]==seq2[2]) and (seq1[3]==seq2[3]):
        return True
    else:
        return False
'Find Matching Row within Census Demo Data of Family Data'
'Deprecated: Unused'
def find_matching_row(census_uni_row, familyuni):
    seqCensus = create_unique_ID(census_uni_row)
    for i in range(0, len(familyuni)):
        seqFam = create_unique_ID(familyuni[i])
        if  matching_value(seqCensus, seqFam) == True:
            return i
    return False
###################################################################################################
'HOUSEHOLD, INCOME, TRAVELER TYPE ASSIGNMENT'
################################################################################################### 
'RETURN TRAVELER TYPE GIVEN AGE AND HOUSEHOLD TYPE'
def traveler_type(age, hht):
    ##0:DNT:0-5, 79+ and those in correct. fac, juvee, nursing homes, other, and military quarters
    ##1:SCN:5-18: 6-15, 16-18*99.948% ##2:SCW:16-18*.0512%
    ##3:CNT:18-22*90.34% + in Dorms ##4:CCW:18-22*9.66% (work in same county)
    ##5:TTT:22-64*78% ##6:HWT:22-64*22% + 65-79 #unemployed(~10%) + work-at-home (~8%) +sickdays
    temp = rd.uniform(0,1)
    if age >= 0 and age< 5 or age>79 or hht in [2,3,4,5,7]:
        travelType=0
    elif age>=5 and age<=15:
        travelType=1
    elif age>=16 and age<= 18:
        if temp>=0.99948:
            travelType=2
        else:
            travelType=1
    elif age>=18 and age<=22 or hht == 6:
        if temp<=.9034:
            travelType=3
        else:
            travelType=4
    elif age>=22 and age<=64:
        if temp<=.78:
            travelType=5
        else:
            travelType=6
    else:
        travelType=6
    return travelType

'RETURN INCOME FOR HOUSEHOLD GIVEN FAMILY INCOME,NON FAMILY INCOME, AND HOUSE HOLD TYPE'
def get_hh_income(famIncome, nonFamIncome, hht):
    if hht:
        i = nonFamIncome
    else:
        i = famIncome
    ie = expand_distribution(i)
    val, ie = select_one(ie)
    bracket = val + 1
    if bracket == 1:
        amount = rd.triangular(2000, 10000,7500)
    else:
        amount = rd.uniform(INCOME_BRACKETS[bracket][0], INCOME_BRACKETS[bracket][1])
    return amount

'Given Household Income and household, distribution income over individuals when necessary'
def add_individual_income_tt(hhi, h):
    hhinctt = []
    l = 0
    for i, p in enumerate(h[0]):
        tt = traveler_type(p[0], 0)
        if tt in[5,6]:
            hhinctt.append([tt,-1,0])
            l+=1
        elif tt in [0,1,3]:
            hhinctt.append([tt,0,0])
        elif tt in[2,4]:
            studentInc = rd.uniform(INCOME_BRACKETS[1][0],
                                    min(INCOME_BRACKETS[1][1],hhi))
            hhinctt.append([tt, 1, studentInc])
            hhi-=studentInc
    coeffs = []
    for i in range(l):
        coeffs.append(rd.random())
        s = sum(coeffs)
        indincomes = [hhi*c/s for c in coeffs]
    for q in hhinctt:
        if q[1] == -1:
            inc = indincomes.pop()
            q[1] = income_amount_to_code(inc)
            q[2] = inc
    return hhinctt

'Prepare Distributions for Creation of Households within Block'
def household_helper(censusrow, famrow):
    global pop
    censusPop = censusrow[9] + censusrow[33]
    pop+=censusPop
    global spop
    'READ IN HOUSE SIZES'
    housesizes = expand_household_size([censusrow[x] for x in HH_DIST])
    rel = [famrow[x] for x in HH_REL_DIST]
    'READ IN POPULATION IN HOUSEHOLDS BY TYPE'
    housepop = [rel[2], rel[17]]
    'READ IN DISTRIBUTION OF HOUSEHOLDERS BY TYPE BY SEX'
    famholder = expand_distribution([rel[x] for x in [4,5]])
    nfamholder = expand_distribution([rel[x] for x in [18,21]])
    'READ IN NUMBER OF NON FAMILY HOUSEHOLDERS LIVING ALONE OR TOGETHER'
    nofamalone = [rel[x] for x in [19, 20, 22, 23]]
    'READ IN FAMILY RELATIONS FOR FAMILY HOUSEHOLDS'
    famrel = expand_distribution([rel[x] for x in range(6,17)])
    htype = []
    for i in range(len(famholder)):
        htype.append(0)
    for i in range(len(nfamholder)):
        htype.append(1)
    'ALL HOUSES FOR THAT BLOCK'
    hhh = buildHouses(housesizes,housepop,famholder,nfamholder, htype, nofamalone, famrel)
    return hhh

'Creates All HouseHolds within Block given prepared distributions by Household Helper'
def buildHouses(housesizes, housepop,famholder, nfamholder, htype, nofamalone, famrel):
    numhouses = len(housesizes)
    allHouses = []
    allHouseHolders = []
    'Population Counters'
    inNonFamHousing = 0
    inFamHousing = 0
    'Householder Availability'
    nonfamHouseHoldersAvailable = len(nfamholder)
    famHouseHoldersAvailable = len(famholder)
    
    'Initialize all HouseHolders within Census Block'
    for i in range(numhouses):
        'Select Household Type From Distribution (0: family, 1: nonfamily)'
        hht, htype = select_one(htype)
        if (hht == 0):
            gender, famholder = select_one(famholder)
            inFamHousing+=1
        else:
            gender, nfamholder = select_one(nfamholder)
            inNonFamHousing+=1
        'Create Householder with Dummy Age of 30, Gender, HHT, and -1 (flag indicating assignment to house)'
        householder = [30, int(not gender), hht, -1]
        if (int(not gender) == 1) and (len(madults) > 0):
            if (len(madults) > 0):
                temp = madults.pop()
        elif (int(not gender) == 0) and (len(fadults) > 0):
            if (len(fadults) > 0):
                temp = fadults.pop()
        elif (len(fadults) == 0 and len(madults) == 0):
            'In the event of non-normally aged householders (what we have classified as children, draw from the oldest'
            'Children of the correct gender'
            if (int(not gender) == 1):
                if (len(mchildren) > 0):
                    temp = mchildren.pop(mchildren.index(max(mchildren)))
            else:
                if (len(fchildren) > 0):
                    temp = fchildren.pop(fchildren.index(max(fchildren)))
        elif (int(not gender) == 1) and (len(madults) == 0) and (len(mchildren) > 0):
            if (len(mchildren) > 0):
                temp = mchildren.pop(mchildren.index(max(mchildren)))
        elif (int(not gender) == 0) and (len(fadults) == 0) and (len(fchildren) > 0):
            if (len(fchildren) > 0):
                temp = fchildren.pop(fchildren.index(max(fchildren)))
        householder[0] = temp[0]
        allHouseHolders.append(householder)
    
    'Assign HouseHolder to House (by House size) for Non Family'
    for hh in enumerate(allHouseHolders):
        hh = hh[1]
        'Male, Non Family HouseHold'
        if (hh[2] == 1) and (hh[1] == 1):
            if (nofamalone[0] != 0):
                housesizes.remove(1)
                allHouses.append([0, hh[2], [hh]])
                hh[3] = 0
                nofamalone[0]-=1
                nonfamHouseHoldersAvailable-=1
                continue
        'Female, Non Family Household'
        if (hh[2] == 1) and (hh[1] == 0):
            if (nofamalone[2] != 0):
                housesizes.remove(1)
                allHouses.append([0, hh[2], [hh]])
                hh[3] = 0
                nofamalone[2]-=1
                nonfamHouseHoldersAvailable-=1
                continue
    
    housesizes.sort()
    housesizes = housesizes[::-1]
    
    'Populate Non Family Houses with Non Family Householders and Create Household Object'
    while((inNonFamHousing < housepop[1]) and (nonfamHouseHoldersAvailable > 0)):
        for hh in enumerate(allHouseHolders):
            hh = hh[1]
            if (nonfamHouseHoldersAvailable > 0):
                if ((hh[2] == 1) and (hh[3] == -1)):
                    if len(housesizes) > 0 :
                        size = housesizes.pop()
                    else:
                        break
                    hh[3] = 0
                    allHouses.append([size-1, hh[2], [hh]])
                    nonfamHouseHoldersAvailable-=1
                    inNonFamHousing+=(size-1)
                    continue
    'Populate Family Households for Family Householders and Create Household Object'
    while((inFamHousing < housepop[0]) and (famHouseHoldersAvailable>0)):
        for hh in enumerate(allHouseHolders):
            hh = hh[1]
            if (famHouseHoldersAvailable > 0):
                if ((hh[2] == 0) and (hh[3] == -1)):
                    if len(housesizes) > 0 :
                        size = housesizes.pop()
                    else:
                        break
                    hh[3] = 0
                    allHouses.append([size-1, hh[2], [hh]])
                    famHouseHoldersAvailable-=1
                    inFamHousing+=(size-1)
                    continue
    'Populate Households with All Family Relations, Exhausting Family Relation Distribution'          
    for j, i in enumerate(famrel):
        for k, hh in enumerate(allHouses):
            if (hh[0] == 0): continue
            else:
                if ((i == 0) and (hh[0] > 0) and (hh[1] == 0)):
                    if (hh[2][0][1] == 0) and (len(madults) > 0):
                        hh[0]-=1
                        person = madults.pop()
                        hh[2].append([person[0], 1, hh[1], 0])
                        break
                    elif (hh[2][0][1] == 1) and (len(fadults) > 0):
                        hh[0]-=1
                        person = fadults.pop()
                        hh[2].append([person[0], 0, hh[1], 0])
                        break
                if ((i in [1,2,3,4]) and (hh[0] > 0) and (hh[1] == 0)):
                    if ((len(mchildren) + len(fchildren)) > 1):
                        r = np.random.randint(1, len(mchildren) + len(fchildren))
                        if (r < len(mchildren)):
                            person = mchildren.pop()
                            hh[2].append([person[0], 1, hh[1], 0])
                            hh[0]-=1
                            break
                        else:
                            person = fchildren.pop()
                            hh[2].append([person[0], 0, hh[1], 0])
                            hh[0]-=1
                            break
                    elif (len(mchildren) > 0):
                        person = mchildren.pop()
                        hh[2].append([person[0], 1, hh[1], 0])
                        hh[0]-=1
                        break
                    elif (len(fchildren) > 0):
                        person = fchildren.pop()
                        hh[2].append([person[0], 0, hh[1], 0])
                        hh[0]-=1
                        break
                if ((i in [5,6,7,8,9,10]) and (hh[0] > 0) and (hh[1] == 0)):
                    if ((len(madults) + len(fadults)) > 1):
                        r = np.random.randint(1, len(madults) + len(fadults))
                        if (r < len(madults)):
                            person = madults.pop()
                            hh[2].append([person[0], 1, hh[1], 0])
                            hh[0]-=1
                            break
                        else:
                            person = fadults.pop()
                            hh[2].append([person[0], 0, hh[1], 0])
                            hh[0]-=1
                            break
                    elif (len(madults) > 0):
                        person = madults.pop()
                        hh[2].append([person[0], 1, hh[1], 0])
                        hh[0]-=1
                        break
                    elif (len(fadults) > 0):
                        person = fadults.pop()
                        hh[2].append([person[0], 0, hh[1], 0])
                        hh[0]-=1
                        break
                         
    for i, hh in enumerate(allHouses):
        while (hh[0] > 0): 
            if ((len(madults)+len(fadults)) > 1):   
                r = np.random.randint(1, len(madults) + len(fadults))
                if (r < len(madults)):
                    person = madults.pop()
                    hh[2].append([person[0], 1, hh[1], 0])
                    hh[0]-=1
                    break
                else:
                    person = fadults.pop()
                    hh[2].append([person[0], 0, hh[1], 0])
                    hh[0]-=1
                    break
            elif (len(madults) > 0):
                person = madults.pop()
                hh[2].append([person[0], 1, hh[1], 0])
                hh[0]-=1
                break
            elif (len(fadults) > 0):     
                person = fadults.pop()
                hh[2].append([person[0], 0, hh[1], 0])
                hh[0]-=1
                break   
            elif ((len(mchildren) + len(fchildren)) > 1):
                r = np.random.randint(1, len(mchildren) + len(fchildren))
                if (r < len(mchildren)):
                    person = mchildren.pop()
                    hh[2].append([person[0], 1, hh[1], 0])
                    hh[0]-=1
                    break
                else:
                    person = fchildren.pop()
                    hh[2].append([person[0], 0, hh[1], 0])
                    hh[0]-=1
                    break
            elif (len(mchildren) > 0):
                person = mchildren.pop()
                hh[2].append([person[0], 1, hh[1], 0])
                hh[0]-=1
                break
            elif (len(fchildren) > 0):
                person = fchildren.pop()
                hh[2].append([person[0], 0, hh[1], 0])
                hh[0]-=1
                break
            elif (len(fchildren) == 0) and (len(mchildren)==0) and (len(madults) ==0) and (len(fadults)==0):
                break
    'Fail Safe to Ensure All Population in Households are placed within house, relaxing house size constraint for'
    'Largest House in Block'
    if (len(allHouses) > 0):
        while (len(madults) > 0):
            person = madults.pop()
            allHouses[len(allHouses)-1][2].append([person[0], 1, 0, 0])
            allHouses[len(allHouses)-1][0]-=1
        while (len(fadults) > 0):
            person = fadults.pop()
            allHouses[len(allHouses)-1][2].append([person[0], 0, 0, 0])
            allHouses[len(allHouses)-1][0]-=1
        while (len(fchildren) > 0):
            person = fchildren.pop()
            allHouses[len(allHouses)-1][2].append([person[0], 0, 0, 0])
            allHouses[len(allHouses)-1][0]-=1
        while (len(mchildren) > 0):
            person = mchildren.pop()
            allHouses[len(allHouses)-1][2].append([person[0], 1, 0, 0])
            allHouses[len(allHouses)-1][0]-=1
    del allHouseHolders
    return allHouses

def person_writer(state, pW, l, gql, ll, fi, nfi, county, tract, block):
    global HH_COUNT
    global PERSON_COUNT
    global writeCount
    global HOUSE_COUNT
    for i, h in enumerate(l):
        house = [h[2]]
        if len(house) != 0:
            HH_COUNT += 1
            hhIncome = get_hh_income(fi, nfi, h[1])
            indIncome = add_individual_income_tt(hhIncome, house)
            for j, p in enumerate(house[0]):
                HOUSE_COUNT+=1
                PERSON_COUNT+= 1
                idnum = str(1000000000 + PERSON_COUNT)
                pid = str(state) + idnum[1:]
                writeCount+=1
                pW.writerow([state] + [county] + [tract] + [block] + [HH_COUNT] + [p[2]] + [ll[0]] + [ll[1]] + [pid] 
                            + [p[0]] + [p[1]] 
                            + [indIncome[j][0]] + [indIncome[j][1]] + [indIncome[j][2]])
    for k, quarter in enumerate(gql):
        if len(quarter) != 0:
            HH_COUNT+=1
            for z, q in enumerate(quarter):
                PERSON_COUNT+=1
                idnum = str(1000000000 + PERSON_COUNT)
                pid = str(state) + idnum[1:]
                income = 0
                writeCount+=1
                pW.writerow([state] + [county] + [tract] + [block]+ [HH_COUNT] + [q[2]] + [ll[0]] + [ll[1]] + [pid] 
                            + [q[0]] + [q[1]] 
                            + [traveler_type(q[0], q[2])] + [income] + [income])

###################################################################################################
'READ IN STATIC DATA'
###################################################################################################  
def read_states():
    """ Read in State names, abbreviations, and state codes"""
    censusFileLocation = M_PATH + '\\'
    fname = censusFileLocation + 'ListofStates.txt'
    mydata = np.recfromcsv(fname, delimiter=',', case_sensitive=True, deletechars='', replace_space=' ')
    return mydata
def write_headers(pW):
    """ Write Headers to NN File """
    pW.writerow(['Residence State'] + ['County Code'] + ['Tract Code'] + ['Block Code'] + ['HH ID'] + ['HH TYPE'] + ['Latitude'] + ['Longitude'] 
                + ['Person ID Number'] + ['Age'] + ['Sex'] + ['Traveler Type'] + ['Income Bracket']
                + ['Income Amount'])
###################################################################################################
'EXECUTIVE SCRIPT'
###################################################################################################  
def executive(teststate, teststateabrev):
    runTester = True
    global HH_COUNT
    global HOUSE_COUNT
    global PERSON_COUNT
    global writeCount    
    startTime = datetime.now()
    print(teststateabrev + " started at " + str(datetime.now())
          + " duration: " + str(datetime.now()-startTime))
    
    'READ ALL INPUTS'
    censusdata, tra, uni = read_census_matrix(teststate)
    latlondata = read_lat_lons(teststate)
    groupquarterdata = read_group_matrix(teststate)
    faminco, nonfaminco, traIncome = read_income_matrix(teststate)
    familydata, unidata = read_family_matrix(teststate)
    total = len(censusdata)
    if runTester:    
        statecode = censusdata[0][1]
        path = 'C:/Users/Hill/Desktop/Thesis/Data/Output/Module1/'
        HH_COUNT = 0
        HOUSE_COUNT = 0
        PERSON_COUNT = 0
        writeCount = 0
        f = open(path + str(teststate + 'Module1NN2ndRun.csv'), 'w+', encoding='utf8')
        personWriter = csv.writer(f, delimiter= ',', lineterminator = '\n')
        write_headers(personWriter)
        IncometractRow = 0
        incomeTract = tra[IncometractRow]
        for rownum, row in enumerate(censusdata):
            personWriter = csv.writer(f , delimiter= ',', lineterminator = '\n')
            'GRAB ALL RELEVANT ROWS IN DATA QUERIES'
            quarterrow = groupquarterdata[rownum]
            familyrow = familydata[rownum]
            latlonrow = latlondata[rownum]
            'FIND CENSUS TRACT IN INCOME DATA'
            if incomeTract != tra[rownum]:
                IncometractRow+=1
                incomeTract = traIncome[IncometractRow]
            'GRAB INCOME DATA ROWS'
            family_income = faminco[IncometractRow]
            non_family_income = nonfaminco[IncometractRow]
            countycode = uni[rownum]
            'INITIALIZATION OF POPULACE WITH SEX AND AGE'
            createResidents([row[x] for x in M_AGE_DIST], [row[x] for x in F_AGE_DIST])
            'ACCOUNT FOR RESIDENTS IN GROUP QUARTERS'
            gqlist = get_group_quarters(quarterrow)
            'BUILD HOUSEHOLDS WITHIN BLOCK'             
            hhh = household_helper(row, familyrow)
            'WRITE OUTPUT OF BLOCK SIMULATION'
            person_writer(statecode, personWriter, hhh, gqlist, latlonrow, 
                          family_income, non_family_income, countycode, tra[rownum], censusdata[rownum][5])
            del gqlist, row, quarterrow, familyrow, latlonrow, family_income, non_family_income
            del personWriter
            'PERIODICALLY UPDATE STATUS OF EXECUTION'     
            if (rownum%1000 == 0):
                print(str(100*rownum/total) + '% Done!')
                print(teststate + " took this much time: " + str(datetime.now()-startTime))
                        
        f.close()
        del censusdata, tra, uni, latlondata, groupquarterdata, faminco, nonfaminco, traIncome,familydata,unidata     
        print('Write Count: ' + str(writeCount))        
        print(teststate + " took this much time: " + str(datetime.now()-startTime))

import sys
exec('executive(sys.argv[1], sys.argv[2])')
