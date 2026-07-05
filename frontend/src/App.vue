<script setup>
import { useSudoku } from './composables/useSudoku'
import SudokuBoard from './components/SudokuBoard.vue'
import ControlPanel from './components/ControlPanel.vue'
import MetricsPanel from './components/MetricsPanel.vue'

const {
  boardSize,
  selectedAlgorithm,
  datasets,
  selectedDataset,
  grid,
  initialGrid,
  solvedGrid,
  solvedCells,
  metrics,
  comparisonMetrics,
  algorithmComparison,
  benchmarkResult,
  exportMessage,
  status,
  errorMessage,
  isBusy,
  isSolving,
  bruteForceAvailable,
  gephiAvailable,
  showDualBoards,
  validValues,
  blockRows,
  blockCols,
  loadSelectedSudoku,
  solve,
  clearBoard,
  generateNew,
  updateCell,
  compareAllAlgorithms,
  executeBenchmark,
  downloadMetrics,
  downloadGephiFiles,
  timer,
} = useSudoku()

const emptySet = new Set()
</script>

<template>
  <div class="app">
    <header class="app-header">
      <div class="header-inner">
        <div class="brand">
          <span class="brand-icon" aria-hidden="true">
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect x="2" y="2" width="24" height="24" rx="4" stroke="currentColor" stroke-width="2" />
              <line x1="2" y1="10" x2="26" y2="10" stroke="currentColor" stroke-width="2" />
              <line x1="2" y1="18" x2="26" y2="18" stroke="currentColor" stroke-width="2" />
              <line x1="10" y1="2" x2="10" y2="26" stroke="currentColor" stroke-width="2" />
              <line x1="18" y1="2" x2="18" y2="26" stroke="currentColor" stroke-width="2" />
            </svg>
          </span>
          <h1 class="brand-title">Sistema de Resolución de Sudoku</h1>
        </div>
        <div class="header-status">
          <span class="status-dot" :class="{ active: status !== 'idle' }"></span>
          <span class="status-text">
            {{
              isSolving
                ? 'Resolviendo…'
                : status === 'solved'
                  ? 'Completado'
                  : status === 'loaded' || status === 'playing'
                    ? 'En juego'
                    : 'Listo'
            }}
          </span>
        </div>
      </div>
    </header>

    <main class="app-main">
      <div v-if="errorMessage" class="alert alert-error" role="alert">
        {{ errorMessage }}
      </div>

      <div class="workspace">
        <aside class="sidebar sidebar-left">
          <ControlPanel
            v-model:board-size="boardSize"
            v-model:selected-dataset="selectedDataset"
            v-model:selected-algorithm="selectedAlgorithm"
            :datasets="datasets"
            :is-busy="isBusy"
            :brute-force-available="bruteForceAvailable"
            :gephi-available="gephiAvailable"
            @load="loadSelectedSudoku()"
            @solve="solve()"
            @clear="clearBoard()"
            @generate="generateNew()"
            @compare="compareAllAlgorithms()"
            @benchmark="executeBenchmark()"
            @export-metrics="downloadMetrics('xlsx')"
            @export-gephi="downloadGephiFiles()"
          />
        </aside>

        <section class="board-section" :class="{ dual: showDualBoards }">
          <template v-if="showDualBoards">
            <SudokuBoard
              :grid="initialGrid"
              :initial-grid="initialGrid"
              :solved-cells="emptySet"
              :size="boardSize"
              :block-rows="blockRows"
              :block-cols="blockCols"
              :valid-values="validValues"
              readonly
              compact
              title="Tablero original"
            />
            <SudokuBoard
              :grid="solvedGrid"
              :initial-grid="initialGrid"
              :solved-cells="solvedCells"
              :size="boardSize"
              :block-rows="blockRows"
              :block-cols="blockCols"
              :valid-values="validValues"
              readonly
              compact
              title="Tablero resuelto"
            />
          </template>
          <SudokuBoard
            v-else
            :grid="grid"
            :initial-grid="initialGrid"
            :solved-cells="solvedCells"
            :size="boardSize"
            :block-rows="blockRows"
            :block-cols="blockCols"
            :valid-values="validValues"
            :disabled="isBusy"
            @update-cell="({ row, col, value }) => updateCell(row, col, value)"
          />
        </section>

        <aside class="sidebar sidebar-right">
          <MetricsPanel
            :metrics="metrics"
            :comparison-metrics="comparisonMetrics"
            :algorithm-comparison="algorithmComparison"
            :benchmark-result="benchmarkResult"
            :export-message="exportMessage"
            :status="status"
            :is-solving="isSolving"
            :play-time="timer.formattedTime"
            :play-time-running="timer.isRunning"
          />
        </aside>
      </div>
    </main>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: var(--color-white);
  border-bottom: 1px solid var(--color-neutral-light);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  color: var(--color-primary);
  display: flex;
}

.brand-title {
  font-size: clamp(1.1rem, 2.5vw, 1.35rem);
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.02em;
}

.header-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--color-neutral);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-neutral-light);
  transition: background var(--transition);
}

.status-dot.active {
  background: var(--color-success);
}

.app-main {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem;
}

.alert {
  padding: 0.875rem 1rem;
  border-radius: var(--radius-sm);
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.alert-error {
  background: #ffebee;
  color: var(--color-error);
  border: 1px solid #ffcdd2;
}

.workspace {
  display: grid;
  grid-template-columns: 280px 1fr 280px;
  gap: 1.5rem;
  align-items: start;
}

.sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.board-section {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.board-section.dual {
  flex-direction: row;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
}

@media (max-width: 1100px) {
  .workspace {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto auto;
  }

  .sidebar-left {
    grid-column: 1;
    grid-row: 1;
  }

  .sidebar-right {
    grid-column: 2;
    grid-row: 1;
  }

  .board-section {
    grid-column: 1 / -1;
    grid-row: 2;
  }
}

@media (max-width: 640px) {
  .app-main {
    padding: 1rem;
  }

  .workspace {
    grid-template-columns: 1fr;
  }

  .sidebar-left,
  .sidebar-right,
  .board-section {
    grid-column: 1;
    grid-row: auto;
  }

  .board-section.dual {
    flex-direction: column;
    align-items: center;
  }

  .header-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
