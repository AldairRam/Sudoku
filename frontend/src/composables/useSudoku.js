import { ref, computed, watch } from 'vue'
import {
  fetchDatasets,
  loadSudoku,
  solveSudoku,
  generateSudoku,
  compareAlgorithms,
  runBenchmark,
  exportGraph,
  exportMetrics,
} from '../services/sudokuApi'
import { useTimer } from './useTimer'

const VALUES_9 = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
const VALUES_12 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C']
const VALUES_16 = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

function createEmptyGrid(size) {
  return Array.from({ length: size }, () => Array(size).fill(''))
}

function normalizeCell(value) {
  if (value === null || value === undefined || value === 0 || value === '') return ''
  return String(value).toUpperCase()
}

function normalizeGrid(raw, size) {
  return Array.from({ length: size }, (_, r) =>
    Array.from({ length: size }, (_, c) => normalizeCell(raw?.[r]?.[c] ?? ''))
  )
}

function gridToApi(grid) {
  return grid.map((row) =>
    row.map((cell) => {
      const v = normalizeCell(cell)
      return v === '' ? 0 : v
    })
  )
}

function solvedCellsFromResponse(initial, solution, explicit = []) {
  if (explicit?.length) {
    return new Set(explicit.map(([r, c]) => `${r},${c}`))
  }
  const set = new Set()
  for (let r = 0; r < initial.length; r++) {
    for (let c = 0; c < initial[r].length; c++) {
      if (!initial[r][c] && solution[r]?.[c]) {
        set.add(`${r},${c}`)
      }
    }
  }
  return set
}

function mapMetrics(m, algo) {
  return {
    executionTime: m.execution_time_ms ?? m.executionTime ?? m.time_ms ?? null,
    nodesExplored: m.nodes_explored ?? m.nodesExplored ?? m.nodes ?? null,
    backtracks: m.backtracks ?? null,
    combinationsTried: m.combinations_tried ?? m.combinationsTried ?? null,
    memoryPeakKb: m.memory_peak_kb ?? m.memoryPeakKb ?? null,
    algorithm: m.algorithm ?? 'Backtracking',
    algorithmKey: m.algorithm_key ?? m.algorithmKey ?? algo,
  }
}

function getBlockConfig(size) {
  if (size === 9) return { rows: 3, cols: 3 }
  if (size === 12) return { rows: 3, cols: 4 }
  if (size === 16) return { rows: 4, cols: 4 }
  return { rows: 3, cols: 3 }
}

function getValidValues(size) {
  if (size === 9) return VALUES_9
  if (size === 12) return VALUES_12
  if (size === 16) return VALUES_16
  return VALUES_9
}

function triggerDownload(url, filename) {
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
}

