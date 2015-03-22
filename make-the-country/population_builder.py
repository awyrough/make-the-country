from itertools import chain
import random as rd
import numpy as np

def treat_income(data):
    """
    Convert to doubles, or zero if NaN
    """
    try:
        return float(data)
    except:
        return 0.0

def treat_demo(data):
    """
    Convert to *** 
    """
    return data

def treat_group(data):
    """
    Convert to ***
    """
    return data

def treat_family(data):
    """
    Convert to ***
    """
    return data

def extract_income(income):
    """
    Return columns of family income and non family income from a given tract income row.
    """
    # CONSTANTS
    faminco_range = range(15, 88, 8)
    nonfaminco_range = range(19, 19 + (88 - 15), 8)

    faminco = [treat_income(income[x]) for x in faminco_range]
    nonfaminco = [treat_income(income[x]) for x in nonfaminco_range]
    return faminco, nonfaminco

def extract_demo(demo):
    """
    Return columns of demo row.
    """
    demo_range = chain(range(8), range(12, 69))

    demo = [treat_demo(demo[x]) for x in demo_range]
    return demo

def extract_group(group):
    """
    Return columns of group row.
    """
    group_range = chain(range(6),range(10,14),range(15,18),range(20,24),range(25,28),range(30,34),range(35,38),range(41,45),range(46,49),range(51,55),range(56,59),range(61,65),range(66,69))

    group = [treat_group(group[x]) for x in group_range]
    return group

def extract_family(family):
    """
    Return columns of family row.
    """
    # no range, take all columns
    family = [treat_family(x) for x in family]
    return family

def build_census_block(demo_row, group_row, family_row, family_income, non_family_income, house_count, person_count):
    # Get appropriate ranges/columns and convert to strings/doubles where appropriate
    demo = extract_demo(demo_row)
    group = extract_group(group_row)
    family = extract_family(family_row)

    madults, mchildren, fadults, fchildren = people_builder(demo)
    group_quarters, madults, mchildren, fadults, fchildren = get_group_quarters(group, madults, mchildren, fadults, fchildren)
    households, madults, mchildren, fadults, fchildren = household_helper(demo, family, madults, mchildren, fadults, fchildren)

    # grab summary information
    latlon = [float(demo_row[x]) for x in [8, 9]]
    county = demo_row[2]
    state = demo_row[1]
    tract = demo_row[3]
    block = demo_row[5] 

    # write block to output
    rows, house_count, person_count = block_builder(households, group_quarters, latlon, house_count, person_count,
                            family_income, non_family_income, state, county, tract, block)
    return rows, house_count, person_count

def block_builder(houses, groups, latlon, house_count, person_count, fam_inco, non_fam_inco, state, county, tract, block):
    """
    Build list of rows for census block, to be returned, and outputed to output source.
    """
    rows = []
    for i, h in enumerate(houses):
        house = [h[2]]
        if len(house) != 0:
            house_count+=1
            hh_income = get_hh_income(fam_inco, non_fam_inco, h[1])
            ind_income = add_individual_income_tt(hh_income, house)
            for j, p in enumerate(house[0]):
                person_count += 1
                idnum = str(1000000000 + person_count)
                pid = str(state) + idnum[1:]
                row = [state, county, tract, block, house_count, p[2], latlon[0], latlon[1], pid, 
                        p[0], p[1], ind_income[j][0], ind_income[j][1], ind_income[j][2]]
                if len(row) != 14:
                    print(row)
                rows.append(row)

    for k, quarter in enumerate(groups):
        if len(quarter) != 0:
            house_count+=1
            for z, q in enumerate(quarter):
                person_count+=1
                idnum = str(1000000000 + person_count)
                pid = str(state) + idnum[1:]
                income = 0
                row = [state, county, tract, block, house_count, q[2], latlon[0], latlon[1], pid, 
                        q[0], q[1], traveler_type(q[0], q[2]), income, income]
                rows.append(row)

    return rows, house_count, person_count

def people_builder(demo):
    """
    Build the population by age group and by gender.
    """
    # ALL MEN AT EACH AGE GROUP (DEMOGRAPHIC QUERY FILE
    M_AGE_DIST = range(10, 33)
    #  ALL WOMEN AT EACH AGE GROUP (DEMOGRAPHIC QUERY FILE
    F_AGE_DIST = range(34, 57)
    return create_residents([int(demo[x]) for x in M_AGE_DIST], [int(demo[y]) for y in F_AGE_DIST])

