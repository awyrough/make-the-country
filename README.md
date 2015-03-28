# make-the-country

Recreate the US population by state and/or by county which is statistically identical to the population as it was in 2010. <br />

This is an independent research project by Hill Wyrough which was spawned from work done with Professsor Alain Kornhauser as part of work in the Transportation program in the Department of Operations Research and Financial Engineering at Princeton. 

## To use

### 1: Clone the repository

git clone git@github.com:awyrough/make-the-country.git

### 2: Preparation

[navigate to git directory]<br />
pip install virtualenv<br />
virtualenv venv<br />
pip install -r requirements<br />

### 3: Authentication

create your secrets.py which has the correct Google API credentials<br />
include your privatekey.pem file in the directory<br />

### 4: Look at argument help

cd make_the_state
python make_the_state.py -h