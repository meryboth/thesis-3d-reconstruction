# El Paraguas: reconstrucción geométrica interpretativa

Modelo de los **dos paraguas presentes en el relevamiento**, creado en Blender mediante MCP el 08/09/2026.

## Entregables

- `el_paraguas_reconstruido.blend`: escena editable con cuatro objetos arquitectónicos (dos cubiertas y dos columnas), referencias COLMAP ocultas y presentación con luces/cámara.
- `el_paraguas_reconstruido.glb`: solamente los cuatro objetos arquitectónicos, con materiales.
- `paraguas_perspectiva.png`: render del modelo.
- `parametros_ajuste.json`: ejes, radios, orientaciones, dimensiones y coeficientes de las superficies.
- `verificacion_modelo.json`: revisión de topología y distancias a una muestra de los puntos usados para ajustar el modelo.
- `referencias.jpg`: selección de doce fotografías del dataset.
- Generador: `reconstruir_paraguas_blender.py`. Se ejecuta dentro de Blender, con un diccionario compartido de globals/locals para `exec`. Lee los parámetros JSON y crea una escena nueva. Las referencias se incorporan si ya están importadas con los nombres usados en esta sesión.

## Referencias y procedimiento

Fuente geométrica: `../../01-paraguas-vicentelopez/02-resultados-finales/colmap-fotogrametria-densa/fused_medium_high_clean.ply` (502.817 puntos). La malla `meshed-poisson-clean-trim5.ply` sirve para comparación visual; sus artefactos no se copian al modelo.

Se transforma la nube mediante **X=x_COLMAP, Y=z_COLMAP, Z=2.62-y_COLMAP** para presentarla de pie. Las columnas se ajustan mediante círculos en nueve cortes entre z=0,6 y z=2,2, y una recta para el desplazamiento de sus centros. El radio se toma de la mediana de esos cortes. La orientación de cada cubierta se estima minimizando el área de su rectángulo envolvente robusto.

Para las cubiertas se divide cada planta en 34×34 celdas. Se estiman cuantiles de altura 0,18 y 0,82 en las celdas con suficiente cobertura y se ajustan dos superficies suaves con ponderación robusta. La base del ajuste contiene términos radiales y correcciones direccionales: 1, sqrt(r), r, r², r³, u, v, u²-v², uv, u²v². Se generan caras superior e inferior, borde cerrado y tapas centrales. Los materiales son una interpretación visual de las fotografías; no son texturas fotogramétricas.

## Alcance y límites

- **Escala SfM, sin calibración métrica**. No interpretar las unidades como metros. El GLB conserva los valores numéricos de estas unidades; calibrar antes de importarlo en un flujo métrico.
- La parte superior central, dentro de r=0,22 unidades SfM, tiene cobertura insuficiente y está interpolada. Las cotas de sus tapas centrales (2,82 y 2,79) son decisiones de modelado. El espesor se regulariza entre 0,015 y 0,16 unidades SfM; no representa una medición constructiva.
- El suelo plano es solamente presentación. No se reconstruyeron terreno, barandas, bancos, cimentaciones, armaduras ni desagües internos.
- Cubiertas y columnas son sólidos separados con una pequeña intersección en su encuentro; no constituyen un único sólido booleano.
- Las cuatro piezas tienen cero aristas no manifold en la revisión. Las distancias registradas son contra puntos de la misma nube utilizada para el ajuste; **no constituyen validación independiente ni precisión métrica**.
- Los archivos originales y los capítulos de tesis no fueron modificados.

Para comparar en Blender, activar la colección `02 Referencias COLMAP (ocultas)` y la visibilidad del objeto de referencia elegido. La nube y la malla conservan la misma transformación que el modelo.

Copia organizada en 07-modelado. Se incluye captura_blender.png.