def get_age(x):
    """
    Return random age in between age brackets.
    """
    AGE_RANGES = [(0,4) , (5,9) , (10,14) , (15,17), (18,19), (20,20), (21,21), (22,24), (25,29), (30,34),\
            (35,39), (40,44), (45,49), (50,54), (55,59), (60,61), (62,64), (65,66), (67,69) , (70, 74), (75,79), (80,84), (85,100) ]
    return rd.randint(AGE_RANGES[x][0], AGE_RANGES[x][1])

def create_residents(male_age_groups, female_age_groups):
    """
    Build people arrays.
    """
    madults = []; mchildren = []; fadults = []; fchildren = []
    for i, agepop in enumerate(male_age_groups):
        for j in range(agepop):
            x = get_age(i)
            if x <= 17: 
                mchildren.append([x, 1, -1])
            else:
                madults.append([x, 1, -1])
    for i, agepop in enumerate(female_age_groups):
        for j in range(agepop):
            x = get_age(i)
            if x <= 17:
                fchildren.append([x, 0, -1])
            else:
                fadults.append([x, 0, -1])
    return madults, mchildren, fadults, fchildren

def get_group_quarters(r, madults, mchildren, fadults, fchildren):
    """
    Adapt people lists to account for residents in group quarters.
    """
    # CONSTANT
    GROUP_QUARTERS = range(6, 48)    
    cfa = []; j = []; nh = []; oiq = []; sh = []; m = []; oniq = []
    l = [cfa, j, nh, oiq, sh, m, oniq]
    gqlist = [int(r[x]) for x in GROUP_QUARTERS]
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
        # Add them to the right group housing list if they are in the right age           
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
                    popped[2] = mod+2
                    l[mod].append(popped)
    return l, madults, mchildren, fadults, fchildren

def household_helper(demo, family, madults, mchildren, fadults, fchildren):
    """
    Prepare data to build households in census block.
    """
    # HOUSEHOLD SIZE DISTRIBUTION
    HH_DIST = range(58,65)
    # HOUSEHOLD RELATIONSHIP DISTRIBUTION
    HH_REL_DIST = range(6,31)
    
    # READ IN HOUSE SIZES
    house_sizes = expand_household_size([int(demo[x]) for x in HH_DIST])
    rel = [int(family[x]) for x in HH_REL_DIST]
    # READ IN POPULATION IN HOUSEHOLDS BY TYPE
    house_pop = [rel[2], rel[17]]
    # READ IN DISTRIBUTION OF HOUSEHOLDERS BY TYPE BY SEX
    fam_holder = expand_distribution([rel[x] for x in [4,5]])
    non_fam_holder = expand_distribution([rel[x] for x in [18,21]])
    # READ IN NUMBER OF NON FAMILY HOUSEHOLDERS LIVING ALONE OR TOGETHER
    no_fam_alone = [rel[x] for x in [19, 20, 22, 23]]
    # READ IN FAMILY RELATIONS FOR FAMILY HOUSEHOLDS
    fam_rel = expand_distribution([rel[x] for x in range(6,17)])
    htype = []
    for i in range(len(fam_holder)):
        htype.append(0)
    for i in range(len(non_fam_holder)):
        htype.append(1)
    # ALL HOUSES FOR THAT BLOCK
    hhh = build_houses(house_sizes, house_pop, fam_holder, non_fam_holder,
                 htype, no_fam_alone, fam_rel, madults, mchildren, fadults, fchildren)
    return hhh

def expand_distribution(dist, add=0):
    """
    Expand a list into a selectable distribution
    """
    vec = [[i]*int(round(float(x))) for i, x in enumerate(dist)]
    return [(num + add) for elem in vec for num in elem]

def expand_household_size(dist):
    vec = [[i]*int(round(x)) for i, x in enumerate(dist)]
    return [(num+1) for elem in vec for num in elem]

def select_one(l):
    """
    Select and return element from list and pop the value (without replace)
    """
    r = np.random.randint(0,len(l)) if len(l)>1 else 0
    if not l:
        return 0, l
    else:
        val = l.pop(r)
        return val, l 

