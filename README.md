# SFTP Import SQL

Proyecto Python para consolidar archivos CSV ubicados bajo jerarquía de carpetas en un servidor SFTP hacia SQL Server.

## Flujo

1. Conecta al SFTP.
2. Recorre jerarquía de carpetas recursivamente.
3. Selecciona archivos cuyo nombre inicia con `data_`.
4. Descarga un archivo a la vez a `temp/`.
5. Valida que el header coincida con el schema configurado.
6. Carga por chunks a SQL Server.
7. Agrega metadata de archivo y corrida.
8. Registra auditoria por archivo.

Cada archivo se carga dentro de una transaccion. Si falla durante descarga,
validacion o insercion, sus filas parciales se revierten, se marca como `FAILED`
y el proceso continua con el siguiente archivo.

## Preparacion local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item config\config.example.yaml config\config.local.yaml
```

Edita `config/config.local.yaml` con credenciales, servidor SQL y columnas reales del CSV.

## Crear tablas

Antes de ejecutar el proceso, ajusta `sql/001_create_tables.sql` con las columnas reales del CSV y ejecutalo en SQL Server.

Tambien ajusta la seccion `schema.columns` de `config/config.local.yaml` para que
coincida exactamente con el header del CSV, en el mismo orden.

## Ejecutar

```powershell
python -m src.main --config config/config.local.yaml
```

## Validacion inicial recomendada

1. Probar primero con 2 o 3 archivos en una carpeta SFTP controlada.
2. Confirmar que el conteo de filas en SQL Server coincida con los CSV.
3. Revisar `dbo.sftp_import_audit` para validar estados, filas y errores.
4. Revisar el archivo generado en `logs/`.

## Notas

- La tabla consolidada se trunca al inicio de cada corrida si `truncate_target_on_start` esta en `true`.
- La tabla de auditoria conserva el historico.
- Si un archivo falla, se registra como `FAILED` y el proceso continua con el siguiente archivo.