export function useSudoku() {
  const boardSize = ref(9)
  const selectedAlgorithm = ref('backtracking')
  const datasets = ref([])
  const selectedDataset = ref('')
  const grid = ref(createEmptyGrid(9))
  const initialGrid = ref(createEmptyGrid(9))
  const solvedGrid = ref(createEmptyGrid(9))
  const solvedCells = ref(new Set())
  const metrics = ref({
    executionTime: null,
    nodesExplored: null,
    backtracks: null,
    combinationsTried: null,
    memoryPeakKb: null,
    algorithm: '—',
    algorithmKey: null,
  })
  const comparisonMetrics = ref(null)
  const algorithmComparison = ref(null)
  const benchmarkResult = ref(null)
  const exportMessage = ref('')
  const status = ref('idle')
  const errorMessage = ref('')
  const isLoading = ref(false)
  const isSolving = ref(false)
  const isComparing = ref(false)

  const timer = useTimer()

  const validValues = computed(() => getValidValues(boardSize.value))
  const blockRows = computed(() => getBlockConfig(boardSize.value).rows)
  const blockCols = computed(() => getBlockConfig(boardSize.value).cols)
  const isBusy = computed(() => isLoading.value || isSolving.value || isComparing.value)
  const bruteForceAvailable = computed(() => boardSize.value === 9)
  const gephiAvailable = computed(() => boardSize.value === 9)
  const showDualBoards = computed(
    () => status.value === 'solved' && solvedGrid.value.some((row) => row.some(Boolean))
  )

  function resetMetrics() {
    metrics.value = {
      executionTime: null,
      nodesExplored: null,
      backtracks: null,
      combinationsTried: null,
      memoryPeakKb: null,
      algorithm: '—',
      algorithmKey: null,
    }
  }

  function resetBoard(size = boardSize.value) {
    grid.value = createEmptyGrid(size)
    initialGrid.value = createEmptyGrid(size)
    solvedGrid.value = createEmptyGrid(size)
    solvedCells.value = new Set()
    resetMetrics()
    comparisonMetrics.value = null
    algorithmComparison.value = null
    benchmarkResult.value = null
    exportMessage.value = ''
    timer.reset()
    status.value = 'idle'
    errorMessage.value = ''
  }

  function beginPuzzle() {
    timer.reset()
    timer.start()
    status.value = 'playing'
    solvedGrid.value = createEmptyGrid(boardSize.value)
  }

  async function loadDatasetList() {
    isLoading.value = true
    errorMessage.value = ''
    try {
      const list = await fetchDatasets(boardSize.value)
      datasets.value = list
      selectedDataset.value = list.length ? list[0].id : ''
    } catch {
      datasets.value = []
      selectedDataset.value = ''
      errorMessage.value = 'No se pudo conectar con la API para obtener los datasets.'
    } finally {
      isLoading.value = false
    }
  }

  async function loadSelectedSudoku() {
    if (!selectedDataset.value) {
      errorMessage.value = 'Selecciona un tablero disponible.'
      return
    }
    isLoading.value = true
    errorMessage.value = ''
    resetMetrics()
    solvedCells.value = new Set()
    solvedGrid.value = createEmptyGrid(boardSize.value)
    try {
      const data = await loadSudoku(selectedDataset.value)
      const size = data.size ?? boardSize.value
      const puzzle = normalizeGrid(data.puzzle ?? data.board, size)
      grid.value = puzzle.map((row) => [...row])
      initialGrid.value = puzzle.map((row) => [...row])
      beginPuzzle()
    } catch {
      errorMessage.value = 'Error al cargar el Sudoku. Verifica que la API esté activa.'
    } finally {
      isLoading.value = false
    }
  }

  async function solve() {
    if (status.value === 'loaded' || status.value === 'playing') {
      if (!timer.isRunning.value) timer.start()
    }
    isSolving.value = true
    errorMessage.value = ''
    if (metrics.value.algorithmKey && metrics.value.algorithmKey !== selectedAlgorithm.value) {
      comparisonMetrics.value = { ...metrics.value }
    }
    resetMetrics()
    solvedCells.value = new Set()
    status.value = 'solving'
    try {
      const puzzleSnapshot = initialGrid.value.map((row) => [...row])
      const algo = selectedAlgorithm.value
      const response = await solveSudoku(boardSize.value, gridToApi(grid.value), algo)
      if (!response.success && response.success !== undefined) {
        throw new Error(response.message ?? 'No se encontró solución.')
      }
      const solution = normalizeGrid(response.solution, boardSize.value)
      grid.value = solution
      solvedGrid.value = solution.map((row) => [...row])
      solvedCells.value = solvedCellsFromResponse(
        puzzleSnapshot,
        solution,
        response.solved_cells
      )
      metrics.value = mapMetrics(response.metrics ?? response, algo)
      timer.stop()
      status.value = 'solved'
    } catch (err) {
      errorMessage.value =
        err.response?.data?.detail ?? err.response?.data?.message ?? err.message ?? 'Error al resolver el Sudoku.'
      status.value = 'error'
    } finally {
      isSolving.value = false
    }
  }

  async function compareAllAlgorithms() {
    if (!initialGrid.value.some((row) => row.some(Boolean))) {
      errorMessage.value = 'Carga un tablero antes de comparar algoritmos.'
      return
    }
    isComparing.value = true
    errorMessage.value = ''
    exportMessage.value = ''
    try {
      const algos =
        boardSize.value === 9
          ? ['backtracking', 'mrv', 'brute_force']
          : ['backtracking', 'mrv']
      const result = await compareAlgorithms(
        boardSize.value,
        gridToApi(initialGrid.value),
        algos
      )
      algorithmComparison.value = result
      benchmarkResult.value = null
    } catch (err) {
      errorMessage.value =
        err.response?.data?.detail ?? err.message ?? 'Error al comparar algoritmos.'
    } finally {
      isComparing.value = false
    }
  }

  async function executeBenchmark() {
    isComparing.value = true
    errorMessage.value = ''
    exportMessage.value = ''
    try {
      benchmarkResult.value = await runBenchmark(selectedAlgorithm.value, boardSize.value)
    } catch (err) {
      errorMessage.value =
        err.response?.data?.detail ?? err.message ?? 'Error al ejecutar benchmark.'
    } finally {
      isComparing.value = false
    }
  }

  async function downloadMetrics(format = 'xlsx') {
    const payload = algorithmComparison.value
      ? { ...algorithmComparison.value }
      : benchmarkResult.value
        ? { ...benchmarkResult.value }
        : { metrics: metrics.value, puzzle_size: boardSize.value }

    if (!payload.comparison && !payload.metrics && metrics.value.algorithmKey === null) {
      errorMessage.value = 'No hay métricas para exportar. Resuelve o compara primero.'
      return
    }

    try {
      const { download_url: downloadUrl } = await exportMetrics(payload, format, 'metricas_sudoku')
      if (downloadUrl) {
        triggerDownload(downloadUrl, `metricas_sudoku.${format}`)
        exportMessage.value = `Métricas exportadas (${format.toUpperCase()}).`
      }
    } catch (err) {
      errorMessage.value =
        err.response?.data?.detail ?? err.message ?? 'Error al exportar métricas.'
    }
  }

  async function downloadGephiFiles() {
    if (!gephiAvailable.value) {
      errorMessage.value = 'El grafo de 81 nodos solo aplica a Sudoku 9×9.'
      return
    }
    const datasetId = selectedDataset.value || '9x9_facil_01'
    try {
      const result = await exportGraph(datasetId, true)
      const files = result.exported_files ?? {}
      if (files.nodes_csv) {
        triggerDownload('/api/graph/download/sudoku_9x9_nodes.csv', 'sudoku_9x9_nodes.csv')
      }
      if (files.edges_csv) {
        setTimeout(() => {
          triggerDownload('/api/graph/download/sudoku_9x9_edges.csv', 'sudoku_9x9_edges.csv')
        }, 300)
      }
      exportMessage.value = `Grafo exportado: ${result.graph?.node_count ?? 81} nodos, ${result.graph?.edge_count ?? 0} aristas.`
    } catch (err) {
      errorMessage.value =
        err.response?.data?.detail ?? err.message ?? 'Error al exportar grafo para Gephi.'
    }
  }

  function clearBoard() {
    grid.value = initialGrid.value.map((row) => [...row])
    solvedGrid.value = createEmptyGrid(boardSize.value)
    solvedCells.value = new Set()
    resetMetrics()
    comparisonMetrics.value = null
    if (initialGrid.value.some((row) => row.some(Boolean))) {
      beginPuzzle()
    } else {
      timer.reset()
      status.value = 'idle'
    }
    errorMessage.value = ''
  }

  async function generateNew() {
    isLoading.value = true
    errorMessage.value = ''
    resetMetrics()
    solvedCells.value = new Set()
    solvedGrid.value = createEmptyGrid(boardSize.value)
    try {
      const data = await generateSudoku(boardSize.value)
      const size = data.size ?? boardSize.value
      const puzzle = normalizeGrid(data.puzzle ?? data.board, size)
      grid.value = puzzle.map((row) => [...row])
      initialGrid.value = puzzle.map((row) => [...row])
      if (data.id) selectedDataset.value = data.id
      beginPuzzle()
    } catch {
      errorMessage.value = 'Error al generar un nuevo Sudoku.'
    } finally {
      isLoading.value = false
    }
  }

  function updateCell(row, col, value) {
    if (initialGrid.value[row][col]) return
    const normalized = normalizeCell(value)
    if (normalized && !validValues.value.includes(normalized)) return

    if (!timer.isRunning.value && (status.value === 'playing' || status.value === 'loaded')) {
      timer.start()
    }

    grid.value[row][col] = normalized
    solvedCells.value = new Set()
    solvedGrid.value = createEmptyGrid(boardSize.value)
    if (status.value === 'solved') status.value = 'playing'
  }

  watch(boardSize, (size) => {
    if (size !== 9 && selectedAlgorithm.value === 'brute_force') {
      selectedAlgorithm.value = 'backtracking'
    }
    resetBoard(size)
    loadDatasetList()
  })

  loadDatasetList()

  return {
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
    isLoading,
    isSolving,
    isComparing,
    isBusy,
    bruteForceAvailable,
    gephiAvailable,
    showDualBoards,
    validValues,
    blockRows,
    blockCols,
    timer,
    loadSelectedSudoku,
    solve,
    clearBoard,
    generateNew,
    updateCell,
    loadDatasetList,
    compareAllAlgorithms,
    executeBenchmark,
    downloadMetrics,
    downloadGephiFiles,
  }
}
