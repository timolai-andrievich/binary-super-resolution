<script setup lang="ts">
// TODO move hovered lens when approaching the edge of the screen
// TODO multiple scales
// TODO download button
// TODO cancel upscaling button, and cancelling on server error
// TODO error message
import { ref, computed } from "vue"
const fileInput = ref(null)
const sourceImg = ref(null)
const upscaledImg = ref(null)
const hoverTextPos = ref([0, 0])
const sourceCanvas = ref(null)
const upscaledCanvas = ref(null)
const loading = ref(false)
const mouseOnCanvas = ref(false)
const errorMessage = ref(null);
const showHover = computed(() => errorMessage.value === null && !loading.value && mouseOnCanvas.value && upscaledImg && upscaledImg.value && upscaledImg.value.src)

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
  if (!response.ok) {
    errorMessage.value = "Error: Unable to connect to the server. Please check your internet connection and ensure that the server is currently accessible. "
    loading.value = false
    return
  }
  let json = await response.json();
  upscaledImg.value.src = json.image;
  loading.value = false
}

function onHoverOriginal(){
  mouseOnCanvas.value = true
}

function onLeaveOriginal() {
  mouseOnCanvas.value = false
}

function onHoverUpscaled(){
  mouseOnCanvas.value = true
}

function onLeaveUpscaled() {
  mouseOnCanvas.value = false
}

function updateHoverPosition(event: any) {
  if (sourceCanvas.value === null || upscaledCanvas.value === null) {
    return
  }
  let scale = 5
  let rect = sourceImg.value.getBoundingClientRect()
  if (rect.top > event.clientY || rect.bottom < event.clientY || rect.left > event.clientX || rect.right < event.clientX) {
    rect = upscaledImg.value.getBoundingClientRect()
  }
  let rectAspect = rect.width / rect.height
  let imgAspect = sourceImg.value.naturalWidth / sourceImg.value.naturalHeight
  let xPadding = 0
  let yPadding = 0
  if (imgAspect > rectAspect) {
    let height = rect.width / imgAspect
    yPadding = (rect.height - height) / 2
  } else if (imgAspect < rectAspect) {
    let width = rect.height * imgAspect
    xPadding = (rect.width - width) / 2
  }
  let x = (event.clientX - rect.left - xPadding) / (rect.width - xPadding * 2)
  let y = (event.clientY - rect.top - yPadding) / (rect.height - yPadding * 2)

  {
    let ctx = sourceCanvas.value.getContext('2d')
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(scale, scale)
    let dx = -(x * sourceImg.value.naturalWidth - sourceCanvas.value.width / scale / 2)
    let dy = -(y * sourceImg.value.naturalHeight - sourceCanvas.value.height / scale / 2)
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, sourceCanvas.value.width, sourceCanvas.value.height)
    ctx.drawImage(sourceImg.value, dx, dy)
  }
  {
    let ctx = upscaledCanvas.value.getContext('2d')
    ctx.setTransform(1, 0, 0, 1, 0, 0)
    ctx.scale(scale / 2, scale / 2)
    let dx = -(x * upscaledImg.value.naturalWidth - upscaledCanvas.value.width / scale)
    let dy = -(y * upscaledImg.value.naturalHeight - upscaledCanvas.value.width / scale)
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, upscaledCanvas.value.width, upscaledCanvas.value.height)
    ctx.drawImage(upscaledImg.value, dx, dy)
  }
  hoverTextPos.value[1] = event.pageY
  hoverTextPos.value[0] = event.pageX
}

</script>

<template>
  <div class="container">
    <div class="inputs">
      <input id="upload-file" type="file" accept=".png,.jpg" ref="fileInput" style="display: none;"/>
      <button @click="fileInput.click()">Upload</button>
      <button @click="submit">Upscale</button>
    </div>
    <div class="images">
      <div class="original-container">
        <img ref="sourceImg" @mousemove="updateHoverPosition" @mouseover="onHoverOriginal" @mouseleave="onLeaveOriginal">
      </div>
      <div class="upscaled-container">
        <div :class="['upscaled-overlay', { hidden: !loading }]">
          <p>Upscaling</p>
          <div class="la-ball-clip-rotate-multiple">
            <div></div>
            <div></div>
          </div>
        </div>
        <div :class="['upscaled-overlay', { hidden: errorMessage === null }]">
          <p>{{ errorMessage }}</p>
        </div>
        <img ref="upscaledImg" @mousemove="updateHoverPosition" @mouseover="onHoverUpscaled" @mouseleave="onLeaveUpscaled">
      </div>
    </div>
  </div>
  <div class="hover-text" :style="{display: showHover ? 'inline' : 'none', top: `${hoverTextPos[1]}px`, left: `${hoverTextPos[0]}px`}" @mousemove="updateHoverPosition">
    <canvas ref="sourceCanvas" width="100" height="100"></canvas>
    <canvas ref="upscaledCanvas" width="100" height="100"></canvas>
  </div>
</template>

<style>
.inputs > button {
  border-radius: 1rem;
  padding: 0.40rem;
  background-color: white;
  border: .13rem black solid;
  transition: 100ms;
}

.inputs > button:hover {
  background-color: lightgray;
}

.hover-text {
  position: absolute;
  transform: translate(-100%, -100%);
  display: flex;
  flex-direction: row;
}

.hover-text > * {
  flex: 1;
}

html, body {
  height: 100%;
}

.container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.inputs {
  padding: 1rem;
  display: flex;
  flex-direction: row;
  column-gap: 1rem;
  justify-content: center;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  height: 100%;
}

.images {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  justify-content: stretch;
}

.images > * {
  flex: 1;
  display: flex;
}

img {
  flex: 1;
  object-fit:contain;
  max-width: 100%;
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
