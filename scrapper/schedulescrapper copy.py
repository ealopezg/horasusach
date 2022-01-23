from re import S
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

days = {"Lunes": "L","Martes": "M","Miércoles": "W","Jueves":"J","Viernes":"V","Sábado":"S"}
hours = {"01-02":"1","03-04":"2","05-06":"3","07-08":"4","09-10":"5","11-12":"6","13-14":"7","15-16":"8","17-18":"9"}
def parseDaySchedule(data):
    out = []
    for e in data.contents:
        if isinstance(e, str):
            striped_day = e.split(" ")
            classroom = ' '.join(striped_day[2:])[1:-1]
            day = days[striped_day[0]]
            hour = hours[striped_day[1]]
            if classroom == "SIN SALA":
                classroom_number = " "
                classroom = " "
                display = day+hour
            else:
                classroom = classroom.replace("SALA ","")
                classroom_number = classroom.split(" ")[0]
                display = day+hour+" ("+classroom_number+")"
            out.append({"display": display,"day":day,"hour":hour,"classroom":classroom,"classroom_number":classroom_number})
    return out
            


def getSchedule(id_school,id_program,period):
    schedule = {}
    driver = webdriver.Firefox()
    driver.get("https://registro.usach.cl/index.php?ct=horario")
    
    school = driver.find_element(By.XPATH,"//select[@id='id_facultad']/option[@value='{}']".format(id_school))
    school.click()
    #schedule['school_name'] = school.text.replace(id_school+' - ','')


    wait = WebDriverWait(driver,15)
    program = wait.until(EC.presence_of_element_located((By.XPATH,"//select[@id='id_list_carrera']/option[@value='{}']".format(id_program))))
    #schedule['program'] = program.text.replace(id_program+' - ','')
    program.click()

    select_period = Select(driver.find_element(By.XPATH,"//select[@id='id_periodo']"))
    select_period.select_by_value(period)

    driver.find_element(By.ID,'enterButton').click()
    new_tab = driver.window_handles[1]
    driver.switch_to.window(new_tab)
    wait.until(EC.presence_of_element_located((By.XPATH,'/html/body/center/table[1]')))
    
    html = driver.page_source
    driver.close()
    driver.quit()

    soup = BeautifulSoup(html,features="html.parser")
    for level_table in soup.body.center.find_all('table',recursive=False)[:-1]:
        trs = level_table.tbody.find_all('tr',recursive=False)
        level = trs[0].td.table.tbody.find_all('tr')[1].find_all('td')[2].contents[4].text.strip()
        schedules = trs[2].td.table.tbody.find_all('tr',recursive=False)[1].td.font.table.tbody.find_all('tr',recursive=False)
        i = 1
        schedule[level] = {}
        while i < len(schedules):
            sch = {}
            cols = schedules[i].find_all('td',recursive = False)
            #sch['code'] = cols[1].text
            sch['type'] = cols[2].text
            #sch['section'] = cols[3].text
            sch['name'] = cols[4].text
            sch['spaces'] = cols[5].text
            sch['enrolled'] = cols[6].text
            sch['teachers'] = []
            sch['schedule'] = {}
            if len(cols) < 9:
                j = i+1
                while True:
                    next_row_cols = schedules[j].find_all('td',recursive = False)
                    if(len(next_row_cols) != 2):
                        j = j-1
                        break
                    day_schedule = parseDaySchedule(next_row_cols[1].strong.font)
                    for d in day_schedule:
                        if d['day'] not in sch['schedule']:
                            sch['schedule'][d['day']] = {}
                        # if d['hour'] not in sch['schedule'][d['day']]:
                        #     sch['schedule'][d['day']][d['hour']] = ""
                        if next_row_cols[0].text != " " and next_row_cols[0].text not in sch['teachers']:
                            sch['teachers'].append(next_row_cols[0].text)
                        sch['schedule'][d['day']][d['hour']] = d['classroom_number']                            
                    j = j+1
                    if(j >= len(schedules)):
                        break
                i = j
            else:
                day_schedule = parseDaySchedule(cols[8].strong.font)
                for d in day_schedule:
                    if d['day'] not in sch['schedule']:
                        sch['schedule'][d['day']] = {}
                    # if d['hour'] not in sch['schedule'][d['day']]:
                    #     sch['schedule'][d['day']][d['hour']] = ""
                    if cols[7].text != " " and cols[7].text not in sch['teachers']:
                        sch['teachers'].append(cols[7].text)
                    sch['schedule'][d['day']][d['hour']] = d['classroom_number']         
            i = i+1
            if cols[1].text not in schedule[level]:
                schedule[level][cols[1].text] = {}
            schedule[level][cols[1].text][cols[3].text] = sch
    return schedule

    

if __name__ == '__main__':
    id_school = "40"
    id_program = "1363"
    id_period = "2022-01"
    # schedule = {id_period: {id_school: {id_program: getSchedule(id_school,id_program,id_period)}}}
    # with open('schedule.json', 'w+') as fp:
    #     json.dump(schedule, fp, indent=4)
    cred = credentials.Certificate("/Users/ealopezg/horario-usach-firebase-adminsdk-dlozi-0064984741.json")

    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://horario-usach-default-rtdb.firebaseio.com/'
    })

    ref = db.reference(id_period+'/'+id_school+'/'+id_program+'/11/13237')
    print(ref.order_by_child('teachers').equal_to("GONZALO PEDRO NOLASCO ACUNA LEIVA").get())

    