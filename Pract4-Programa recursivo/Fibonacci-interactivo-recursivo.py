import time

def fibonacci_recursivo(n):
    if n <= 1:
        return n
    else:
        return fibonacci_recursivo(n-1) + fibonacci_recursivo(n-2)

def fibonacci_iterativo(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


n_objetivo = 35  


inicio = time.time()
res_rec = fibonacci_recursivo(n_objetivo)
fin = time.time()
tiempo_rec = fin - inicio


inicio = time.time()
res_ite = fibonacci_iterativo(n_objetivo)
fin = time.time()
tiempo_ite = fin - inicio

print(f"Resultado para n={n_objetivo}: {res_rec}")
print(f"Tiempo Recursivo: {tiempo_rec:.6f} segundos")
print(f"Tiempo Iterativo: {tiempo_ite:.6f} segundos")