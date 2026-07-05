<script setup>
import { computed } from 'vue'

const props = defineProps({
  boardSize: { type: Number, required: true },
  selectedDataset: { type: String, default: '' },
  selectedAlgorithm: { type: String, default: 'backtracking' },
  datasets: { type: Array, default: () => [] },
  isBusy: { type: Boolean, default: false },
  bruteForceAvailable: { type: Boolean, default: true },
  gephiAvailable: { type: Boolean, default: true },
})

const emit = defineEmits([
  'update:boardSize',
  'update:selectedDataset',
  'update:selectedAlgorithm',
  'load',
  'solve',
  'clear',
  'generate',
  'compare',
  'benchmark',
  'export-metrics',
  'export-gephi',
])

const localSize = computed({
  get: () => props.boardSize,
  set: (v) => emit('update:boardSize', Number(v)),
})

const localDataset = computed({
  get: () => props.selectedDataset,
  set: (v) => emit('update:selectedDataset', v),
})

const localAlgorithm = computed({
  get: () => props.selectedAlgorithm,
  set: (v) => emit('update:selectedAlgorithm', v),
})
</script>

<template>
  <div class="control-panel card">
    <h2 class="card-title">Controles</h2>

    <div class="field">
      <label class="field-label" for="board-size">Tamaño del tablero</label>
      <div class="size-options">
        <button
          type="button"
          class="size-btn"
          :class="{ active: localSize === 9 }"
          :disabled="isBusy"
          @click="localSize = 9"
        >
          <span class="size-label">Sudoku 9×9</span>
          <span class="size-desc">Clásico · 3×3 bloques</span>
        </button>
        <button
          type="button"
          class="size-btn"
          :class="{ active: localSize === 12 }"
          :disabled="isBusy"
          @click="localSize = 12"
        >
          <span class="size-label">Sudoku 12×12</span>
          <span class="size-desc">Extendido · 3×4 bloques</span>
        </button>
        <button
          type="button"
          class="size-btn"
          :class="{ active: localSize === 16 }"
          :disabled="isBusy"
          @click="localSize = 16"
        >
          <span class="size-label">Sudoku 16×16</span>
          <span class="size-desc">Hexadoku · 4×4 bloques</span>
        </button>
      </div>
    </div>

    <div class="field">
      <label class="field-label" for="dataset">Tablero disponible</label>
      <select
        id="dataset"
        v-model="localDataset"
        class="select"
        :disabled="isBusy || !datasets.length"
      >
        <option v-if="!datasets.length" value="" disabled>Sin datasets disponibles</option>
        <option v-for="ds in datasets" :key="ds.id" :value="ds.id">
          {{ ds.name ?? ds.id }}
        </option>
      </select>
    </div>

    <button type="button" class="btn btn-secondary" :disabled="isBusy || !localDataset" @click="emit('load')">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
        <path d="M8 2v8M8 10l3-3M8 10L5 7" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        <path d="M3 12h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
      </svg>
      Cargar Sudoku
    </button>

    <hr class="divider" />

    <div class="field">
      <label class="field-label" for="algorithm">Algoritmo de resolución</label>
      <div class="algo-options">
        <button
          type="button"
          class="algo-btn"
          :class="{ active: localAlgorithm === 'backtracking' }"
          :disabled="isBusy"
          @click="localAlgorithm = 'backtracking'"
        >
          <span class="algo-name">Backtracking</span>
          <span class="algo-desc">Con poda por restricciones</span>
        </button>
        <button
          type="button"
          class="algo-btn"
          :class="{ active: localAlgorithm === 'mrv' }"
          :disabled="isBusy"
          @click="localAlgorithm = 'mrv'"
        >
          <span class="algo-name">Backtracking + MRV</span>
          <span class="algo-desc">Heurística voraz · Minimum Remaining Values</span>
        </button>
        <button
          type="button"
          class="algo-btn"
          :class="{ active: localAlgorithm === 'brute_force', disabled: !bruteForceAvailable }"
          :disabled="isBusy || !bruteForceAvailable"
          @click="localAlgorithm = 'brute_force'"
        >
          <span class="algo-name">Fuerza Bruta</span>
          <span class="algo-desc">Comparación experimental (9×9)</span>
        </button>
      </div>
      <p v-if="!bruteForceAvailable" class="field-hint">
        Fuerza Bruta solo disponible en 9×9 por su alto costo computacional.
      </p>
      <p v-else-if="localAlgorithm === 'brute_force'" class="field-hint field-hint-warn">
        Usa tableros fáciles (p. ej. SDK9_01) para comparar sin esperas largas.
      </p>
    </div>

    <div class="actions">
      <button type="button" class="btn btn-primary" :disabled="isBusy" @click="emit('solve')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M9 2L4 9h4l-1 5 5-7H8l1-5z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round" />
        </svg>
        {{ isBusy ? 'Procesando…' : 'Resolver' }}
      </button>

      <button type="button" class="btn btn-outline" :disabled="isBusy" @click="emit('clear')">
        Limpiar
      </button>

      <button type="button" class="btn btn-outline" :disabled="isBusy" @click="emit('generate')">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
        </svg>
        Generar otro Sudoku
      </button>
    </div>

    <hr class="divider" />

    <div class="field">
      <label class="field-label">Análisis y exportación</label>
      <div class="actions">
        <button type="button" class="btn btn-secondary" :disabled="isBusy" @click="emit('compare')">
          Comparar algoritmos
        </button>
        <button type="button" class="btn btn-outline" :disabled="isBusy" @click="emit('benchmark')">
          Benchmark del dataset
        </button>
        <button type="button" class="btn btn-outline" :disabled="isBusy" @click="emit('export-metrics')">
          Exportar métricas (Excel)
        </button>
        <button
          type="button"
          class="btn btn-outline"
          :disabled="isBusy || !gephiAvailable"
          @click="emit('export-gephi')"
        >
          Exportar grafo Gephi (CSV)
        </button>
      </div>
      <p v-if="!gephiAvailable" class="field-hint">
        La exportación del grafo de 81 nodos solo está disponible en 9×9.
      </p>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--color-white);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
  padding: 1.25rem;
  border: 1px solid var(--color-neutral-light);
}

