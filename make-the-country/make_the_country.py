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
