# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import Select
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC

from http.client import OK
import requests

from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import json
import codecs
from html import unescape


days = {"Lunes": "L","Martes": "M","Miércoles": "W","Jueves":"J","Viernes":"V","Sábado":"S"}
hours = {"01-02":"1","03-04":"2","05-06":"3","07-08":"4","09-10":"5","11-12":"6","13-14":"7","15-16":"8","17-18":"9"}
def parseDaySchedule(data):
    out = []
    for e in data.contents:
        if isinstance(e, str):
            striped_day = e.split(" ")
            print(striped_day)
            classroom = ' '.join(striped_day[2:])[1:-1]
            day = days[striped_day[0]]
            hour = hours[striped_day[1]]
            if classroom == "SIN SALA":
                classroom_number = None
                classroom = None
                display = day+hour
            else:
                classroom = classroom.replace("SALA ","")
                classroom_number = classroom.split(" ")[0]
                display = day+hour+" ("+classroom_number+")"
            out.append({"display": display,"day":day,"hour":hour,"classroom":classroom,"classroom_number":classroom_number})
    return out
            


def getSchedule(id_school,id_program,period):
    schedule = {"id_school": id_school, "id_program": id_program, "period": period}
    # r = requests.post("https://registro.usach.cl/index.php?ct=horario&mt=muestra_horario",data={"id_facultad":id_school,"id_list_carrera":id_program,"id_periodo": period})

    # if r.status_code != 200:
    #     return None
    # print(r.text)

    with open('response2.txt','r') as f:
        text = f.read()






    # driver = webdriver.Firefox()
    # driver.get("https://registro.usach.cl/index.php?ct=horario")
    
    # school = driver.find_element(By.XPATH,"//select[@id='id_facultad']/option[@value='{}']".format(id_school))
    # school.click()
    # #schedule['school_name'] = school.text.replace(id_school+' - ','')


    # wait = WebDriverWait(driver,60)
    # program = wait.until(EC.presence_of_element_located((By.XPATH,"//select[@id='id_list_carrera']/option[@value='{}']".format(id_program))))
    # #schedule['program'] = program.text.replace(id_program+' - ','')
    # program.click()

    # select_period = Select(driver.find_element(By.XPATH,"//select[@id='id_periodo']"))
    # select_period.select_by_value(period)

    # driver.find_element(By.ID,'enterButton').click()
    # new_tab = driver.window_handles[1]
    # driver.switch_to.window(new_tab)
    # wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/center/table[1]')))
    
    # html = driver.page_source
    # driver.close()
    # driver.quit()

    soup = BeautifulSoup(text,features="html.parser")
    semesters = {}
    for level_table in soup.body.center.find_all('table',recursive=False)[:-1]:
        trs = level_table.find_all('tr',recursive=False)
        level = trs[0].td.table.find_all('tr')[1].find_all('td')[2].contents[4].text.strip()
        schedules = trs[2].td.table.find_all('tr',recursive=False)[1].td.font.table.find_all('tr',recursive=False)
        i = 1
        semester = {}
        while i < len(schedules):
            print(i)
            sch = {}
            cols = schedules[i].find_all('td',recursive = False)
            print(len(cols))
            # sch['duration'] = cols[0].text
            # sch['code'] = cols[1].text
            # sch['name'] = cols[4].text
            # sch['type'] = cols[2].text
            
            sch['section'] = cols[3].text
            sch['spaces'] = cols[5].text
            sch['enrolled'] = cols[6].text
            sch['teachers'] = []
            sch['schedule'] = []
            d_h = set()
            if len(cols) < 9:
                j = i+1
                while True:
                    print(j)
                    next_row_cols = schedules[j].find_all('td',recursive = False)
                    print(next_row_cols)
                    if(len(next_row_cols) != 2):
                        j = j-1
                        break
                    if next_row_cols[0].text != " " and next_row_cols[0].text not in sch['teachers']:
                            sch['teachers'].append(next_row_cols[0].text)
                    days_hours = parseDaySchedule(next_row_cols[1].strong.font)
                    for d in days_hours:
                        if d['day']+d['hour'] not in d_h:
                            sch['schedule'].append(d)
                            d_h.add(d['day']+d['hour'])
                    j = j+1
                    if(j >= len(schedules)):
                        break
                i = j
            else:
                if cols[7].text != " " and cols[7].text not in sch['teachers']:
                    sch['teachers'].append(cols[7].text)
                days_hours = parseDaySchedule(cols[8].strong.font)
                for d in days_hours:
                    if d['day']+d['hour'] not in d_h:
                        sch['schedule'].append(d)
                        d_h.add(d['day']+d['hour'])
            i = i+1
            if cols[1].text not in semester:
                semester[cols[1].text] = {}
                semester[cols[1].text]['code'] = cols[1].text
                semester[cols[1].text]['name'] = cols[4].text
                semester[cols[1].text]['duration'] = cols[0].text
                semester[cols[1].text]['sections'] = {}
                semester[cols[1].text]['unique'] = False
                semester[cols[1].text]['display_types'] = ""
            if cols[2].text not in semester[cols[1].text]['sections']:
                semester[cols[1].text]['sections'][cols[2].text] = []
            semester[cols[1].text]['sections'][cols[2].text].append(sch)
        for subject in semester:
            types = [*semester[subject]['sections']];
            semester[subject]['display_types'] = '-'.join(types)
            if len(types) == 1 and len(semester[subject]['sections'][types[0]]) == 1:
                semester[subject]['unique'] = True
                
        semesters[level] = semester
    schedule['schedule'] = semesters   
    return schedule

    

if __name__ == '__main__':
    id_school = "40"
    #id_program = "1364"
    cred = credentials.Certificate("/Users/ealopezg/horario-usach-af4f2-firebase-adminsdk-f6z49-f73e7e9ffa.json")

    firebase_admin.initialize_app(cred, {
        'projectId': 'horario-usach-af4f2'
    })

    db = firestore.client()
    programs = ['1363']
    #programs = ['1361','1362','1363','1364','1365','1366','1367','1368','1369','1440','1441','1442','1443','1444','1461','1462','1463','1464','1465','1466','1467','1468','1469','1749','1771','1776','1781']
    #programs = ['1340','1341','1349','1351','1352','1353','1354','1355','1356','1357','1359','1361','1362','1363','1364','1365','1366','1367','1368','1369','1440','1441','1442','1443','1444','1461','1462','1463','1464','1465','1466','1467','1468','1469','1749','1771','1776','1781']
    #programs = ['1361','1362','1363','1364','1365','1366','1367']
   #programs = ['1361','1362','1363','1364','1365','1366','1367','1368','1369','1440','1441','1442','1443','1444','1461','1462','1463','1464','1465','1466','1467','1468','1469']
    id_period = "2022-01"
    for id_program in programs:
        print(id_program)
        schedule = getSchedule(id_school,id_program,id_period)
        # if schedule:
        #     doc_ref = db.collection(u'schedules').document(id_school+'_'+id_program+'_'+id_period).set(schedule)

    # with open('schedule.json', 'w+') as fp:
    #     json.dump(schedule, fp, indent=4)