year = raw_input('Please type the year you are interested in, from 2007 to 2016:')
if eval(year)<=2016 and eval(year)>=2007:
    print("Thanks! This will take a while. Check this directory later for a file named "+year+"_results.csv")
    
    import urllib
    import json
    import xmltodict
    import pandas as pd
    import time
    import re
    from wikiapi import WikiApi

#Useful variables for looping
    base_url = "https://en.wikipedia.org/wiki/Deaths_in_" 
    months = ["January"]#,"February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

#Useful reference variables
    wesco = ["english","welsh","irish","scottish","british", "american", "canadian", "australian","zealand" ] # Western-English speaking country of origin
    cpp = ["tv","actor","actress","singer","star","oscar", "nobel","pulitzer","nascar", "television","film","movie","writer","cartoon", "rock", "celebrity", "hockey","football", "baseball", "nfl","nhl", "sports","hollywood"] #celebrity-prone-profession

    #Initiate lists of values that will be extracted from Wikipedia for each year
    Day = []
    Month = []
    Year = []
    ID = []
    RefLength = []
    Age = []
    WESCO = []
    CPP =[]
    Other = []
#Loop through months for entered year to construct the url
    for month in months:
        url = base_url + month + "_" + year
        data = urllib.urlopen(url)
        data = data.read()
        
#Assign appropriate number of days to each month (February will on ocassion have 29 days, I will miss 1 day of values. OK)        
        if month == "January" or month == "March" or month == "May" or month == "July" or month == "August" or month == "October" or month == "December":
            #days = range(1, 32)
            days = range(1, 10)
        elif month == "April" or month == "June" or month == "September" or month == "November":
            days = range(1, 31)
        elif month == "February":
            days = range (1, 29)
        
        for day in days:
            Day.append(day)
            Month.append(month)
            Year.append(year)
#Dig through the XML 
            try:   #. Some years follow the 0-base and others the 1-base caounting for days of the month. First try 1-base (most)
                temp = xmltodict.parse(data)["html"]["body"]["div"][2]["div"][2]["div"][3]["ul"][day]["li"]
                for i in range(len(temp)):
#Extract name 
                    try: #.. Some years dont need the [0] in the page structure
                        found = temp[i]["a"][0]["#text"]
                    except: #.. I cannot find the expected syntax
                        try:    #...
                            found = temp[i]["a"]["#text"]
                        except: #... I cannot find an entry even if I remove the '[0]'
                            found = "NA"

            except: #. OK I cannot find anything with 1-base. It has to be 0-base
                try: #. Now try the 0-base 
                    temp = xmltodict.parse(data)["html"]["body"]["div"][2]["div"][2]["div"][3]["ul"][day-1]["li"]
                    for i in range(len(temp)):
#Extract name 
                        try: #.. Some years dont need the [0] in the page structure
                            found = temp[i]["a"][0]["#text"]
                        except: #.. Can I find a valid entry if I remove '[0]' from 'temp[i]["a"][0]["@href"]'?
                            try:    #...
                                found = temp[i]["a"]["#text"]
                            except: #... I cannot find an entry even if I remove the '[0]'
                                found = "NA"
                except: #.
                    found = "NA"
            ID.append(found) #name
#wikipedia entry text length (words)(there will be a slight overestimation because of non-ascii characters)
            if found != "NA":

                try:
                    wiki = WikiApi()
                    results = wiki.find(found)
                    article = wiki.get_article(results[0])
                    a = article.content
                    a = a.split()
                    RefLength.append(len(a))
                except: #....
                    RefLength.append("NA")
            else: #-
                RefLength.append("NA")             

#Extract age, Western-English speaking country of origin (WESCO), celebrity-prone-profession (CPP)
            for i in range(len(temp)):
                try:
                    text =  temp[i]["#text"]
                    Other.append(text)
                    
                    text = re.sub( r'\([^)]*\)', '', text) #removes everything in parethneses. It tends to be years that would confuse the script below
                    #age
                    a = re.findall(r'\d+',text) #finds all numbers
                    if len(a)==1: # there is only one number returned, it has to be age (some very few errors, ~<0.1%, expected)
                        a = int(a[0]) 
                        Age.append(a)
                    # what happens if there are still other numbers included in the text?
                    elif len(a[0]) <= 3: # if the first number has a naximum of 3 digits it has to be age
                        a = int(a[0]) 
                        Age.append(a)
                    else:
                        Age.append("NA") #if more than one numbers are present I cannot guarantee I can ID the age without further work
                    
                    #wesco & cpp
                    a = [re.findall(x, text.lower())==[x] for x in wesco] #returns list of False/True
                    for i in range(len(a)):
                        test = 0
                        if a[i] == True:
                            test = 1
                            break
                    WESCO.append(test)
                    
                    a = [re.findall(x, text.lower())==[x] for x in cpp]
                    for i in range(len(a)):
                        test = 0
                        if a[i] == True:
                            test = 1
                            break
                    CPP.append(test)
                    
                except:
                    WESCO.append("NA")
                    Age.append("NA")
                    CPP.append("NA")
                    Other.append("NA")
            time.sleep(1)#1 second sleep after each day of the month
    
    temp = pd.DataFrame(
    {'Day': Day,
     'Month': Month,
     'Year': Year,
     'Name': [x.encode('ascii', 'ignore') for x in ID],
     'Age': Age,
     'ImportanceIndex': RefLength,
     'WESCO': WESCO,
     'CPP': CPP,
     'Text': [x.encode('ascii', 'ignore') for x in Other]
    })
    temp = temp[["Year","Month","Day","Name","Age","ImportanceIndex","WESCO","CPP","Text"]]
    name = "V2/"+year + "_results.csv"
    temp.to_csv(name)


else:
    print("Sorry there is some problem with the year you entered. Aborting....")




