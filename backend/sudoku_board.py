"""
Conversión y validación de tableros Sudoku.

Requisitos cubiertos:
  4. Convertir el tablero del dataset en una matriz 9×9.
  5. Generar un nuevo tablero de Sudoku.
 13. Validar si un número puede colocarse en una celda.
 14. Verificar que una solución cumpla las reglas del Sudoku.
"""

from __future__ import annotations

import copy
import random
from typing import Any

from sudoku_constants import get_blocks, get_values, normalize


def puzzle_a_tablero(puzzle: list[list[Any]], size: int) -> list[list[str]]:
    """Convierte el puzzle del API a una matriz interna de cadenas."""
    return [[normalize(celda) for celda in fila] for fila in puzzle]


def convertir_a_matriz_9x9(puzzle: list[list[Any]]) -> list[list[str]]:
    """
    Convierte un tablero del dataset a matriz 9×9 normalizada.
    Lanza ValueError si el puzzle no tiene exactamente 9 filas y 9 columnas.
    """
    if len(puzzle) != 9 or any(len(fila) != 9 for fila in puzzle):
        raise ValueError("El tablero debe ser una matriz 9×9.")
    return puzzle_a_tablero(puzzle, 9)


def tablero_a_api(board: list[list[str]]) -> list[list[Any]]:
    """Convierte la matriz interna al formato consumido por el frontend/API."""
    resultado: list[list[Any]] = []
    for fila in board:
        fila_api: list[Any] = []
        for celda in fila:
            if not celda:
                fila_api.append(0)
            elif celda.isdigit():
                fila_api.append(int(celda))
            else:
                fila_api.append(celda)
        resultado.append(fila_api)
    return resultado


def celdas_resueltas(
    inicial: list[list[str]], solucion: list[list[str]]
) -> list[list[int]]:
    """Identifica las celdas que estaban vacías y fueron completadas."""
    celdas: list[list[int]] = []
    for r, fila in enumerate(inicial):
        for c, valor in enumerate(fila):
            if not valor and solucion[r][c]:
                celdas.append([r, c])
    return celdas


def validar_colocacion_celda(
    board: list[list[str]], fila: int, columna: int, valor: str, size: int
) -> bool:
    """
    Verifica si un valor puede colocarse en (fila, columna)
    respetando fila, columna y subcuadrante.
    """
    br, bc = get_blocks(size)
    if valor in board[fila]:
        return False
    if valor in (board[r][columna] for r in range(size)):
        return False
    inicio_f, inicio_c = (fila // br) * br, (columna // bc) * bc
    for r in range(inicio_f, inicio_f + br):
        for c in range(inicio_c, inicio_c + bc):
            if board[r][c] == valor:
                return False
    return True


def verificar_solucion_valida(board: list[list[str]], size: int) -> bool:
    """Comprueba que el tablero esté completo y cumpla todas las reglas del Sudoku."""
    br, bc = get_blocks(size)
    for r in range(size):
        if any(not board[r][c] for c in range(size)):
            return False
        if len({board[r][c] for c in range(size)}) != size:
            return False
    for c in range(size):
        if len({board[r][c] for r in range(size)}) != size:
            return False
    for sr in range(0, size, br):
        for sc in range(0, size, bc):
            bloque = [
                board[r][c]
                for r in range(sr, sr + br)
                for c in range(sc, sc + bc)
            ]
            if len(set(bloque)) != size:
                return False
    return True


def validar_puzzle_inicial(board: list[list[str]], size: int) -> dict[str, Any]:
    """
    Verifica que las pistas iniciales no violen las reglas del Sudoku.
    Devuelve si es válido y la cantidad de conflictos detectados.
    """
    conflictos: list[dict[str, Any]] = []
    for fila in range(size):
        for columna in range(size):
            if not board[fila][columna]:
                continue
            valor = board[fila][columna]
            board[fila][columna] = ""
            if not validar_colocacion_celda(board, fila, columna, valor, size):
                conflictos.append({"row": fila, "col": columna, "value": valor})
            board[fila][columna] = valor

    return {
        "valid": len(conflictos) == 0,
        "conflicts": len(conflictos),
        "conflict_cells": conflictos[:10],
    }


def sanitizar_puzzle(puzzle: list[list[Any]], size: int) -> tuple[list[list[Any]], int]:
    """
    Elimina pistas conflictivas del puzzle (conserva las válidas en orden de lectura).
    Necesario porque algunas cadenas del Excel contienen duplicados en fila/columna/bloque.
    """
    board = puzzle_a_tablero(puzzle, size)
    removidas = 0

    for fila in range(size):
        for columna in range(size):
            if not board[fila][columna]:
                continue
            valor = board[fila][columna]
            board[fila][columna] = ""
            if not validar_colocacion_celda(board, fila, columna, valor, size):
                board[fila][columna] = ""
                removidas += 1
            else:
                board[fila][columna] = valor

    return tablero_a_api(board), removidas


def obtener_candidatos_celda(
    board: list[list[str]], fila: int, columna: int, size: int
) -> list[str]:
    """Devuelve los valores válidos para una celda vacía."""
    if board[fila][columna]:
        return []
    return [
        normalize(valor)
        for valor in get_values(size)
        if validar_colocacion_celda(board, fila, columna, normalize(valor), size)
    ]


def generar_tablero_sudoku(size: int) -> tuple[list[list[str]], str]:
    """
    Genera un puzzle nuevo resolviendo un tablero completo
    y eliminando aproximadamente la mitad de las celdas.
    """
    if size not in (9, 12, 16):
        raise ValueError("Tamaño no soportado. Use 9, 12 o 16.")

    from sudoku_solvers import SolverMetrics, resolver_backtracking

    completo = [["" for _ in range(size)] for _ in range(size)]
    resolver_backtracking(completo, size, SolverMetrics())

    puzzle = copy.deepcopy(completo)
    eliminaciones = size * size // 2
    coordenadas = [(r, c) for r in range(size) for c in range(size)]
    random.shuffle(coordenadas)
    for r, c in coordenadas[:eliminaciones]:
        puzzle[r][c] = ""

    identificador = f"generated_{size}x{size}_{random.randint(1000, 9999)}"
    return puzzle, identificador
