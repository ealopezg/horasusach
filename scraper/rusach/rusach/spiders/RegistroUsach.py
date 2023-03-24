import scrapy
import json
from rusach.items import SchoolItem,ProgramItem

DAYS = {
    'Lunes': 'L',
    'Martes': 'M',
    'Miércoles': 'W',
    'Jueves': 'J',
    'Viernes': 'V',
    'Sábado': 'S'
}

HOURS = {
    '01-02': '1',
    '03-04': '2',
    '05-06': '3',
    '07-08': '4',
    '09-10': '5',
    '11-12': '6',
    '13-14': '7',
    '15-16': '8',
    '17-18': '9',
}

class RegistrousachSpider(scrapy.Spider):
    name = 'RegistroUsach'
    allowed_domains = ['registro.usach.cl']
    BASE_URL = 'https://registro.usach.cl/index.php?ct=horario'
    
    def start_requests(self):
        yield scrapy.Request(self.BASE_URL,callback=self.parse_schools)
    
    def parse_schools(self,response):
        schools_selector = response.selector.xpath('//*[@id="id_facultad"]').css('option[value]')
        for school_selector in schools_selector:
            school = SchoolItem(id=school_selector.attrib['value'],name=school_selector.xpath('text()').get().split(' - ')[1],programs=[])
            yield scrapy.FormRequest(
                url=self.BASE_URL+'&mt=get_carreras',
                formdata={'idCombo1': school['id']},
                callback=self.parse_programs,
                cb_kwargs={'school': school}
            )
    
    def parse_programs(self,response,school):
        programs_selector = response.selector.xpath('//*[@id="id_list_carrera"]').css('option[value]')
        for program_selector in programs_selector:
            program = ProgramItem(id_program=program_selector.attrib['value'],id_school=school['id'],name=program_selector.xpath('text()').get().split(' - ')[1],period='2023-01',schedule={})
            school['programs'].append(program)
            yield scrapy.FormRequest(
                url=self.BASE_URL+'&mt=muestra_horario',
                formdata={"id_facultad":school['id'],"id_list_carrera":program['id_program'],"id_periodo": '2023-01'},
                callback=self.parse_schedule,
                cb_kwargs={'school': school,'program': program}
            )
        yield school
                

    
    def parse_schedule(self,response,school,program):
        #from scrapy.shell import inspect_response
        #inspect_response(response, self)
        schedules_selector = response.selector.xpath('/html/body/center/table')
        schedule = {}
        for schedule_selector in schedules_selector[:-1]:
            level = schedule_selector.css('*').xpath('tr[1]/td/table/tr[2]/td[3]/br[3]/preceding-sibling::text()[1]').get().strip()
            courses_selector = schedule_selector.css('*').xpath('tr[3]/td/table/tr[2]/td/font/table/tr[not(@bgcolor)]')
            courses = {}
            last_course_id = None
            last_course_type = None
            
            for course_selector in courses_selector:
                cols_selector = course_selector.xpath('td')
                course = {
                    'duration': '',
                    'code': '',
                    'display_types': '',
                    'name': '',
                    'unique': True,
                    'sections': {}
                }
                if len(cols_selector.getall()) != 2:
                    cols = cols_selector
                    course['duration'] = cols[0].css('::text').get()
                    course['code'] = cols[1].css('::text').get()
                    course['name'] = cols[4].css('::text').get()
                    
                    
                    section = {
                        'section': cols[3].css('::text').get(),
                        'type': cols[2].css('::text').get(),
                        'spaces': cols[5].css('::text').get(),
                        'enrolled': cols[6].css('::text').get(),
                        'teachers': [],
                        'schedule': []
                    }
                    
                    last_course_id = course['code']
                    last_course_type = section['type']
                    
                    if len(cols_selector.getall()) == 9:
                        section['teachers'] = [cols[7].css('::text').get()]
                        section['schedule'] = parse_day(cols[8].css('*').xpath('font/text()').getall())
                        last_course_id = None
                        last_course_type = None
                    
                    if course['code'] not in courses:
                        course['sections'][section['type']] = [section]
                        course['display_types'] = section['type']
                        courses[course['code']] = course
                    else:
                        types = set(courses[course['code']]['display_types'].split('-'))
                        types.add(section['type'])
                        types = list(types)
                        types.sort(reverse=True) # T - L
                        courses[course['code']]['display_types'] = '-'.join(types)
                        courses[course['code']]['unique'] = False
                        if section['type'] not in courses[course['code']]['sections']:
                            courses[course['code']]['sections'][section['type']] = []
                        courses[course['code']]['sections'][section['type']].append(section)

                    
                if len(cols_selector.getall()) == 2:
                    cols = cols_selector
                    courses[last_course_id]['sections'][last_course_type][-1]['teachers'].append(cols[0].css('::text').get())
                    actual_schedule = list(map(lambda x: x['display'],courses[last_course_id]['sections'][last_course_type][-1]['schedule']))
                    for sc in parse_day(cols[1].css('*').xpath('font/text()').getall()):
                        if sc['display'] not in actual_schedule:
                            courses[last_course_id]['sections'][last_course_type][-1]['schedule'].append(sc)
            schedule[level] = courses
        program['schedule'] = schedule
        yield program
                    




def parse_day(data):
    out = []
    for raw_day in data:
        raw_day_split = raw_day.split()
        try:
            day = {
                'day': DAYS[raw_day_split[0]],
                'hour': HOURS[raw_day_split[1]],
                'classroom': ' '.join(raw_day_split[2:]).strip('()').strip(),
                'classroom_number': None
            }
            if day['classroom'] == 'SIN SALA':
                day['classroom'] = None
            else:
                if len(day['classroom'].split()) == 2:
                    day['classroom_number'] = day['classroom'].split()[1]
                    day['classroom'] = day['classroom'].split()[1]
            day['display'] = day['day']+day['hour']
            out.append(day)
        except:
            pass
    return out
            
            