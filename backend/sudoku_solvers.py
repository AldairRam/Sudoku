"""
Algoritmos de resolución y preprocesamiento para Sudoku.

Requisitos cubiertos:
  8.  Backtracking.
  9.  Fuerza Bruta.
 10.  Backtracking con heurística MRV (Minimum Remaining Values).
 11.  Búsqueda DFS explícita usada por Backtracking.
 12.  Divide y Vencerás como preprocesamiento de subcuadrantes.
"""

from __future__ import annotations

from typing import Callable

from sudoku_board import (
    obtener_candidatos_celda,
    validar_colocacion_celda,
    verificar_solucion_valida,
)
from sudoku_constants import get_blocks, get_values, normalize


class SolverMetrics:
    """Acumula métricas de ejecución de un algoritmo de resolución."""

    def __init__(self) -> None:
        self.nodes = 0
        self.backtracks = 0
        self.combinations_tried = 0


ALGORITMOS: dict[str, dict[str, str | Callable[..., bool]]] = {}


def busqueda_dfs(
    board: list[list[str]],
    size: int,
    metrics: SolverMetrics,
    seleccionar_celda: Callable[[list[list[str]], int], tuple[int, int] | None],
    probar_valores: Callable[[list[list[str]], int, int, int, SolverMetrics], bool],
) -> bool:
    """
    Búsqueda en profundidad (DFS) genérica para Sudoku.
    Delega la elección de celda y la expansión de valores al callback recibido.
    """
    celda = seleccionar_celda(board, size)
    if celda is None:
        return True

    fila, columna = celda
    metrics.nodes += 1
    return probar_valores(board, size, fila, columna, metrics)


def _seleccionar_primera_vacia(board: list[list[str]], size: int) -> tuple[int, int] | None:
    for r in range(size):
        for c in range(size):
            if not board[r][c]:
                return r, c
    return None


def _seleccionar_mrv(board: list[list[str]], size: int) -> tuple[int, int] | None:
    """Heurística voraz MRV: elige la celda con menos candidatos válidos."""
    mejor: tuple[int, int] | None = None
    min_candidatos = size + 1

    for r in range(size):
        for c in range(size):
            if board[r][c]:
                continue
            candidatos = obtener_candidatos_celda(board, r, c, size)
            cantidad = len(candidatos)
            if cantidad < min_candidatos:
                min_candidatos = cantidad
                mejor = (r, c)
                if min_candidatos == 0:
                    return mejor
    return mejor


def _expandir_backtracking(
    board: list[list[str]],
    size: int,
    fila: int,
    columna: int,
    metrics: SolverMetrics,
) -> bool:
    for numero in get_values(size):
        valor = normalize(numero)
        if validar_colocacion_celda(board, fila, columna, valor, size):
            board[fila][columna] = valor
            if busqueda_dfs(board, size, metrics, _seleccionar_primera_vacia, _expandir_backtracking):
                return True
            board[fila][columna] = ""
            metrics.backtracks += 1
    return False


def _expandir_mrv(
    board: list[list[str]],
    size: int,
    fila: int,
    columna: int,
    metrics: SolverMetrics,
) -> bool:
    for valor in obtener_candidatos_celda(board, fila, columna, size):
        board[fila][columna] = valor
        if busqueda_dfs(board, size, metrics, _seleccionar_mrv, _expandir_mrv):
            return True
        board[fila][columna] = ""
        metrics.backtracks += 1
    return False


def resolver_backtracking(
    board: list[list[str]], size: int, metrics: SolverMetrics
) -> bool:
    """Resuelve el Sudoku con backtracking y poda por restricciones."""
    return busqueda_dfs(
        board, size, metrics, _seleccionar_primera_vacia, _expandir_backtracking
    )


def resolver_backtracking_mrv(
    board: list[list[str]], size: int, metrics: SolverMetrics
) -> bool:
    """Resuelve el Sudoku con backtracking + heurística MRV."""
    return busqueda_dfs(board, size, metrics, _seleccionar_mrv, _expandir_mrv)


def resolver_fuerza_bruta(
    board: list[list[str]], size: int, metrics: SolverMetrics
) -> bool:
    """
    Prueba combinaciones sin poda anticipada;
    valida la solución completa al llegar al final.
    """
    vacias = [(r, c) for r in range(size) for c in range(size) if not board[r][c]]

    def fuerza_bruta(indice: int) -> bool:
        if indice >= len(vacias):
            metrics.nodes += 1
            return verificar_solucion_valida(board, size)

        fila, columna = vacias[indice]
        for numero in get_values(size):
            valor = normalize(numero)
            metrics.nodes += 1
            metrics.combinations_tried += 1
            board[fila][columna] = valor
            if fuerza_bruta(indice + 1):
                return True
            board[fila][columna] = ""
        metrics.backtracks += 1
        return False

    return fuerza_bruta(0)


def preprocesar_divide_y_venceras(
    board: list[list[str]], size: int = 9
) -> dict[str, object]:
    """
    Divide el tablero en subcuadrantes y preprocesa cada bloque de forma independiente.
    Calcula celdas vacías y dominios de candidatos por subcuadrante.
    """
    br, bc = get_blocks(size)
    subcuadrantes: list[dict[str, object]] = []
    indice_bloque = 0

    for sr in range(0, size, br):
        for sc in range(0, size, bc):
            celdas_vacias: list[tuple[int, int]] = []
            dominios: dict[str, list[str]] = {}

            for r in range(sr, sr + br):
                for c in range(sc, sc + bc):
                    if not board[r][c]:
                        celdas_vacias.append((r, c))
                        dominios[f"{r},{c}"] = obtener_candidatos_celda(board, r, c, size)

            subcuadrantes.append(
                {
                    "block_index": indice_bloque,
                    "origin": (sr, sc),
                    "empty_cells": celdas_vacias,
                    "domains": dominios,
                    "empty_count": len(celdas_vacias),
                }
            )
            indice_bloque += 1

    return {
        "size": size,
        "block_shape": (br, bc),
        "blocks": subcuadrantes,
        "total_empty_cells": sum(b["empty_count"] for b in subcuadrantes),
    }


def obtener_resolver(algoritmo: str) -> Callable[[list[list[str]], int, SolverMetrics], bool]:
    """Devuelve la función de resolución asociada a la clave del algoritmo."""
    resolver = ALGORITMOS.get(algoritmo, {}).get("fn")
    if resolver is None:
        raise ValueError(f"Algoritmo desconocido: {algoritmo}")
    return resolver  # type: ignore[return-value]


ALGORITMOS.update(
    {
        "backtracking": {
            "name": "Backtracking con poda por restricciones",
            "fn": resolver_backtracking,
        },
        "brute_force": {
            "name": "Fuerza Bruta (sin poda anticipada)",
            "fn": resolver_fuerza_bruta,
        },
        "mrv": {
            "name": "Backtracking con heurística MRV",
            "fn": resolver_backtracking_mrv,
        },
    }
)
