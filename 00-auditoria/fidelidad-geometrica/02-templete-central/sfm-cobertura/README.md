# SfM — cobertura y calidad de malla (Templete Central)

Capturas desde CloudCompare/RealityScan de la malla texturizada, no atadas a una pose de cámara puntual (a diferencia de `../dji/comparacion_*.jpg` o `../insta360/comparacion_*.jpg`). Sirven para documentar completitud de la reconstrucción SfM en el análisis cualitativo de fidelidad geométrica (Cap. 4, 4.8).

- **vista_superior.png** — vista cenital de la cubierta cuadrada, dividida en 4 paños. Se ven varios huecos/zonas sin registro (parches negros irregulares), distribuidos en los 4 paños pero más concentrados en los dos superiores de la imagen. Se distingue con claridad la doble trayectoria de vuelo del dron (línea de puntos blancos, un anillo interior y uno exterior alrededor de la estructura) y un frustum verde aislado (cámara Insta360, separada del resto).
- **vista_lateral_01.png** — perfil lateral a nivel de piso: cubierta completa, 3 columnas visibles, superficie inferior de la losa con buen detalle de las nervaduras/molduras. Se ve fondo de referencia (posiblemente una placa u objeto reflectante rojo/amarillo bajo la cubierta, sin registrar con textura limpia) y los frustums de cámara del dron en dos líneas paralelas sobre la escena.
- **vista_lateral_02.png** — variante de ángulo de la vista lateral, más cercana, con el piso empedrado en primer plano y carteles/objetos bajo la cubierta visibles (sin reconstrucción limpia, aparecen como manchas de color). Buena vista para apreciar el detalle de las nervaduras de la losa y el ritmo de columnas.

Frustums blancos/azules visibles en las tres = posiciones de cámara del dataset (dron), no son parte de la malla.
