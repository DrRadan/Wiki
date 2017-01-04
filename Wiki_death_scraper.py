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
    months = ["January","February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

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
            days = range(1, 32)
        elif month == "April" or month == "June" or month == "September" or month == "November":
            days = range(1, 31)
        elif month == "February":
            days = range (1, 29)
        
        for day in days:
#Dig through the XML    
            temp = xmltodict.parse(data)["html"]["body"]["div"][2]["div"][2]["div"][3]["ul"][day]["li"]
            for i in range(len(temp)):
                Day.append(day+1)
                Month.append(month)
                Year.append(year)

#Extract name and wikipedia entry text length (words)(there will be a slight overestimation because of non-ascii characters)
                try:
                    ref = temp[i]["a"][0]["@href"]
                    try:
                        start = ref.find('/wiki/') + 6
                        found = ref[start:]
                    except:
                        found = "NA"
                    ID.append(found) #name

                    if found != "NA":
                        try:
                            wiki = WikiApi()
                            results = wiki.find(found)
                            article = wiki.get_article(results[0])
                            a = article.content
                            a = a.split()
                            RefLength.append(len(a))
                        except:
                            RefLength.append("NA")
                    else:
                        RefLength.append("NA")
                except:
                    ID.append("NA")
                    RefLength.append("NA")
#Extract age, Western-English speaking country of origin (WESCO), celebrity-prone-profession (CPP)
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
    name = year + "_results.csv"
    temp.to_csv(name)


else:
    print("Sorry there is some problem with the year you entered. Aborting....")




