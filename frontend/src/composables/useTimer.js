import { ref, computed, onUnmounted } from 'vue'

export function useTimer() {
  const elapsedMs = ref(0)
  const isRunning = ref(false)
  let intervalId = null
  let startedAt = null

  const formattedTime = computed(() => {
    const totalSec = Math.floor(elapsedMs.value / 1000)
    const h = Math.floor(totalSec / 3600)
    const m = Math.floor((totalSec % 3600) / 60)
    const s = totalSec % 60
    if (h > 0) {
      return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
    }
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  })

  function tick() {
    if (startedAt !== null) {
      elapsedMs.value = Date.now() - startedAt
    }
  }

  function start() {
    if (isRunning.value) return
    startedAt = Date.now() - elapsedMs.value
    isRunning.value = true
    intervalId = setInterval(tick, 100)
  }

  function stop() {
    if (!isRunning.value) return
    tick()
    isRunning.value = false
    clearInterval(intervalId)
    intervalId = null
    startedAt = null
  }

  function reset() {
    stop()
    elapsedMs.value = 0
  }

  onUnmounted(() => {
    if (intervalId) clearInterval(intervalId)
  })

  return { elapsedMs, isRunning, formattedTime, start, stop, reset }
}
