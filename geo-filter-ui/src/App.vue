<template>
  <MyFile />
</template>

<script>
import MyFile from "./components/MyFile.vue";

export default {
  name: "App",
  components: {
    MyFile,
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
