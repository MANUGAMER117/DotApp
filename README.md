# DotApp - prototipo funcional

Sistema Django para gestionar perfiles, reservas, inventario multibodega, alertas preventivas, devoluciones y entrega con firma digitalizada.

## Requisitos
- Python 3.13+
- Dependencias de `requirements.txt`

## Puesta en marcha

```bash
python -m venv env

# Windows
env\Scripts\activate

# Linux/macOS
source env/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Luego abre `http://127.0.0.1:8000/`.

El comando `seed_demo` carga colaboradores, perfiles, bodegas, referencias, inventario y una reserva de ejemplo.

## Flujo para la presentación
1. Dashboard: muestra indicadores y stock crítico.
2. Colaboradores: entra a Perfil y cambia tallas / próxima entrega.
3. Reservas: crea una reserva y confírmala.
4. Entrega: abre «Entregar / firmar», selecciona bodega, firma con mouse o táctil y genera el acta PDF.
5. Inventario: verifica que el stock se descuenta al firmar y que aparecen sugerencias de compra.
6. Devoluciones: registra una causal y comprueba el aumento del stock.
7. Alertas: emite una alerta y revisa el mensaje de correo en la consola del servidor.

## Requerimientos cubiertos
- RF-01: reservas, estados y notificación por correo de prueba.
- RF-02: próxima entrega, ventana preventiva de 30 días y alertas.
- RF-03: inventario por bodega/SKU/talla, mínimo y sugerencia de compra.
- RF-04: firma en canvas, fecha/hora, ID, geolocalización y acta PDF.
- RF-05: devoluciones y clasificación por causal.
- RNF-02: CSRF de Django y correo en entorno de desarrollo; producción requiere configuración real de TLS/cifrado.
- RNF-04: interfaz responsive y captura offline de firma mediante almacenamiento local con sincronización al recuperar conexión.

## requirements.txt
El archivo lista las dependencias directas del proyecto. Para regenerarlo desde un entorno ya instalado puedes usar:

```bash
pip freeze > requirements.txt
```

Para una entrega académica pequeña es preferible conservar un archivo mínimo con las dependencias directas, como el que ya se incluye: Django y ReportLab.

## Módulo Operadores
El módulo **Operadores** permite registrar al personal interno que administra DotApp (Administrador, Recursos Humanos, Bodega y Compras), editar sus datos y activar/desactivar su estado. Los roles son informativos en este prototipo; no implementan autenticación ni permisos diferentes por rol.

## ¿Qué hace cada sección?
- **Dashboard:** es el resumen operativo: colaboradores activos, reservas pendientes, inventario bajo, próximas entregas y actas generadas.
- **Operadores:** administra al personal interno que opera el sistema. Permite crear, editar y activar/desactivar operadores y registrar su rol.
- **Colaboradores:** contiene los empleados que reciben la dotación. Aquí se registran datos básicos, tallas, preferencias y fecha de próxima entrega.
- **Reservas:** gestiona la solicitud de una dotación, su confirmación, la entrega, la firma y la generación del acta PDF. Al firmar una entrega también se descuenta una unidad del inventario seleccionado.
- **Inventario:** controla existencias por bodega, SKU y talla. Permite registrar entradas de stock y muestra el punto de reorden y la sugerencia de compra.
- **Devoluciones:** registra cambios de talla, defectos, desgaste u otras causales y devuelve automáticamente una unidad al inventario de la bodega seleccionada.


### Corrección de navegación de Colaboradores
La navegación principal usa ahora la ruta explícita `/colaboradores/`. Se eliminó la inclusión duplicada de las URLs de la aplicación que provocaba que `/usuarios/` coincidiera primero con el Dashboard. Se conserva `/usuarios/` como alias compatible.
