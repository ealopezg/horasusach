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
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


            


def getPrograms(id_school):
    driver = webdriver.Firefox()
    driver.get("https://registro.usach.cl/index.php?ct=horario")
    
    school = driver.find_element(By.XPATH,"//select[@id='id_facultad']/option[@value='{}']".format(id_school))
    school.click()
    #schedule['school_name'] = school.text.replace(id_school+' - ','')


    wait = WebDriverWait(driver,15)
    wait.until(EC.presence_of_element_located((By.XPATH,"//select[@id='id_list_carrera']/option[@value='1363']")))
    option_programs = driver.find_elements(By.XPATH,"//select[@id='id_list_carrera']/option")
    programs = []
    for p in option_programs[1:]:
        p_name = p.text.split(' - ')[1]
        p_code = p.text.split(' - ')[0]
        programs.append({"name":p_name,"code":p_code})
    driver.close()
    driver.quit()
    return programs
    

    

if __name__ == '__main__':
    program_list = ['1340','1341','1349','1351','1352','1353','1354','1355','1356','1357','1359','1361','1362','1363','1364','1365','1366','1367','1368','1369','1440','1441','1442','1443','1444','1461','1462','1463','1464','1465','1466','1467','1468','1469','1749','1771','1776','1781']
    id_school = '40'
    programs = getPrograms(id_school)
    # id_school = "40"
    # id_program = "1363"
    # id_period = "2022-01"
    # schedule = {id_period: {id_school: {id_program: getSchedule(id_school,id_program,id_period)}}}
    # with open('schedule.json', 'w+') as fp:
    #     json.dump(schedule, fp, indent=4)
    cred = credentials.Certificate("/Users/ealopezg/horario-usach-af4f2-firebase-adminsdk-f6z49-f73e7e9ffa.json")
    firebase_admin.initialize_app(cred, {
        'projectId': 'horario-usach-af4f2'
    })

    db = firestore.client()
    for p in programs:
        if p['code'] in program_list:
            doc_ref = db.collection('schools',id_school,'programs').document(p['code']).set({'name':p['name'],'hidden': False})
        else:
            doc_ref = db.collection('schools',id_school,'programs').document(p['code']).set({'name':p['name'],'hidden': True})

    