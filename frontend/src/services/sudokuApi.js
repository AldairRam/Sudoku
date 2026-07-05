import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000,
  headers: { 'Content-Type': 'application/json' },
})

export async function fetchDatasets(size) {
  const { data } = await api.get('/datasets', { params: { size } })
  return data.datasets ?? data
}

export async function loadSudoku(datasetId) {
  const { data } = await api.get(`/sudoku/${datasetId}`)
  return data
}

export async function solveSudoku(size, puzzle, algorithm = 'backtracking') {
  const { data } = await api.post('/solve', { size, puzzle, algorithm })
  return data
}

export async function generateSudoku(size) {
  const { data } = await api.post('/generate', { size })
  return data
}

export async function compareAlgorithms(size, puzzle, algorithms = null) {
  const { data } = await api.post('/compare', { size, puzzle, algorithms })
  return data
}

export async function runBenchmark(algorithm = 'backtracking', size = null) {
  const { data } = await api.post('/benchmark', { algorithm, size })
  return data
}

export async function exportGraph(datasetId, exportFiles = true) {
  const { data } = await api.post('/graph', {
    size: 9,
    dataset_id: datasetId,
    export: exportFiles,
  })
  return data
}

export async function exportMetrics(metrics, format = 'xlsx', filename = 'metricas') {
  const { data } = await api.post('/metrics/export', { metrics, format, filename })
  return data
}

export function getDownloadUrl(path) {
  if (!path) return null
  if (path.startsWith('http')) return path
  return path.startsWith('/') ? path : `/api/metrics/download/${path}`
}

export default api
