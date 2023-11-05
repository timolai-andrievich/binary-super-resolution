<script setup lang="ts">
import { onMounted, ref } from "vue";
const fileInput = ref(null);
const img = ref("");
let loading = false;

function submit() {
  let file = fileInput.value.files[0];
  let reader = new FileReader();
  if (file === undefined) {
    return
  }
  reader.readAsDataURL(file);
  reader.onload = e => processImage(e.target.result)
}

async function processImage(image) {
  loading = true;
  let response = await fetch('/upscale', { method: "POST", mode: "no-cors", body: JSON.stringify({ image: image }) })
  let json = await response.json()
  img.value = json.image
  loading = false;
}

</script>

<template>
  <div class="container">
    <div class="inputs">
      <input id="upload-file" type="file" accept=".png,.jpg" ref="fileInput" />
      <button @click="submit">Submit</button>
    </div>
    <div>
      <img :src="img" />
    </div>
  </div>
</template>

<style>
.container {
  display: flex;
  flex-direction: column;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
