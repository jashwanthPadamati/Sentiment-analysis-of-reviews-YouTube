#importing necessary packages
#install packages which aren't available
from flask import Flask, request, render_template
import matplotlib.pyplot as plt
from textblob import TextBlob
import io
import base64
from selenium import webdriver
import time

#execution starts from main...

#creating app for the Flask
app=Flask(__name__, static_url_path='/')

#default route for methods GET and POST
@app.route("/",methods=['GET','POST'])
#function for the above route
def index():
	return(render_template('open.html'))#displaying open.html to the user

#route for result
@app.route("/res",methods=['GET','POST'])	
#function for the above route
def scrape():
    url=request.form.get('url')#accessing the url from the open.html
    #download and place the chrome driver in the local
    #pass the relavent path to the driver
    driver=webdriver.Chrome(executable_path='C:/Users/Admin/Documents/Sentimental Analysis of reviews/Executable Code/templates/driver/chromedriver.exe')
    #open the url using the driver
    driver.get(url)
    #defining the pause for every scroll that we see in below code 
    pause=5 #setting pause time
    driver.execute_script('window.scrollTo(1, 500);')   # scroll to 500 pixel on the monitor where 500 is height
    time.sleep(pause) #waiting for pause sec
    video = driver.find_element_by_css_selector("video") #accessing video using css selector
    driver.execute_script("arguments[0].muted = true;", video)#muting the video
    driver.execute_script("window.scrollTo(0,750);")# scroll to 750 pixel on the monitor where 750 is height
    time.sleep(pause)#waiting for pause sec
    driver.execute_script("window.scrollTo(0,1000);")# scroll to 750 pixel on the monitor where 750 is height
    time.sleep(pause)#waiting for pause sec
    driver.execute_script("window.scrollTo(0,1500);")# scroll to 1500 pixel on the monitor where 1500 is height
    lastHeight =3000#setting lastheight
    i=0
    while i<10:#runs for either 10 instructions 
        driver.execute_script("window.scrollTo(0,"+str(lastHeight)+");")# scroll to lastheight variable pixel on the monitor
        time.sleep(pause)#waiting for pause sec
        newHeight = driver.execute_script("return document.documentElement.scrollHeight")#setting new height after the scroll
        #out of loop when max height is reached
        if newHeight == lastHeight:
            break
        division=newHeight-lastHeight# difference of heights
        lastHeight+=division#update the last height for the scroll
        driver.execute_script("window.scrollTo(0,"+str(lastHeight)+");")#scroll to last height
        lastHeight = newHeight#update the lastheight
        i+=1#iteration icremental
        
    '''Using Xpath along with id'''
    comment_div=driver.find_element_by_xpath('//*[@id="contents"]')#getting division of comments
    comments=comment_div.find_elements_by_xpath('//*[@id="content-text"]')#getting comments under comments division 
    likes=comment_div.find_elements_by_xpath('//*[@id="vote-count-middle"]')# getting likes under comments division
    likeslist=[]#To store all the likes count for all the comments collected
    
    '''initialization'''
    no_of_positive=0
    no_of_negetive=0
    no_of_deep_positive=0
    no_of_deep_negetive=0
    no_of_neutral=0
    for like in likes:
        #validating for only digits
        val_like=''.join(filter(lambda x: x.isdigit(),like.text))
        #assigning for empty strings
        if(len(val_like)==0):
            likeslist.append(0)
        else:
            likeslist.append(int(val_like))#conversion to values
    
    for i in range(len(comments)):
        comment=comments[i]#for every comment
        anal=TextBlob(comment.text)#getting the text of comment collected
        '''Getting polarity for all the comments and classifying them accordingly'''
        if anal.sentiment.polarity>0 and anal.sentiment.polarity<0.4:
            no_of_positive+=1+likeslist[i]
        elif anal.sentiment.polarity>=0.4:
            no_of_deep_positive+=1+likeslist[i]
        elif anal.sentiment.polarity==0:
            no_of_neutral+=1+likeslist[i]
        elif anal.sentiment.polarity<=-0.4:
            no_of_deep_negetive+=1+likeslist[i]
        else:
            no_of_negetive+=1+likeslist[i]
                   
    '''building the graph based on analysis'''
    
    labels=['Strongly Positive','Positive','Neutral','Negetive','Strong Negetive']
    values=[no_of_deep_positive,no_of_positive,no_of_neutral,no_of_negetive,no_of_deep_negetive]
    plt.bar(labels,values,color=['blue', 'cyan','green','yellow','red'])
    plt.xlabel('Type of Comments', fontsize=18)
    plt.ylabel('No of Comments', fontsize=18)
    plt.xticks(labels, fontsize=6, rotation=0,fontstyle='italic')
    plt.title('Analysis of Comments')
   
    '''saving the image in the format of png image and creating path for the graph'''
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    graph='data:image/png;base64,{}'.format(graph_url)
    driver.close()
    #sending graph path to the output.html page
    return(render_template('output.html',graph=graph))
    
if(__name__=="__main__"):
	app.run(debug=True)