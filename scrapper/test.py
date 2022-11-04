import requests
d = {"id_facultad":"40","id_list_carrera":"1363","id_periodo": "2022-01"}
r = requests.post("https://registro.usach.cl/index.php?ct=horario&mt=muestra_horario",data={"id_facultad":"40","id_list_carrera":"1363","id_periodo": "2022-01"})
print(r.text)

with open("prueba.html", 'w') as f:
    f.write(r.text)
    f.close()