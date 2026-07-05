from __future__ import annotations
import csv
from pathlib import Path
from typing import Any
from sudoku_constants import get_blocks

def _id_nodo(fila: int, columna: int, size: int) -> str:
    return f'r{fila}c{columna}'

def _celdas_misma_unidad(fila: int, columna: int, size: int) -> set[tuple[int, int]]:
    br, bc = get_blocks(size)
    relacionadas: set[tuple[int, int]] = set()
    for c in range(size):
        if c != columna:
            relacionadas.add((fila, c))
    for r in range(size):
        if r != fila:
            relacionadas.add((r, columna))
    inicio_f, inicio_c = (fila // br * br, columna // bc * bc)
    for r in range(inicio_f, inicio_f + br):
        for c in range(inicio_c, inicio_c + bc):
            if (r, c) != (fila, columna):
                relacionadas.add((r, c))
    return relacionadas

def modelar_grafo_restricciones(board: list[list[str]], size: int=9) -> dict[str, Any]:
    if len(board) != size or any((len(fila) != size for fila in board)):
        raise ValueError(f'Se esperaba una matriz {size}×{size}.')
    nodos: list[dict[str, Any]] = []
    aristas: list[dict[str, str]] = []
    aristas_vistas: set[tuple[str, str]] = set()
    for fila in range(size):
        for columna in range(size):
            nodo_id = _id_nodo(fila, columna, size)
            valor = board[fila][columna] or '.'
            nodos.append({'id': nodo_id, 'label': f'({fila},{columna})={valor}', 'row': fila, 'col': columna, 'value': valor, 'fixed': bool(board[fila][columna])})
            for rf, cf in _celdas_misma_unidad(fila, columna, size):
                origen = nodo_id
                destino = _id_nodo(rf, cf, size)
                par = tuple(sorted((origen, destino)))
                if par in aristas_vistas:
                    continue
                aristas_vistas.add(par)
                aristas.append({'source': origen, 'target': destino, 'type': 'Undirected', 'relationship': 'constraint'})
    return {'size': size, 'node_count': len(nodos), 'edge_count': len(aristas), 'nodes': nodos, 'edges': aristas}

def exportar_archivos_gephi(grafo: dict[str, Any], directorio_salida: str | Path, prefijo: str='sudoku') -> dict[str, str]:
    salida = Path(directorio_salida)
    salida.mkdir(parents=True, exist_ok=True)
    ruta_nodos = salida / f'{prefijo}_nodes.csv'
    ruta_aristas = salida / f'{prefijo}_edges.csv'
    with ruta_nodos.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=['Id', 'Label', 'Row', 'Col', 'Value', 'Fixed'])
        escritor.writeheader()
        for nodo in grafo['nodes']:
            escritor.writerow({'Id': nodo['id'], 'Label': nodo['label'], 'Row': nodo['row'], 'Col': nodo['col'], 'Value': nodo['value'], 'Fixed': int(nodo['fixed'])})
    with ruta_aristas.open('w', newline='', encoding='utf-8') as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=['Source', 'Target', 'Type', 'Relationship'])
        escritor.writeheader()
        for arista in grafo['edges']:
            escritor.writerow({'Source': arista['source'], 'Target': arista['target'], 'Type': arista['type'], 'Relationship': arista['relationship']})
    return {'nodes_csv': str(ruta_nodos.resolve()), 'edges_csv': str(ruta_aristas.resolve())}
