<script setup lang="ts">
import { onMounted, ref } from "vue"
const fileInput = ref(null)
const sourceImg = ref(null)
const upscaledImg = ref(null)
let loading = ref(false)

function submit() {
  let file = fileInput.value.files[0];
  let reader = new FileReader();
  if (file === undefined) {
    return;
  }
  reader.readAsDataURL(file);
  reader.onload = (e) => processImage(e.target.result);
}

async function processImage(image) {
  loading.value = true
  upscaledImg.value.src = image
  sourceImg.value.src = image
  let response = await fetch("/upscale", {
    method: "POST",
    mode: "no-cors",
    body: JSON.stringify({ image: image }),
  });
  let json = await response.json();
  upscaledImg.value.src = json.image;
  loading.value = false
}
</script>

<template>
  <div class="container">
    <div class="inputs">
      <input id="upload-file" type="file" accept=".png,.jpg" ref="fileInput" />
      <button @click="submit">Submit</button>
    </div>
    <div class="images">
      <img ref="sourceImg">
      <div class="upscaled-container">
        <div :class="['upscaled-overlay', { hidden: !loading }]">
          <p>Upscaling</p>
          <div class="la-ball-clip-rotate-multiple">
            <div></div>
            <div></div>
          </div>
        </div>
        <img ref="upscaledImg">
      </div>
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

.images {
  display: flex;
  flex-direction: row;
  width: 100%;
  justify-content: center;
}

.upscaled-container {
  position: relative;
}

.upscaled-overlay {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  background-color: rgba(255, 255, 255, .8);
}

.upscaled-overlay.hidden {
  display: none;
}
</style>
