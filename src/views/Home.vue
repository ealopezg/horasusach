<template>
  <div class="home">
    <div class="container-fluid p-xl-5 p-md-4">
      <div class="row">
        <div class="col mb-sm-3">
          <div class="p-3 mb-3">
            <h3>Buscador de cursos</h3>
            <select @change="handleSelectSchool()" v-model="id_school" class="form-select mb-3" aria-label="Elegir escuela o facultad">
              <option selected value="">Elegir escuela o facultad</option>
              <option v-for="(school,index) in schools" v-bind:key="index" :value="school.id" @click="handleSelectSchool(school.id)">{{school.name}}</option>
            </select>
            <select @change="handleSelectProgram()" v-model="id_program" class="form-select mb-3" aria-label="Elegir una carrera o programa" :disabled="id_school == ''">
              <option  selected value="">Elegir una carrera o programa</option>
              <option v-for="(program,index) in programs" v-bind:key="index" :value="program.id" >{{program.id + ' - '+program.name}}</option>
            </select>
            <select @change="handleSelectSemester()" v-model="semester" class="form-select" aria-label="Elegir nivel" :disabled="id_program == ''">
              <option selected value="">Elegir nivel</option>
              <option v-for="(semester_val,semester) in semester_schedule" v-bind:key="semester" :value="semester" >{{semester}}</option>
            </select>
          </div>
          
          <div class="table-responsive" v-if="pages > 0">
            <table class="table table-sm align-middle">
              <thead>
                <tr>
                  <th scope="col">Código</th>
                  <th scope="col">Sección</th>
                  <th scope="col">Tipo</th>
                  <th scope="col">Nombre</th>
                  <th scope="col">Profesores</th>
                  <th scope="col">Horario</th>
                  <th scope="col">Acción</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(subject,code) in subjects[actual_page]" v-bind:key="code">
                  <th>{{ subject.code }}</th>
                  <th>{{ subject.unique ? subject.sections[subject.display_types][0].section : 'Varias' }}</th>
                  <th>{{ subject.display_types }}</th>
                  <th>{{ subject.name }}</th>
                  <th><div v-if="subject.unique">
                        <span v-for="(teacher,index) in subject.sections[subject.display_types][0].teachers" v-bind:key="index" style="font-size: 0.7em">{{ teacher }}<br></span>
                    </div><div v-else>-</div></th>
                  <th><div v-if="subject.unique"><span v-for="sch in subject.sections[subject.display_types][0].schedule" :key="sch.display" :class="!isAlreadyinSchedule(subject) && this.schedule[sch['day']][sch['hour']].length > 0 ? 'text-danger': ''">{{ sch.display }}</span></div><div v-else>-</div></th>
                  <th><button :disabled="isAlreadyinSchedule(subject) && subject.unique" type="button" :class="'btn '+(isAlreadyinSchedule(subject) ? 'btn-warning':'btn-primary')" @click="handleAddSubjectToSchedule(subject)"><i v-if="!isAlreadyinSchedule(subject)" class="fas fa-plus"></i><i v-else class="fas fa-check"></i></button></th>
                </tr>
              </tbody>
            </table>
            <nav>
              <ul class="pagination" v-if="pages > 0">
                <li :class="'page-item ' + (this.actual_page-1 == 0 ? 'disabled': '')">
                  <a class="page-link" aria-label="Previous" @click="this.actual_page--" >
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                </li>
                <li :class="'page-item '+ (page+1 == this.actual_page ? 'active': '')" v-for="page in [...Array(this.pages).keys(pages)]" v-bind:key="page" @click="this.actual_page = page+1"><a  class="page-link">{{ page+1 }}</a></li>
                <li :class="'page-item ' + (this.pages == this.actual_page ? 'disabled': '')">
                  <a class="page-link" aria-label="Next" @click="this.actual_page++">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                </li>
              </ul>
            </nav>
          </div>
        </div>
        <div class="col-xs-12 col-xl-6 mt-xl-0 mt-4">
          <div class="row mb-3 align-items-end">
            <div class="d-flex flex-wrap justify-content-between align-items-center">
              <div class="col d-flex align-items-center justify-content-center"><h3>Mi Horario</h3></div>
              <div class="col-md-2 justify-content-end d-flex">
                <button type="button" class="btn btn-danger" @click="handleDeleteSchedule()"><i class="fas fa-trash"></i></button>
              </div>
            </div>
          </div>
          <div class="row justify-content-center">
            <div class="container justify-content-center">
              <div class="table-responsive">
                <table class="table table-bordered table-sm table-schedule">
                <thead>
                  <tr>
                    <th scope="col">Hora</th>
                    <th scope="col">Lunes<br>(L)</th>
                    <th scope="col">Martes<br>(M)</th>
                    <th scope="col">Miercoles<br>(W)</th>
                    <th scope="col">Jueves<br>(J)</th>
                    <th scope="col">Viernes<br>(V)</th>
                    <th scope="col">Sábado<br>(S)</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(hour,index) in [1,2,3,4,5,6,7,8,9]" v-bind:key="index">
                    <th scope="row">{{ hour }}<br>{{ this.hours[hour] }}</th>
                    <td v-for="(day,index) in ['L','M','W','J','V','S']" v-bind:key="index" @click="makeBusy(day,hour)" :class="(this.schedule[day][hour].length > 1 ? 'bg-danger':'')+(this.busy[day+hour] != undefined ? 'table-active': '')+ ' align-middle'"><div v-for="(s,index) in this.schedule[day][hour]" v-bind:key="index"><schedule  :code="s.code" :section="s.section" :type="s.type" :name="s.name" :classroom="s.classroom" :color="s.color"/><br></div></td>
                  </tr>
                </tbody>
              </table>
              </div>
              
            </div>
            
          </div>
          <div class="row">
            <div class="table-responsive" v-if="Object.keys(subjects_added).length > 0">
              <table class="table table-sm align-middle">
                <thead>
                  <tr>
                    <th scope="col">Código</th>
                    <th scope="col">Sección</th>
                    <th scope="col">Nombre</th>
                    <th scope="col">Profesores</th>
                    <th scope="col">Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(subject,key) in subjects_added" v-bind:key="key">
                    <th><schedule  :code="subject.code" :section="subject.section" :type="subject.type" :color="subject.color"/></th>
                    <th>{{ subject.section }}</th>
                    <th>{{ subject.name }}</th>
                    <th><div v-if="subject.teachers.length > 0">
                        <span v-for="(teacher,index) in subject.teachers" v-bind:key="index" style="font-size: 0.7em">{{ teacher }}<br></span>
                      </div><div v-else>-</div></th>
                    <th><button type="button" class="btn btn-danger" @click="handleDeleteSubjectFromSchedule(key)"><i class="fas fa-minus"></i></button></th>
                  </tr>
                </tbody>
              </table>
            </div>

          </div>
          
        </div>
      </div>
    </div>
    <div class="modal fade" id="subject_modal" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-fullscreen-md-down">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">Agregar {{ this.subject_modal.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="container">
              <div class="row" v-for="(sections,type) in this.subject_modal.sections" v-bind:key="type">
                <h4>{{ this.section_types[type] ?? type}}</h4>
                <table class="table table-sm align-middle" >
                  <thead>
                    <tr>
                      <th scope="col"></th>
                      <th scope="col">Sección</th>
                      <th scope="col">Cupos</th>
                      <th scope="col">Inscritos</th>
                      <th scope="col">Profesores</th>
                      <th scope="col">Horario</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="s in sections" :key="s.section">
                      <th><input class="form-check-input" type="radio" :name="type" :value="s" v-model="this.subject_modal.selected[type]"></th>
                      <th>{{ s.section }}</th>
                      <th>{{ s.spaces }}</th>
                      <th>{{ s.enrolled }}</th>
                      <th><table v-if="s.teachers.length > 0">
                      <tbody>
                        <tr v-for="(teacher,index) in s.teachers" :key="index"><th><small>{{ teacher }}</small></th></tr>
                      </tbody>
                    </table><div v-else>-</div></th>
                      <th>
                        <span v-for="sch in s.schedule" :key="sch.display" :class="this.schedule[sch['day']][sch['hour']].length > 0 ? 'text-danger': ''">{{ sch.display }}</span>
                      </th>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            <button type="button" class="btn btn-primary" @click="handleModalAddToSchedule()">Agregar</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// @ is an alias to /src
import { db } from '@/firebase'
import Schedule from '@/components/Schedule'
import {Modal} from 'bootstrap'
import { collection, query, getDocs, doc, getDoc,where} from "firebase/firestore";
var colors = [ "#3B7682", "#686868", "#6D255F", "#8E4A17", "#11077D",
  "#BB1F3C", "#40A443", "#795943", "#9F2020", "#63078A"]
export default {
  name: 'Home',
  components: {
    Schedule
  },
  data() {
    return {
      section_types: {'T': 'Teoría','L': 'Laboratorio','E': 'Ejercicios'},
      hours: {'1': '8:00-9:30','2': '9:40-11:10','3': '11:20-12:50','4': '13:50-15:20','5':'15:30-17:00','6': '17:10-18:40','7': '18:45-20:10','8': '20:10-21:35','9': '21:35-23:00'},
      enable_program_select: false,
      schools: [],
      programs: [],
      period: '',
      id_school: '',
      id_program: '',
      semester: '',
      subjects: {},
      subjects_added: {},
      semester_schedule: {},
      busy: {},
      pages: 0,
      actual_page: 1,
      subject_modal: {},
      s_modal: null,
      schedule: {
        L:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        },
        M:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        },
        W:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        },
        J:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        },
        V:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        },
        S:{
          1:[],
          2:[],
          3:[],
          4:[],
          5:[],
          6:[],
          7:[],
          8:[],
          9:[]
        }
      }
    }
  },
  methods: {
    handleSelectSchool: async function(){
      this.id_program = '';
      this.semester = '';
      this.programs = [];
      this.subjects = {};
      this.pages = 0;
      console.log(this.id_school)
      if(this.id_school != ''){
        const q = query(collection(db, "schools",this.id_school,"programs"),where("hidden","==",false));
        const querySnapshot = await getDocs(q);
        querySnapshot.forEach((doc) => {
          var new_program = doc.data()
          new_program.id = doc.id
          this.programs.push(new_program)
        });
      }
      
    },
    handleSelectProgram: async function(){
      this.subjects = {};
      this.semesters = [];
      this.semester = '';
      this.pages = 0;
      if(this.id_program != ''){
        const docRef = doc(db, "schedules",this.id_school+'_'+this.id_program+'_'+'2022-01');
        const docSnap = await getDoc(docRef);
        if (docSnap.exists()) {
          this.semester_schedule = docSnap.data().schedule;
        } else {
          console.log("Programa no encontrado")
        }
      }
    },
    handleSelectSemester: async function(){
      this.subjects = {};
      this.pages = 0;
      if(this.semester != ''){
        var page = 0;
        var keys = Object.keys(this.semester_schedule[this.semester]);
        keys.sort();
        for (let index = 0; index < keys.length; index++) {
          if(index % 15 == 0){
            page++;
            this.subjects[page] = {}
          }
          this.subjects[page][keys[index]] = this.semester_schedule[this.semester][keys[index]];
        }
        this.pages = page;
      }
      console.log(this.subjects)
      
    },
    handleAddSubjectToSchedule: function(subject){
      var sb;
      if(subject.unique){
        sb = JSON.parse(JSON.stringify(subject.sections[subject.display_types][0]));
        sb['name'] = subject.name;
        sb['code'] = subject.code;
        sb['type'] = subject.display_types;
        this.addSectionToSchedule(sb);
      }
      else{
        this.subject_modal = JSON.parse(JSON.stringify(subject));
        Object.keys(this.subject_modal.sections).forEach((type) => this.subject_modal.sections[type].sort((a,b)=> (a.section > b.section ? 1 : -1)));
        this.subject_modal['selected'] = Object.fromEntries(Object.entries(this.subject_modal.sections).map(([k, v]) => [k, v[0]]));
        console.log(this.subject_modal['selected'])
        this.s_modal.show();
      }
    },
    addSectionToSchedule: function(subject){
      var key = subject.code+'.'+subject.type;
      if(this.subjects_added[key] !== undefined){
        this.handleDeleteSubjectFromSchedule(key)
      }
      this.subjects_added[key] = JSON.parse(JSON.stringify(subject));
      var color_index = Math.floor( Math.random()*colors.length );
      var color = colors[color_index];
      colors.splice(color_index,1);
      this.subjects_added[key].color = color;
      subject.schedule.forEach((d) => {
        this.schedule[d['day']][d['hour']].push({code: subject.code,section:subject.section,type:subject.type,name:subject.name,color: color,classroom: d['classroom']})
      });
    },
    handleDeleteSubjectFromSchedule: function(key){
      this.subjects_added[key].schedule.forEach((d) => {
        for( var i = 0; i < this.schedule[d['day']][d['hour']].length; i++){
          if( this.schedule[d['day']][d['hour']][i].code == this.subjects_added[key].code && this.schedule[d['day']][d['hour']][i].section == this.subjects_added[key].section && this.schedule[d['day']][d['hour']][i].type == this.subjects_added[key].type){
            this.schedule[d['day']][d['hour']].splice(i,1);
            i--;
          }
        }
      });
      colors.push(this.subjects_added[key].color);
      delete this.subjects_added[key];
    },
    handleDeleteSchedule: function(){
      Object.keys(this.subjects_added).forEach( (key) => {
        this.handleDeleteSubjectFromSchedule(key);
      })
    },
    makeBusy: function(day,hour){
      if( this.busy[day+hour] == undefined){
        this.busy[day+hour] = true;
      }
      else{
        delete this.busy[day+hour];
      }
      
    },
    handleModalAddToSchedule: function(){
      Object.keys(this.subject_modal.selected).forEach(function(type){
        var sb = JSON.parse(JSON.stringify(this.subject_modal.selected[type]));
        sb.name = this.subject_modal.name;
        sb.code = this.subject_modal.code;
        sb.type = type;
        this.addSectionToSchedule(sb);
      },this);
      this.s_modal.hide();

    },
    isAlreadyinSchedule(subject){
      var out = true;
      Object.keys(subject.sections).forEach(function(a){
        out = out && (this.subjects_added[subject.code+'.'+a] != undefined);
      },this);
      return out;
    },
    isFree(section){
      var out = true;
      section.schedule.forEach(function (s){
        out = out && this.schedule[s['day']][s['hour']].length == 0;
      },this);
      return out;
    }
  },
  async mounted(){
    const q = query(collection(db, "schools"));
    const querySnapshot = await getDocs(q);
    querySnapshot.forEach((doc) => {
      var new_school = doc.data()
      new_school.id = doc.id
      this.schools.push(new_school)
    });
    this.s_modal = new Modal(document.getElementById('subject_modal'));
  }
}
</script>
<style scoped>
table{
  font-size: 0.9em!important;
}


</style>