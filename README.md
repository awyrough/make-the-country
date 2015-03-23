# make-the-country

Recreate the US population by state and/or by county which is statistically identical to the population as it was in 2010. 

This is an independent research project by Hill Wyrough which was spawned from work done with Professsor Alain Kornhauser as part of work in the Transportation program in the Department of Operations Research and Financial Engineering at Princeton. 

## To use

### 1: Clone the repository

git clone git@github.com:awyrough/make-the-country.git

### 2: Preparation

[navigate to git directory]
pip install virtualenv
virtualenv venv
pip install -r requirements

### 3: Authentication

create your secrets.py which has the correct Google API credentials
include your privatekey.pem file in the directory
