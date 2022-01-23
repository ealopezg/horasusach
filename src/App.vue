<template>
  <div id="nav">
    <h3>📆 Horas USACH</h3>
  </div>
  <router-view/>
  <div class="container">
    <footer class="py-3 my-4 border-top">
      <p class="text-center text-muted">Creado por 🚀 <a href="https://github.com/ealopezg">Esteban López</a> - 
    Información extraida desde <a href="https://registro.usach.cl/">Registro usach</a> -
    <small>Puede que la información no esté actualizada</small></p>
    </footer>
  </div>
</template>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}

@import'~bootstrap/dist/css/bootstrap.css'
</style>
