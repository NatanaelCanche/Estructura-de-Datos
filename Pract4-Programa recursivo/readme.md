 Solución Recursiva :
 Ventaja: El código es mucho más limpio, corto y se asemeja directamente a la definición matemática de la serie: Fn = Fn-1 + Fn-2
 Desventaja: Es extremadamente ineficiente para números grandes. Esto se debe a que recalcula los mismos valores una y otra vez (redundancia). Su complejidad es exponencial O(2^n)

 Solucion Iterativa:
 Ventaja: Es mucho más rápida. Solo calcula cada número de la serie una vez y los suma sobre la marcha. Su complejidad es lineal O(n).
 Desventaja: El código es un poco más largo y requiere el manejo manual de variables temporales (a y b), lo que lo hace menos "intuitivo" a primera vista.
