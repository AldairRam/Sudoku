<script setup>

import { computed } from 'vue'



const props = defineProps({

  metrics: {

    type: Object,

    default: () => ({

      executionTime: null,

      nodesExplored: null,

      backtracks: null,

      combinationsTried: null,

      memoryPeakKb: null,

      algorithm: '—',

      algorithmKey: null,

    }),

  },

  comparisonMetrics: { type: Object, default: null },

  algorithmComparison: { type: Object, default: null },

  benchmarkResult: { type: Object, default: null },

  exportMessage: { type: String, default: '' },

  status: { type: String, default: 'idle' },

  isSolving: { type: Boolean, default: false },

  playTime: { type: String, default: '00:00' },

  playTimeRunning: { type: Boolean, default: false },

})



const statusLabel = computed(() => {

  if (props.isSolving) return 'Resolviendo…'

  const map = {

    idle: 'En espera',

    playing: 'En juego',

    loaded: 'Tablero listo',

    solving: 'Resolviendo…',

    solved: 'Solución encontrada',

    error: 'Error',

  }

  return map[props.status] ?? 'En espera'

})



const progressPercent = computed(() => {

  if (props.isSolving) return 65

  if (props.status === 'solved') return 100

  if (props.status === 'loaded' || props.status === 'playing') return 30

  return 0

})



const algoKey = computed(() => props.metrics.algorithmKey)

const isBruteForce = computed(() => algoKey.value === 'brute_force')

const isMrv = computed(() => algoKey.value === 'mrv')



const algoBadgeLabel = computed(() => {

  if (isBruteForce.value) return 'Fuerza Bruta'

  if (isMrv.value) return 'Backtracking + MRV'

  return 'Backtracking'

})



function formatTime(ms) {

  if (ms === null || ms === undefined) return '—'

  if (ms < 1) return `${(ms * 1000).toFixed(0)} µs`

  if (ms < 1000) return `${Number(ms).toFixed(2)} ms`

  return `${(ms / 1000).toFixed(3)} s`

}



function formatNumber(n) {

  if (n === null || n === undefined) return '—'

  return Number(n).toLocaleString('es-ES')

}



function formatMemory(kb) {

  if (kb === null || kb === undefined) return '—'

  if (kb < 1024) return `${Number(kb).toFixed(1)} KB`

  return `${(kb / 1024).toFixed(2)} MB`

}



function speedupFactor(current, previous) {

  if (!current?.executionTime || !previous?.executionTime) return null

  const ratio = previous.executionTime / current.executionTime

  if (ratio >= 1) return `${ratio.toFixed(1)}× más rápido`

  return `${(1 / ratio).toFixed(1)}× más lento`

}

</script>



