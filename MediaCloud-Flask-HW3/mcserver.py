import ConfigParser, logging, datetime, os
import re
from flask import Flask, render_template, request
import json, ast 

import mediacloud

CONFIG_FILE = 'settings.config'
basedir = basedir = os.path.dirname(os.path.realpath(__file__))


print (basedir)
# load the settings file
config = ConfigParser.ConfigParser()
config.read(os.path.join(basedir, 'settings.config'))

# set up logging
log_file_path = os.path.join(basedir,'logs','mcserver.log')
logging.basicConfig(filename=log_file_path,level=logging.DEBUG)
logging.info("Starting the MediaCloud example Flask app!")

# clean a mediacloud api client
mc = mediacloud.api.MediaCloud( config.get('mediacloud','api_key') )

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("search-form.html")

@app.route("/search",methods=['POST'])
def search_results():
    keywords = request.form['keywords']
    dateFrom = request.form['date1']
    dateTo = request.form['date2']
    dateFrom = str(dateFrom)
    dateTo = str(dateTo)
    dateFromD = dateFrom.replace(',', '-')
    dateToD = dateTo.replace(',', '-')

    date1 = dateFrom.split(',')
    date2 = dateTo.split(',')
    
    intDate1 = []
    intDate2 = []
    for val in date1:
    
        intDate1.append(int(val))
    for val2 in date2:
  
        intDate2.append(int(val2))

    now = datetime.datetime.now()
    results = mc.sentenceCount(keywords, solr_filter=[mc.publish_date_query( datetime.date( intDate1[0], intDate1[1], intDate1[2]), datetime.date( intDate2[0], intDate2[1], intDate2[2])),'media_sets_id:1'], split=True, split_start_date = dateFromD, split_end_date = dateToD)
    
    splitData = results['split']
    #print splitData
    splitData1 = json.dumps(splitData)
    #for key, value in splitData1.iteritems():
      #  print key, 'corresponds to', d[key]

    z = splitData1.replace('T00:00:00Z', '')
    #print z
    myDict = ast.literal_eval(z)
        
    myDict.pop('end')
    myDict.pop('start')
    myDict.pop('gap')
    a =len(myDict)
    dictKeys = myDict.keys()
    dictVal = myDict.values()

    dataToPlot=[]
    d = {'year': 0, 'value': 0}
    for i in range(a):
        year = unicode( dictKeys[i], 'utf-8')    
        print year
        value = unicode(str( dictVal[i]), 'utf-8')    

        dataToPlot.append({'year': year, 'value':value })

  
    
    dJson = json.dumps(dataToPlot)
    print dJson
    return render_template("search-results.html", 
        keywords=keywords, sentenceCount=results['count'], sentenceCount2=dJson )

                

if __name__ == "__main__":
    app.debug = True
    app.run()