.card-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-neutral);
  margin-bottom: 1.25rem;
}

.field {
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: #333;
  margin-bottom: 0.5rem;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--color-neutral);
  margin-top: 0.5rem;
  line-height: 1.4;
}

.field-hint-warn {
  color: var(--color-tertiary);
}

.size-options,
.algo-options {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.size-btn,
.algo-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  border: 2px solid var(--color-neutral-light);
  background: var(--color-secondary);
  transition: all var(--transition);
  text-align: left;
  width: 100%;
}

.size-btn:hover:not(:disabled),
.algo-btn:hover:not(:disabled) {
  border-color: var(--color-primary-light);
}

.size-btn.active,
.algo-btn.active {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
}

.size-btn:disabled,
.algo-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.size-label,
.algo-name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-primary);
}

.size-desc,
.algo-desc {
  font-size: 0.75rem;
  color: var(--color-neutral);
  margin-top: 0.125rem;
}

.select {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-neutral-light);
  border-radius: var(--radius-sm);
  background: var(--color-secondary);
  font-size: 0.875rem;
  color: #333;
  transition: border-color var(--transition);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath d='M3 4.5L6 7.5L9 4.5' stroke='%2377767D' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  padding-right: 2rem;
}

.select:focus {
  outline: none;
  border-color: var(--color-primary);
}

.select:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.divider {
  border: none;
  border-top: 1px solid var(--color-neutral-light);
  margin: 1.25rem 0;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  transition: all var(--transition);
  width: 100%;
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-light);
}

.btn-secondary {
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.btn-secondary:hover:not(:disabled) {
  background: #c5cae9;
}

.btn-outline {
  background: transparent;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
}

.btn-outline:hover:not(:disabled) {
  background: var(--color-primary-soft);
}
</style>
