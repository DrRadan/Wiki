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
    cpp = ["tv","actor","actress","singer","star","oscar", "nobel","pulitzer","nascar", "television","film","movie","writer","cartoon", "rock", "legend",  "celebrity", "hockey","football", "baseball", "nfl","nhl", "sports","hollywood", "music", "hip-hop", "grammy", "guitar"] #celebrity-prone-profession

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
            try:   #. Some years follow the 0-base and others the 1-base caounting for days of the month. First try 0-base (logical)
                temp = xmltodict.parse(data)["html"]["body"]["div"][2]["div"][2]["div"][3]["ul"][day-1]["li"]
                for i in range(len(temp)):
                    Day.append(day)
                    Month.append(month)
                    Year.append(year)

                    ## A. Determine name of celebrity and lenth of their wikipedia entry page
                    if isinstance(temp[i]["a"], list) == True :  #.. Some years dont need the [0] in the page structure and some not
              			found = temp[i]["a"][0]["#text"]
                    elif isinstance(temp[i]["a"], dict) == True :
						found = temp[i]["a"]["#text"]
                    else:
						found = "NA"

                    ID.append(found)
                    wiki = WikiApi()
                    try:
                    	results = wiki.find(found)
                        article = wiki.get_article(results[0]) #Assume 1st hit is the most relevant. Supported by empirical evidence 
                        a = article.content
                        a = a.split()
                        RefLength.append(len(a))
                    except:
                        RefLength.append("NA")


                    ## B. Determine values Other, Age, WESCO, and CPP within this entry of this day of this month for the year entered
                    try: #.. Some years need the [0] in the page structure and others don't
                        text = temp[i]["#text"]
                        Other.append(text)

                        #1. age
                        text = re.sub( r'\([^)]*\)', '', text) #removes everything in parethneses. It tends to be years that would confuse the script below
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

                        #2. wesco 
                        a = [re.findall(x, text.lower())==[x] for x in wesco] #returns list of False/True
                        test = 0
                        for i in range(len(a)):
                            if a[i] == True:
                                test = 1
                                break
                        WESCO.append(test)
                    
                        # 3. cpp
                        a = [re.findall(x, text.lower())==[x] for x in cpp]
                        test = 0
                        for i in range(len(a)):
                            if a[i] == True:
                                test = 1
                                break
                        CPP.append(test)

                    except: #..
                        Other.append("NA")
                        Age.append("NA")
                        WESCO.append("NA")
                        CPP.append("NA")                    

            except: #. Now redo try for alternative
                try:#. Some years follow the 0-base and others the 1-base caounting for days of the month. Now try 1-base 
                    temp = xmltodict.parse(data)["html"]["body"]["div"][2]["div"][2]["div"][3]["ul"][day]["li"]
                    for i in range(len(temp)):
                        Day.append(day)
                        Month.append(month)
                        Year.append(year)

                    ## A. Determine name of celebrity and lenth of their wikipedia entry page
                    	if isinstance(temp[i]["a"], list) == True : #.. Some years dont need the [0] in the page structure and some not
                        	found = temp[i]["a"][0]["#text"]
                    	elif isinstance(temp[i]["a"], dict) == True :
                        	found = temp[i]["a"]["#text"]
                    	else:
                        	found = "NA"

                    	ID.append(found)
                    	wiki = WikiApi()
                    	try:
                    		results = wiki.find(found)
                        	article = wiki.get_article(results[0]) #Assume 1st hit is the most relevant. Supported by empirical evidence 
                        	a = article.content
                        	a = a.split()
                        	RefLength.append(len(a))
                    	except:
                        	RefLength.append("NA")


                        ## B. Determine values Other, Age, WESCO, and CPP within this entry of this day of this month for the year entered
                        try: #.. Some years need the [0] in the page structure and others don't
                            text = temp[i]["#text"]
                            Other.append(text)

                            #1. age
                            text = re.sub( r'\([^)]*\)', '', text) #removes everything in parethneses. It tends to be years that would confuse the script below
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

                            #2. wesco 
                            a = [re.findall(x, text.lower())==[x] for x in wesco] #returns list of False/True
                            test = 0
                            for i in range(len(a)):
                                if a[i] == True:
                                    test = 1
                                    break
                            WESCO.append(test)
                    
                            # 3. cpp
                            a = [re.findall(x, text.lower())==[x] for x in cpp]
                            test = 0
                            for i in range(len(a)):
                                if a[i] == True:
                                    test = 1
                                    break
                            CPP.append(test)

                        except: #..
                            Other.append("NA")
                            Age.append("NA")
                            WESCO.append("NA")
                            CPP.append("NA")                                        
                except: #.
                    Day.append(day)
                    Month.append(month)
                    Year.append(year)
                    ID.append("NA")
                    RefLength.append("NA")
                    Age.append("NA")
                    WESCO.append("NA")
                    CPP.append("NA")
                    Other.append("NA")

### ~~~~~~~ Debugging Script ~~~~~~~~ ###

#    print "Day: "+str(len(Day))print Day
#    print "Month: "+str(len(Month))
#    print Month
#    print "Year: "+str(len(Year))
#    print Year
#    print "ID: "+str(len(ID))
#    print ID
#    print "Age: "+str(len(Age))
#    print Age
#    print "RefLength: "+str(len(RefLength))
#    print RefLength
#    print "WESCO: "+str(len(WESCO))
#    print WESCO
#    print "CPP: "+str(len(CPP))
#    print CPP
#    print "Other: "+str(len(Other))
#    print Other

### ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ ###

    temp = pd.DataFrame(
    {'Day': Day[0:len(ID)], #this takes care of a weird bug that gives one more entry to D/M/Y because of inconsistensies at the wiki html. 
     'Month': Month[0:len(ID)],
     'Year': Year[0:len(ID)],
     'Name': [x.encode('ascii', 'ignore') for x in ID],
     'Age': Age,
     'ImportanceIndex': RefLength,
     'WESCO': WESCO,
     'CPP': CPP,
     'Text': [x.encode('ascii', 'ignore') for x in Other]
    })
    temp = temp[["Year","Month","Day","Name","Age","ImportanceIndex","WESCO","CPP","Text"]]
    name = "V2/" + year + "_results.csv"
    temp.to_csv(name)


else:
    print("Sorry there is some problem with the year you entered. Aborting....")



