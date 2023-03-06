#******* Created by Harrison Beaumont Kinbacher **********
#* In an attempt to automate and control his home garden *
#****************** Contact 0498050007 *******************

#----------------------------------------------------------------------------------------------------------------------------

#libaries used in the processing of this application
from flask import Flask, render_template, request, session
import os
import mysql.connector
import random
app = Flask(__name__)

#session secret key
app.secret_key = "randomPassword"

#reduce the file age to 0 to save space and assist with image cacheing problem - need to test how this effects session storage and cookies
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

#-----------------------------------------------------------------------------------------------------------------------------

#function to remove the previous image when new image is generated
def removeImage():

    #to check if image exists then delete it if it does exist to assit with image display issue
    for file in os.listdir('/var/www/basic-flask-app/static'):
        if file.endswith('.png'):
            stringgg = "/var/www/basic-flask-app/static/{}".format(file)
            os.remove(stringgg) 

    return None


#----------------------------------------------------------------------------------------------------------------------------

#function to save sql pull data to file and create graph and display it from any sql statement
def pullGraph(statement,connection):

        
        #pull soilmoisture data from the database
        gardenDataInsert = statement
        create_cursor = connection.cursor()
        create_cursor.execute(gardenDataInsert)
       
        #save the pulled data into array
        pullStorage = create_cursor.fetchall()
        
        #sorting of the soilMoisture data pull array *(look into optimising this sorting logic)*
        newSave = []
        for (timeDate,x) in pullStorage:
    
            newSave.append(timeDate + " " + x)

        newSave2 = []
        for x in newSave:
            newSave2.append(x.split(" "))

        #close the cursor and the connection
        create_cursor.close()
        connection.close()


        #processing of the data pulled from the database getting it ready to be saved to a text doc in gnu format
        if len(newSave2) >= 1:

            #creates a random int for storing image
            num1 = random.randint(0,5000000)

            #save new data to file
            with open('/var/www/basic-flask-app/moistureData.txt', 'w') as f:
                for line in newSave2:
                    newString = ""
                    counter = 0
                    for x in line:
                        if counter == 0:
                            newString = x
                        if counter == 1:
                            newString = newString + "---" + x
                        if counter > 1:
                            newString = newString + "," + x
                        counter += 1
                
                    f.write(f"{newString}\n")
            
            #generate gnu plot and save the graph in the CLI command
            os.system("gnuplot -p -e \"set terminal png size 1500,1500; set output \'/var/www/basic-flask-app/static/{}.png\'; load \'/var/www/basic-flask-app/gnuMoisturePlotScript\'\"".format(num1))
            
            return num1
        
        return None
    
#---------------------------------------------------------------------------------------------------------------------------

#function to connect to the database and returning the connnection
def databaseConnect():
    
    #GLOBAL sql connection to the local hosted daatabase on my raspPI and associated login information
    connection = mysql.connector.connect(host="localhost",
                                            port=3306, 
                                            user="root", 
                                            password="randomPassword")
    return connection

#--------------------------------------------------------------------------------------------------------------------------

#processing for the landing page
@app.route('/')
def index():
    
    #check to see if data package exists in GET REQUEST - if it does will push incoming garden data into database
    if request.args.get("name") != None:
        
        #calling custom database function
        connection = databaseConnect()
        
        gardenDataInsert = "INSERT INTO garden.soilMoisture (dateTime, moisture) VALUES (NOW(),\"{}\")".format(request.args.get("name"))
        create_cursor = connection.cursor()
        create_cursor.execute(gardenDataInsert)
        connection.commit()

        #close the cursor and the connection
        create_cursor.close()
        connection.close()

        return render_template('index.html')
    
    return render_template('index.html')


#--------------------------------------------------------------------------------------------------------------------------


#soil moisture data pull processing
@app.route('/generate', methods=["post"])
def generateDate():

        #to check if image exists then delete it if it does exist to assit with image display issue
        removeImage()     

        #GLOBAL sql connection to the local hosted daatabase on my raspPI and associated login information using custom function
        connection = databaseConnect()
        #calling custom function to create the graph 
        num1 = pullGraph("select * from  garden.soilMoisture",connection)
        
        if num1 is not None:
            #changing int name to include file path for image display
            num1 = "/static/" + str(num1) + ".png"
            return render_template('main.html', result=[session["user"],num1])
        
        return render_template('main.html', result=[session["user"]])


#--------------------------------------------------------------------------------------------------------------------------

