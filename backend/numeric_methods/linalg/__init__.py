"""Álgebra lineal directa (no iterativa) en Python puro con floats.

A diferencia de los solvers de `solvers/linear/` (Jacobi, Gauss-Seidel), que
son métodos iterativos registrados, aquí van herramientas auxiliares que un
método puede usar internamente; por ejemplo, Newton resuelve en cada
iteración un sistema lineal J·Δx = −F con la regla de Cramer.
"""
