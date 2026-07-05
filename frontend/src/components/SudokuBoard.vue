<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  grid: { type: Array, required: true },
  initialGrid: { type: Array, required: true },
  solvedCells: { type: Set, default: () => new Set() },
  size: { type: Number, required: true },
  blockRows: { type: Number, default: 3 },
  blockCols: { type: Number, default: 3 },
  validValues: { type: Array, default: () => [] },
  disabled: { type: Boolean, default: false },
  readonly: { type: Boolean, default: false },
  title: { type: String, default: '' },
  compact: { type: Boolean, default: false },
})

const emit = defineEmits(['update-cell'])

const focusedCell = ref(null)

const cellSize = computed(() => {
  if (props.compact) {
    if (props.size <= 9) return '2rem'
    if (props.size <= 12) return '1.5rem'
    return '1.1rem'
  }
  if (props.size <= 9) return '2.5rem'
  if (props.size <= 12) return '1.85rem'
  return '1.35rem'
})

const fontSize = computed(() => {
  if (props.compact) {
    if (props.size <= 9) return '1rem'
    if (props.size <= 12) return '0.8rem'
    return '0.65rem'
  }
  if (props.size <= 9) return '1.25rem'
  if (props.size <= 12) return '0.95rem'
  return '0.75rem'
})

const symbolHint = computed(() => {
  if (props.size === 12) return '1–9, A–C'
  if (props.size === 16) return '1–9, A–G'
  return '1–9'
})

function isGiven(row, col) {
  if (props.readonly) return Boolean(props.grid[row]?.[col])
  return Boolean(props.initialGrid[row]?.[col])
}

function isSolved(row, col) {
  return props.solvedCells.has(`${row},${col}`)
}

function cellClass(row, col) {
  const classes = ['cell']
  if (isGiven(row, col)) classes.push('cell-given')
  if (isSolved(row, col)) classes.push('cell-solved')
  if (focusedCell.value === `${row},${col}`) classes.push('cell-focused')
  if ((row + 1) % props.blockRows === 0 && row < props.size - 1) classes.push('border-bottom-thick')
  if ((col + 1) % props.blockCols === 0 && col < props.size - 1) classes.push('border-right-thick')
  return classes
}

function handleInput(row, col, event) {
  const raw = event.target.value.slice(-1).toUpperCase()
  emit('update-cell', { row, col, value: raw })
  event.target.value = props.grid[row][col]
}

function handleKeydown(row, col, event) {
  if (event.key === 'Backspace' || event.key === 'Delete') {
    event.preventDefault()
    emit('update-cell', { row, col, value: '' })
    return
  }
  if (event.key === 'ArrowUp' && row > 0) focusCell(row - 1, col)
  if (event.key === 'ArrowDown' && row < props.size - 1) focusCell(row + 1, col)
  if (event.key === 'ArrowLeft' && col > 0) focusCell(row, col - 1)
  if (event.key === 'ArrowRight' && col < props.size - 1) focusCell(row, col + 1)
}

function focusCell(row, col) {
  const el = document.getElementById(`cell-${row}-${col}`)
  el?.focus()
}

watch(
  () => props.size,
  () => {
    focusedCell.value = null
  }
)
</script>

<template>
  <div class="board-card card" :class="{ compact: compact }">
    <div class="board-header">
      <div>
        <p class="board-label">{{ title || `Tablero ${size}×${size}` }}</p>
        <p v-if="!readonly" class="board-hint">Edita las celdas vacías · Usa {{ symbolHint }}</p>
      </div>
      <div v-if="!readonly" class="legend">
        <span class="legend-item"><span class="swatch swatch-given"></span> Dado</span>
        <span class="legend-item"><span class="swatch swatch-solved"></span> Resuelto</span>
      </div>
    </div>

    <div
      class="board"
      :style="{ '--cell-size': cellSize, '--cell-font': fontSize, gridTemplateColumns: `repeat(${size}, var(--cell-size))` }"
      role="grid"
      :aria-label="`Sudoku ${size} por ${size}`"
    >
      <template v-for="(row, r) in grid" :key="r">
        <div
          v-for="(cell, c) in row"
          :key="`${r}-${c}`"
          role="gridcell"
          :class="cellClass(r, c)"
        >
          <input
            v-if="!readonly && !isGiven(r, c)"
            :id="`cell-${r}-${c}`"
            type="text"
            inputmode="text"
            maxlength="1"
            class="cell-input"
            :value="cell"
            :disabled="disabled"
            :aria-label="`Celda fila ${r + 1} columna ${c + 1}`"
            @input="handleInput(r, c, $event)"
            @keydown="handleKeydown(r, c, $event)"
            @focus="focusedCell = `${r},${c}`"
            @blur="focusedCell = null"
          />
          <span v-else class="cell-given-value" :class="{ 'cell-filled': readonly && cell }">{{ cell }}</span>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.card {
  background: var(--color-white);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  padding: 1.5rem;
  border: 1px solid var(--color-neutral-light);
  width: 100%;
  max-width: fit-content;
}

.card.compact {
  padding: 1rem;
}

.board-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.board-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-neutral);
}

.board-hint {
  font-size: 0.8125rem;
  color: var(--color-neutral);
  margin-top: 0.25rem;
}

.legend {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--color-neutral);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.swatch {
  width: 14px;
  height: 14px;
  border-radius: 3px;
  border: 1px solid var(--color-neutral-light);
}

.swatch-given {
  background: var(--color-given);
}

.swatch-solved {
  background: var(--color-solved);
}

.board {
  display: grid;
  border: 2.5px solid var(--color-primary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  width: fit-content;
  margin: 0 auto;
}

.cell {
  width: var(--cell-size);
  height: var(--cell-size);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #ccc;
  background: var(--color-white);
  position: relative;
}

.border-bottom-thick {
  border-bottom: 2.5px solid var(--color-primary);
}

.border-right-thick {
  border-right: 2.5px solid var(--color-primary);
}

.cell-given {
  background: var(--color-given);
}

.cell-solved {
  background: var(--color-solved);
}

.cell-solved .cell-given-value {
  color: var(--color-primary);
  font-weight: 600;
}

.cell-focused {
  outline: 2px solid var(--color-primary-light);
  outline-offset: -2px;
  z-index: 1;
}

.cell-given-value {
  font-family: var(--font-mono);
  font-size: var(--cell-font);
  font-weight: 600;
  color: var(--color-primary);
  user-select: none;
}

.cell-input {
  width: 100%;
  height: 100%;
  border: none;
  background: transparent;
  text-align: center;
  font-family: var(--font-mono);
  font-size: var(--cell-font);
  font-weight: 500;
  color: #333;
  outline: none;
  padding: 0;
}

.cell-given-value.cell-filled {
  color: var(--color-success);
}

.cell-input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 640px) {
  .card {
    padding: 1rem;
    max-width: 100%;
    overflow-x: auto;
  }
}
</style>
