<template>
  <span class="badge bg-secondary" v-if="code" data-bs-toggle="tooltip" data-bs-placement="top" :title="classroom ? name+'('+classroom+')' : (name ? name : '')" :style="'background-color:'+color+'!important'" ref="info">{{ code ?  code+'-'+type+'-'+section : '' }}</span>
</template>

<script>
import { Tooltip } from "bootstrap";

export default {
    name: "Schedule",
    props:{
        code: String,
        name: String,
        section: String,
        type: String,
        color: String,
        classroom: String
    },
    mounted(){
        new Tooltip(this.$refs.info)
    }
}
</script>