#soil moisture data pull processing
@app.route('/generateDate', methods=["post"])
def generateDateData():

        #to check if image exists then delete it if it does exist to assit with image display issue
        removeImage()      


        #if to make sure date has a value input
        if request.form['date'] != '':
            #GLOBAL sql connection to the local hosted daatabase on my raspPI and associated login information using custom function
            connection = databaseConnect()
            #calling custom function to create the graph 
            num1 = pullGraph("select * from garden.soilMoisture where cast(dateTime as date)=date\"{}\"".format(request.form['date']),connection)

           #if statement to make sure a value comes back to return to the frontend value wont come back if no graph is generated 
            if num1 is not None:
                #changing int name to include file path for image display
                num1 = "/static/" + str(num1) + ".png"
                return render_template('main.html', result=[session["user"],num1])
        
        return render_template('main.html', result=[session["user"]])


#--------------------------------------------------------------------------------------------------------------------------

#soil moisture between dates pull processing
@app.route('/generateDateTwo', methods=["post"])
def generateDateTwo():

        #to check if image exists then delete it if it does exist to assit with image display issue
        removeImage() 
       

        #if to make sure date has a value input
        if (request.form['dateTwo'] != '') and (request.form['dateThree'] != ''):
            #GLOBAL sql connection to the local hosted daatabase on my raspPI and associated login information using custom function
            connection = databaseConnect()
            #calling custom function to create the graph 
            num1 = pullGraph("select * from garden.soilMoisture where cast(dateTime as date) BETWEEN date\"{}\" AND date\"{}\";".format(request.form['dateTwo'],request.form['dateThree']),connection)

            #if statement to make sure a value comes back to return to the frontend value wont come back if no graph is generated 
            if num1 is not None:
                #changing int name to include file path for image display
                num1 = "/static/" + str(num1) + ".png"
                return render_template('main.html', result=[session["user"],num1])
        
        return render_template('main.html', result=[session["user"]])



#---------------------------------------------------------------------------------------------------------------------------

#landing page login form processing
@app.route('/form', methods=["post"])
def form():

    #handles all the login processing making sure the user is logging in correctly
    if not request.form['user-name']:
        return render_template('index.html', result = "Make sure you fill out both Username and Password boxes please :)")


    if not request.form['Password']:
        return render_template('index.html', result = "Make sure you fill out both Username and Password boxes please :)")

    else:
        #GLOBAL sql connection to the local hosted daatabase on my raspPI and associated login information using custom function
        connection = databaseConnect()

        #pulls data from the garden databse login table checking to see if the username exists in it
        loginSearch ="SELECT * from garden.login where username=\"{}\"".format(request.form['user-name'])
        create_cursor = connection.cursor()
        create_cursor.execute(loginSearch)
        pulledValues = create_cursor.fetchall()

        #checks to see if the password matches if the username exists
        if len(pulledValues) == 1:
            if pulledValues[0][1] == request.form['Password']:
                #adding the user to the session then returning the main page
                session["user"] = request.form['user-name']
                return render_template('main.html',result=[session["user"]])
            else:
                 return render_template('index.html', result = "Password Incorrect")
        else:
            #returns nothing found if the account is not found in the database
            stringValue = "no account named {} found".format(request.form['user-name'])
            return render_template('index.html', result = stringValue)

        #close the cursor and the connection
        create_cursor.close()
        connection.close()

    return render_template('index.html')


#--------------------------------------------------------------------------------------------------------------------------


#clearing session on logout
@app.route('/logout')
def logout():
    
    #removing the user from session
    session.pop("user",None)

    return render_template('index.html', result = "logout success")


#--------------------------------------------------------------------------------------------------------------------------

#checking to see if user is logged in and navigating to the main user page
@app.route('/mainNav')
def mainNav():
    
    #checking if user is in session before sending to page to avoid hacking
    if "user" in session:
        return render_template('main.html', result = [session["user"]])
    else:
        return render_template('index.html', result = "You needa login brah")



#--------------------------------------------------------------------------------------------------------------------------

    
#function taken from stackoverflow https://stackoverflow.com/questions/34066804/disabling-caching-in-flask to remove cache for images - need to test how this effects session storage and cookies
@app.after_request
def add_header(r):
    
    #Add headers to both force latest IE rendering engine or Chrome Frame,
    #and also to cache the rendered page for 10 minutes.
    
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r



#---------------------------------------------------------------------------------------------------------------------------


#python flask app run defaults
if __name__ == '__main__':
    app.run()
