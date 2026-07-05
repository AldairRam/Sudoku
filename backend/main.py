from __future__ import annotations
import copy
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sudoku_board import celdas_resueltas, convertir_a_matriz_9x9, generar_tablero_sudoku, puzzle_a_tablero, tablero_a_api, validar_puzzle_inicial
from sudoku_datasets import listar_datasets_disponibles, obtener_tablero_por_id
from sudoku_graph import exportar_archivos_gephi, modelar_grafo_restricciones
from sudoku_metrics import calcular_porcentaje_resueltos, comparar_rendimiento_algoritmos, exportar_metricas, resolver_con_metricas
from sudoku_solvers import ALGORITMOS, preprocesar_divide_y_venceras
app = FastAPI(title='Sudoku Solver API')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])
EXPORT_DIR = Path(__file__).parent / 'exports'
GEPHI_DIR = EXPORT_DIR / 'gephi'

class SolveRequest(BaseModel):
    size: int
    puzzle: list[list[Any]]
    algorithm: str = 'backtracking'

class GenerateRequest(BaseModel):
    size: int

class GraphRequest(BaseModel):
    size: int = 9
    puzzle: list[list[Any]] | None = None
    dataset_id: str | None = None
    export: bool = False

class CompareRequest(BaseModel):
    size: int
    puzzle: list[list[Any]]
    algorithms: list[str] | None = None

class BenchmarkRequest(BaseModel):
    algorithm: str = 'backtracking'
    size: int | None = None

class ExportMetricsRequest(BaseModel):
    metrics: dict[str, Any]
    format: str = 'json'
    filename: str = 'metricas'

@app.get('/api/datasets')
def list_datasets(size: int=9):
    return {'datasets': listar_datasets_disponibles(size)}

@app.get('/api/sudoku/{dataset_id}')
def get_sudoku(dataset_id: str):
    try:
        return obtener_tablero_por_id(dataset_id)
    except KeyError:
        raise HTTPException(status_code=404, detail='Dataset no encontrado')

@app.get('/api/algorithms')
def list_algorithms():
    return {'algorithms': [{'key': clave, 'name': info['name']} for clave, info in ALGORITMOS.items()]}

@app.post('/api/solve')
def solve(request: SolveRequest):
    size = request.size
    if size not in (9, 12, 16):
        raise HTTPException(status_code=400, detail='Tamaño no soportado')
    algo_key = request.algorithm if request.algorithm in ALGORITMOS else 'backtracking'
    if algo_key == 'brute_force' and size > 9:
        raise HTTPException(status_code=400, detail='Fuerza Bruta solo está disponible para Sudoku 9×9.')
    inicial = puzzle_a_tablero(request.puzzle, size)
    if size == 9:
        convertir_a_matriz_9x9(request.puzzle)
    validacion = validar_puzzle_inicial(copy.deepcopy(inicial), size)
    if not validacion['valid']:
        raise HTTPException(status_code=400, detail=f"El tablero tiene {validacion['conflicts']} pistas conflictivas.")
    preproceso = preprocesar_divide_y_venceras(inicial, size)
    resultado = resolver_con_metricas(request.puzzle, size, algo_key)
    if not resultado['success']:
        return {'success': False, 'message': 'No se encontró solución'}
    solucion = resultado['solution']
    metricas = resultado['metrics']
    return {'success': True, 'solution': tablero_a_api(solucion), 'solved_cells': celdas_resueltas(inicial, solucion), 'preprocessing': preproceso, 'metrics': metricas}

@app.post('/api/generate')
def generate(request: GenerateRequest):
    size = request.size
    if size not in (9, 12, 16):
        raise HTTPException(status_code=400, detail='Tamaño no soportado')
    puzzle, gen_id = generar_tablero_sudoku(size)
    return {'id': gen_id, 'size': size, 'puzzle': tablero_a_api(puzzle)}

@app.post('/api/graph')
def build_graph(request: GraphRequest):
    if request.size != 9:
        raise HTTPException(status_code=400, detail='El grafo de 81 nodos está definido para Sudoku 9×9.')
    if request.dataset_id:
        try:
            dataset = obtener_tablero_por_id(request.dataset_id)
            puzzle = dataset['puzzle']
        except KeyError:
            raise HTTPException(status_code=404, detail='Dataset no encontrado')
    elif request.puzzle:
        puzzle = request.puzzle
    else:
        raise HTTPException(status_code=400, detail='Indique dataset_id o puzzle.')
    board = convertir_a_matriz_9x9(puzzle)
    grafo = modelar_grafo_restricciones(board, 9)
    respuesta: dict[str, Any] = {'graph': {'node_count': grafo['node_count'], 'edge_count': grafo['edge_count'], 'nodes': grafo['nodes'], 'edges': grafo['edges']}}
    if request.export:
        rutas = exportar_archivos_gephi(grafo, GEPHI_DIR, prefijo='sudoku_9x9')
        respuesta['exported_files'] = rutas
    return respuesta

@app.post('/api/compare')
def compare_algorithms(request: CompareRequest):
    if request.size not in (9, 12, 16):
        raise HTTPException(status_code=400, detail='Tamaño no soportado')
    comparacion = comparar_rendimiento_algoritmos(request.puzzle, request.size, request.algorithms)
    return comparacion

@app.post('/api/benchmark')
def benchmark_datasets(request: BenchmarkRequest):
    puzzles = listar_datasets_disponibles(request.size)
    puzzles_completos = []
    for meta in puzzles:
        dataset = obtener_tablero_por_id(meta['id'])
        puzzles_completos.append({'size': dataset['size'], 'puzzle': dataset['puzzle']})
    resultado = calcular_porcentaje_resueltos(puzzles_completos, request.algorithm)
    return resultado

@app.post('/api/metrics/export')
def export_metrics_endpoint(request: ExportMetricsRequest):
    if request.format not in ('json', 'csv', 'xlsx'):
        raise HTTPException(status_code=400, detail="Formato debe ser 'json', 'csv' o 'xlsx'.")
    ruta = EXPORT_DIR / request.filename
    try:
        archivo = exportar_metricas(request.metrics, ruta, request.format)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    return {'exported_file': archivo, 'download_url': f'/api/metrics/download/{Path(archivo).name}'}

@app.get('/api/metrics/download/{filename}')
def download_metrics_file(filename: str):
    ruta = (EXPORT_DIR / filename).resolve()
    if not str(ruta).startswith(str(EXPORT_DIR.resolve())):
        raise HTTPException(status_code=400, detail='Ruta no válida.')
    if not ruta.exists():
        raise HTTPException(status_code=404, detail='Archivo no encontrado.')
    media_types = {'.json': 'application/json', '.csv': 'text/csv', '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
    media_type = media_types.get(ruta.suffix.lower(), 'application/octet-stream')
    return FileResponse(ruta, media_type=media_type, filename=filename)

@app.get('/api/graph/download/{filename}')
def download_gephi_file(filename: str):
    ruta = (GEPHI_DIR / filename).resolve()
    if not str(ruta).startswith(str(GEPHI_DIR.resolve())):
        raise HTTPException(status_code=400, detail='Ruta no válida.')
    if not ruta.exists():
        raise HTTPException(status_code=404, detail='Archivo no encontrado.')
    return FileResponse(ruta, media_type='text/csv', filename=filename)
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5000)
