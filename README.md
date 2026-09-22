# Atlas de Parasitología

Aplicación estática para estudiar y editar la base de parasitología veterinaria. La primera semilla se genera desde `PARÁSITOS.xlsx` y solo agrega registros nominales que están expresamente mencionados en el material de cátedra. No infiere rasgos clínicos, taxonómicos ni morfológicos.

## Qué incluye

- Fichas jerárquicas para gran grupo, grupo, subgrupo, familia, subfamilia, género y especie.
- Regla `spp.`: un género sin especie se muestra como *Género spp.*; una especie se muestra en minúscula e itálica.
- Modo consulta y modo edición. En edición se modifica texto con doble clic; `Ctrl/Cmd + Z` deshace el último cambio local.
- Búsqueda global, filtros, tabla ordenable, comparación y revisión explícita de discrepancias de fuente.
- Etiquetas editables, colores por ficha con recientes/favoritos e imágenes en el navegador mediante IndexedDB.
- Importación no destructiva desde XLSX, exportación XLSX y backup `atlas-parasitologia-backup.zip` (datos, colores y blobs de imágenes).

## Ejecución local

No se instala ningún servidor de pago. Desde la carpeta del proyecto:

```bash
python3 -m http.server 4173
```

Abrir `http://localhost:4173` en Chrome.

## Fuente y trazabilidad

- `dist/data/seed.json` fue construido desde la hoja `TODOS` de `PARÁSITOS.xlsx`.
- `tools/build_seed.py` es reproducible y conserva las filas de origen en cada ficha.
- Los nombres adicionales procedentes de los documentos de cátedra se marcan como **menciones nominales**, sin atribuirles información no escrita en los materiales.
- Las grafías contradictorias permanecen en *Revisión de fuentes* hasta su confirmación editorial.

## Firestore, únicamente plan gratuito

La aplicación funciona localmente sin cuenta ni nube. Para compartir **los datos de texto** entre navegadores:

1. Crear un proyecto en Firebase y seleccionar **Spark (sin costo)**. No activar Blaze, facturación ni Firebase Storage.
2. Crear una base **Cloud Firestore** y una aplicación web. El propio Firebase entrega el objeto de configuración; no es secreto.
3. Activar Google Sign-In si se desea usar la regla incluida, y publicar `firestore.rules` desde la consola.
4. Pegar el objeto de configuración en `Configuración > Sincronización Firestore` de la aplicación.

Las imágenes no se suben a Firebase: quedan locales en IndexedDB y se trasladan usando el backup ZIP. Esta decisión evita Firebase Storage y cualquier dependencia de almacenamiento pago.

> Antes de publicar para más personas, definir quiénes podrán autenticarse. La regla incluida exige autenticación y evita una base abierta al público.

## Despliegue gratuito

GitHub Pages puede servir estos archivos estáticos sin backend. El proyecto no requiere secretos en el repositorio. Una vez asociado el repositorio, configurar Pages para publicar desde la rama `main` y la raíz del proyecto.

## Desarrollo de la semilla

Tras actualizar el Excel, copiarlo como `../upload/PARÁSITOS.xlsx` y ejecutar:

```bash
python3 tools/build_seed.py
```

Luego revisar *Revisión de fuentes* antes de normalizar nombres o consolidar características repetidas.