<template>

  <div class="metrics-panel">

    <div class="card card-timer" :class="{ running: playTimeRunning }">

      <p class="card-label">Tiempo de juego</p>

      <p class="timer-display">{{ playTime }}</p>

      <p class="timer-status">

        {{ playTimeRunning ? 'Contando…' : status === 'solved' ? 'Completado' : 'En pausa' }}

      </p>

    </div>



    <div class="card card-analysis">

      <p class="card-label">Análisis experimental</p>

      <h2 class="card-status">{{ statusLabel }}</h2>



      <div class="progress-bar">

        <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>

      </div>



      <div class="metrics-grid">

        <div class="metric">

          <span class="metric-icon" aria-hidden="true">

            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">

              <circle cx="9" cy="9" r="7" stroke="currentColor" stroke-width="1.5" />

              <path d="M9 5v4l2.5 2.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />

            </svg>

          </span>

          <div>

            <p class="metric-label">Tiempo de ejecución</p>

            <p class="metric-value">{{ formatTime(metrics.executionTime) }}</p>

          </div>

        </div>



        <div class="metric">

          <span class="metric-icon" aria-hidden="true">

            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">

              <circle cx="4" cy="9" r="2" fill="currentColor" />

              <circle cx="9" cy="4" r="2" fill="currentColor" />

              <circle cx="14" cy="9" r="2" fill="currentColor" />

              <circle cx="9" cy="14" r="2" fill="currentColor" />

            </svg>

          </span>

          <div>

            <p class="metric-label">Nodos explorados</p>

            <p class="metric-value">{{ formatNumber(metrics.nodesExplored) }}</p>

          </div>

        </div>



        <div class="metric">

          <span class="metric-icon" aria-hidden="true">

            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">

              <path d="M4 9h10M9 4l5 5-5 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />

            </svg>

          </span>

          <div>

            <p class="metric-label">{{ isBruteForce ? 'Combinaciones probadas' : 'Backtracks' }}</p>

            <p class="metric-value">

              {{ formatNumber(isBruteForce ? metrics.combinationsTried : metrics.backtracks) }}

            </p>

          </div>

        </div>



        <div class="metric">

          <span class="metric-icon" aria-hidden="true">

            <svg width="18" height="18" viewBox="0 0 18 18" fill="none">

              <rect x="3" y="5" width="12" height="10" rx="1" stroke="currentColor" stroke-width="1.5" />

              <path d="M6 5V4a3 3 0 016 0v1" stroke="currentColor" stroke-width="1.5" />

            </svg>

          </span>

          <div>

            <p class="metric-label">Memoria pico</p>

            <p class="metric-value">{{ formatMemory(metrics.memoryPeakKb) }}</p>

          </div>

        </div>

      </div>



      <div v-if="comparisonMetrics" class="comparison">

        <p class="comparison-title">Comparación con ejecución anterior</p>

        <div class="comparison-row">

          <span class="comparison-algo">{{ comparisonMetrics.algorithm }}</span>

          <span class="comparison-time">{{ formatTime(comparisonMetrics.executionTime) }}</span>

        </div>

        <div class="comparison-row">

          <span class="comparison-algo">{{ metrics.algorithm }}</span>

          <span class="comparison-time">{{ formatTime(metrics.executionTime) }}</span>

        </div>

        <p v-if="speedupFactor(metrics, comparisonMetrics)" class="comparison-result">

          {{ metrics.algorithm }}: {{ speedupFactor(metrics, comparisonMetrics) }}

        </p>

      </div>



      <div v-if="algorithmComparison?.comparison?.length" class="comparison">

        <p class="comparison-title">Comparación entre algoritmos</p>

        <div

          v-for="row in algorithmComparison.comparison"

          :key="row.algorithm_key"

          class="comparison-row"

        >

          <span class="comparison-algo">{{ row.algorithm }}</span>

          <span class="comparison-time">

            {{ row.skipped ? 'Omitido' : formatTime(row.execution_time_ms) }}

          </span>

        </div>

        <p v-if="algorithmComparison.fastest_time_ms" class="comparison-result">

          Más rápido: {{ formatTime(algorithmComparison.fastest_time_ms) }}

        </p>

      </div>



      <div v-if="benchmarkResult" class="comparison">

        <p class="comparison-title">Benchmark del dataset</p>

        <div class="comparison-row">

          <span class="comparison-algo">Tableros evaluados</span>

          <span class="comparison-time">{{ benchmarkResult.total_boards }}</span>

        </div>

        <div class="comparison-row">

          <span class="comparison-algo">Resueltos correctamente</span>

          <span class="comparison-time">{{ benchmarkResult.solved_correctly }}</span>

        </div>

        <p class="comparison-result">

          Éxito: {{ benchmarkResult.success_rate_percent }}%

        </p>

      </div>



      <p v-if="exportMessage" class="export-msg">{{ exportMessage }}</p>

    </div>



    <div

      class="card card-algorithm"

      :class="{ 'card-brute': isBruteForce, 'card-mrv': isMrv }"

    >

      <p class="algo-label">Algoritmo utilizado</p>

      <p class="algo-value">{{ metrics.algorithm }}</p>

      <p v-if="isBruteForce" class="algo-note">

        Prueba todas las combinaciones sin poda anticipada. Costo computacional elevado.

      </p>

      <p v-else-if="isMrv" class="algo-note">

        Selecciona la celda con menos valores candidatos (MRV) para reducir la búsqueda.

      </p>

      <p v-else class="algo-note">

        Descarta ramas inválidas antes de explorarlas, reduciendo nodos y tiempo.

      </p>

      <div class="algo-badge">

        <span class="badge-dot" :class="{ active: isSolving || status === 'solved' }"></span>

        {{ algoBadgeLabel }}

      </div>

    </div>

  </div>

</template>



<style scoped>

.metrics-panel {

  display: flex;

  flex-direction: column;

  gap: 1rem;

}



