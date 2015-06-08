import os
import requests
from BeautifulSoup import BeautifulSoup
import re
#Open File
import webbrowser
import os

def getOpenHouses(s,mlid):
    date=None
    time=None
    url="http://vow.mlspin.com/clients/ShowOpenHouse.aspx?List_No="+str(mlid)
    r = s.get(url)
    soup = BeautifulSoup(r.content)
    x=0
    for table in soup.findAll('table'):
        if x==2:
            #print table
            z=0
            for r in table.findAll('td'):
                if z==0:
                    text_parts = r.findAll(text=True)
                    text = ''.join(text_parts)
                    date=text.rstrip().lstrip()
                    date=' '.join(date.split())
                if z==1:
                    text_parts = r.findAll(text=True)
                    text = ''.join(text_parts)
                    time=text.rstrip().lstrip()
                    time=' '.join(time.split())
                z+=1
        x+=1
    return date,time
        
s = requests.session()

cid='CLIENT_ID_HERE'
password='PASSWORD_HERE'

money = re.compile('|'.join([
  r'^\$?(\d*\.\d{1,2})$',  # e.g., $.50, .50, $1.50, $.5, .5
  r'^\$?(\d+)$',           # e.g., $500, $5, 500, 5
  r'^\$(\d+\.?)$',         # e.g., $5.
]))

#
#<a href="report.aspx?thisnum=6&amp;mls=71852326" style="color:blue;">
#<b>482 Beale Street&nbsp;Quincy, MA</b>
#</a>

#Get All The Rows
results=open('houses.txt',"w")

html_template=''
for line in open('Template.html','r'):
    html_template+=line
    
address_list=''
open_house_list=''
dollar_amount_list=''

num_houses=0
page_num=0
max_page=0

while page_num<max_page or (max_page==0 and page_num==0):
    
    page_num=page_num+1
    #print page_num,num_houses
    print "Processing Page : "+str(page_num)
    
    num_houses=0
    start=False
    
    s.post('http://vow.mlspin.com/?cid='+cid+'&pass='+password)
    r = s.get('http://vow.mlspin.com/clients/index.aspx?p='+str(page_num))
    soup = BeautifulSoup(r.content)

    for select in soup.findAll('select', {"name":"p"}):
        #print str(select)
        for option in select.findAll('option'):
            text_parts = option.findAll(text=True)
            text = ''.join(text_parts)
            max_page=int(text)
            
    
    x=0
    for table in soup.findAll('table', border="0"):
        if x==5:
            for row in table.findAll('tr'):
                id=""
                date=""
                time=""
                href_row=row.find('a')
                if  href_row!=None:
                    if str(href_row['href']).count('javascript')==0:
                        num_houses+=1
                        id=href_row['href'].split("mls=")[1]
                        mls_url= str("http://vow.mlspin.com/clients/"+href_row['href'])
                        text_parts = href_row.findAll(text=True)
                        text = ''.join(text_parts)
                        name_of_building=text.replace('&nbsp;',' ')
                        
                        for img in row.findAll('img'):
                            if img['src']=="http://media.mlspin.com/images/openhouse.png":
                                date,time=getOpenHouses(s,id)
                                
                                #print id,date,time
                                results.write(id+"\t"+mls_url.rstrip().lstrip()+"\t"+name_of_building.rstrip().lstrip()+"\t"+date+"\t"+time+"\n")
                                address_list+='"'+name_of_building.rstrip().lstrip()+'",'+'\n'
                                timing=date+' '+time
                                open_house_list+='"'+timing.rstrip().lstrip()+'",'+'\n'
                                
                            
                                text_parts = row.findAll('td', text = re.compile('([$])(\d+(?:\.\d{2})?)'))
                                dollar_parts = ''.join(text_parts)    
                                dollar_amount=dollar_parts.rstrip().lstrip()
                                dollar_amount_list+='"'+dollar_amount.rstrip().lstrip()+'",'
        x+=1


address_list.rstrip().rstrip(',')
open_house_list.rstrip().rstrip(',')
dollar_amount_list.rstrip().rstrip(',')
html_template=html_template.replace("{'INSERT_ADDRESS_LIST_HERE'}",address_list)
html_template=html_template.replace("{'INSERT_OH_LIST_HERE'}",open_house_list)
html_template=html_template.replace("{'INSERT_PRICE_LIST_HERE'}",dollar_amount_list)

results_html=open('OpenHouses.html','w')

results_html.write(html_template)
results_html.close()

new = 2 # open in a new tab, if possible
webbrowser.open('file://' + os.path.realpath('OpenHouses.html'),new=new)