def build_houses(house_sizes, house_pop, fam_holder, non_fam_holder, htype, no_fam_alone, fam_rel, madults, mchildren, fadults, fchildren):
    """
    Build each individual household within a Census block.
    """
    numhouses = len(house_sizes)
    allHouses = []
    allHouseHolders = []
    'Population Counters'
    inNonFamHousing = 0
    inFamHousing = 0
    'Householder Availability'
    nonfamHouseHoldersAvailable = len(non_fam_holder)
    famHouseHoldersAvailable = len(fam_holder)

    'Initialize all HouseHolders within Census Block'
    for i in range(numhouses):
        'Select Household Type From Distribution (0: family, 1: nonfamily)'
        hht, htype = select_one(htype)
        if (hht == 0):
            gender, fam_holder = select_one(fam_holder)
            inFamHousing+=1
        else:
            gender, non_fam_holder = select_one(non_fam_holder)
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
            if (no_fam_alone[0] != 0):
                house_sizes.remove(1)
                allHouses.append([0, hh[2], [hh]])
                hh[3] = 0
                no_fam_alone[0]-=1
                nonfamHouseHoldersAvailable-=1
                continue
        'Female, Non Family Household'
        if (hh[2] == 1) and (hh[1] == 0):
            if (no_fam_alone[2] != 0):
                house_sizes.remove(1)
                allHouses.append([0, hh[2], [hh]])
                hh[3] = 0
                no_fam_alone[2]-=1
                nonfamHouseHoldersAvailable-=1
                continue
    
    house_sizes.sort()
    house_sizes = house_sizes[::-1]
    
    'Populate Non Family Houses with Non Family Householders and Create Household Object'
    while((inNonFamHousing < house_pop[1]) and (nonfamHouseHoldersAvailable > 0)):
        for hh in enumerate(allHouseHolders):
            hh = hh[1]
            if (nonfamHouseHoldersAvailable > 0):
                if ((hh[2] == 1) and (hh[3] == -1)):
                    if len(house_sizes) > 0 :
                        size = house_sizes.pop()
                    else:
                        break
                    hh[3] = 0
                    allHouses.append([size-1, hh[2], [hh]])
                    nonfamHouseHoldersAvailable-=1
                    inNonFamHousing+=(size-1)
                    continue
    'Populate Family Households for Family Householders and Create Household Object'
    while((inFamHousing < house_pop[0]) and (famHouseHoldersAvailable>0)):
        for hh in enumerate(allHouseHolders):
            hh = hh[1]
            if (famHouseHoldersAvailable > 0):
                if ((hh[2] == 0) and (hh[3] == -1)):
                    if len(house_sizes) > 0 :
                        size = house_sizes.pop()
                    else:
                        break
                    hh[3] = 0
                    allHouses.append([size-1, hh[2], [hh]])
                    famHouseHoldersAvailable-=1
                    inFamHousing+=(size-1)
                    continue
    'Populate Households with All Family Relations, Exhausting Family Relation Distribution'          
    for j, i in enumerate(fam_rel):
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

    return allHouses, madults, mchildren, fadults, fchildren

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

def get_hh_income(fam_inco, non_fam_inco, hht):
    """
    Draw on household income distributions and return a value within the bracket.
    """
    if hht:
        i = non_fam_inco
    else:
        i = fam_inco
    ie = expand_distribution(i)
    val, ie = select_one(ie)
    bracket = val + 1
    if bracket == 1:
        amount = rd.triangular(2000, 10000,7500)
    else:
        amount = rd.uniform(INCOME_BRACKETS[bracket][0], INCOME_BRACKETS[bracket][1])
    return amount

def income_amount_to_code(income):
    """
    Translate the amount of income to the bracket.
    """
    for k in INCOME_BRACKETS.keys():
        if income<=INCOME_BRACKETS[k][1] and income>=INCOME_BRACKETS[k][0] and income != 0:
            return k
        elif income == 0:
            return 0

def add_individual_income_tt(hhi, h):
    """
    Add individual income to the household members.
    """
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

def traveler_type(age, hht):
    ##0:DNT:0-5, 79+ and those in correct. fac, juvee, nursing homes, other, and military quarters
    ##1:SCN:5-18: 6-15, 16-18*99.948% ##2:SCW:16-18*.0512%
    ##3:CNT:18-22*90.34% + in Dorms ##4:CCW:18-22*9.66% (work in same county)
    ##5:TTT:22-64*78% ##6:HWT:22-64*22% + 65-79 #unemployed(~10%) + work-at-home (~8%) +sickdays
    temp = rd.uniform(0,1)
    if (age >= 0 and age< 5) or (age>79) or (hht in [2,3,4,5,7]):
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