.card {

  background: var(--color-white);

  border-radius: var(--radius-md);

  box-shadow: var(--shadow-md);

  border: 1px solid var(--color-neutral-light);

  padding: 1.25rem;

}



.card-timer {

  text-align: center;

  border: 2px solid var(--color-neutral-light);

  transition: border-color var(--transition), background var(--transition);

}



.card-timer.running {

  border-color: var(--color-primary);

  background: var(--color-primary-soft);

}



.timer-display {

  font-family: var(--font-mono);

  font-size: 2.75rem;

  font-weight: 700;

  color: var(--color-primary);

  letter-spacing: 0.05em;

  margin: 0.25rem 0;

  line-height: 1.1;

}



.timer-status {

  font-size: 0.75rem;

  color: var(--color-neutral);

}



.card-label,

.algo-label {

  font-size: 0.6875rem;

  font-weight: 600;

  text-transform: uppercase;

  letter-spacing: 0.08em;

  color: var(--color-neutral);

  margin-bottom: 0.5rem;

}



.card-status {

  font-size: 1.125rem;

  font-weight: 700;

  color: var(--color-primary);

  margin-bottom: 1rem;

}



.progress-bar {

  height: 6px;

  background: var(--color-neutral-light);

  border-radius: 99px;

  overflow: hidden;

  margin-bottom: 1.25rem;

}



.progress-fill {

  height: 100%;

  background: var(--color-primary);

  border-radius: 99px;

  transition: width 0.4s ease;

}



.metrics-grid {

  display: flex;

  flex-direction: column;

  gap: 1rem;

}



.metric {

  display: flex;

  align-items: flex-start;

  gap: 0.75rem;

}



.metric-icon {

  color: var(--color-primary);

  flex-shrink: 0;

  margin-top: 0.125rem;

}



.metric-label {

  font-size: 0.75rem;

  color: var(--color-neutral);

  margin-bottom: 0.125rem;

}



.metric-value {

  font-family: var(--font-mono);

  font-size: 1.125rem;

  font-weight: 600;

  color: #1a1a2e;

}



.comparison {

  margin-top: 1.25rem;

  padding-top: 1rem;

  border-top: 1px dashed var(--color-neutral-light);

}



.comparison-title {

  font-size: 0.6875rem;

  font-weight: 600;

  text-transform: uppercase;

  letter-spacing: 0.06em;

  color: var(--color-neutral);

  margin-bottom: 0.625rem;

}



.comparison-row {

  display: flex;

  justify-content: space-between;

  gap: 0.5rem;

  font-size: 0.8125rem;

  margin-bottom: 0.375rem;

}



.comparison-algo {

  color: #333;

  flex: 1;

  overflow: hidden;

  text-overflow: ellipsis;

  white-space: nowrap;

}



.comparison-time {

  font-family: var(--font-mono);

  font-weight: 600;

  color: var(--color-primary);

}



.comparison-result {

  font-size: 0.8125rem;

  font-weight: 600;

  color: var(--color-success);

  margin-top: 0.5rem;

}



.export-msg {

  margin-top: 1rem;

  font-size: 0.8125rem;

  color: var(--color-success);

}



.card-algorithm {

  background: var(--color-primary);

  color: var(--color-white);

  border-color: var(--color-primary);

}



.card-brute {

  background: #4a148c;

  border-color: #4a148c;

}



.card-mrv {

  background: #00695c;

  border-color: #00695c;

}



.algo-label {

  color: rgba(255, 255, 255, 0.7);

}



.algo-value {

  font-size: 0.9375rem;

  font-weight: 600;

  line-height: 1.4;

  margin-bottom: 0.5rem;

}



.algo-note {

  font-size: 0.75rem;

  line-height: 1.4;

  opacity: 0.85;

  margin-bottom: 0.75rem;

}



.algo-badge {

  display: inline-flex;

  align-items: center;

  gap: 0.5rem;

  font-size: 0.75rem;

  font-family: var(--font-mono);

  background: rgba(255, 255, 255, 0.15);

  padding: 0.375rem 0.75rem;

  border-radius: 99px;

}



.badge-dot {

  width: 6px;

  height: 6px;

  border-radius: 50%;

  background: rgba(255, 255, 255, 0.4);

}



.badge-dot.active {

  background: #69f0ae;

  box-shadow: 0 0 6px #69f0ae;

}

</style>

