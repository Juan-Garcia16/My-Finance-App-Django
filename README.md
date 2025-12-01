# My Finance App Django

Aplicación web para gestión personal de finanzas desarrollada con Django. Permite llevar transacciones (ingresos/gastos), categorías, presupuestos mensuales, metas de ahorro y reportes visuales.

**Resumen rápido**
- **Stack**: Python + Django (5.2.x), TailwindCSS para estilos, Chart.js para gráficos, plantillas Django y Material Symbols.
- **Propósito**: ayudar al usuario a registrar ingresos/gastos, fijar presupuestos por categoría/mes, seguir metas de ahorro y ver reportes gráficos fáciles de interpretar.

**Módulos principales**
- **`users`**: gestión del perfil del usuario (modelo `Profile`), vistas relacionadas con el tablero (dashboard) y utilidades de usuario.
- **`categories`**: definición y gestión de categorías de transacciones (cada categoría tiene color y nombre).
- **`transactions`**: registro y edición de transacciones (`Ingreso` y `Gasto`). Incluye:
	- Formulario y vistas para crear/editar/eliminar transacciones.
	- `TransactionManager` (servicio) que centraliza la lógica de creación, edición y listado.
	- Plantilla `templates/transactions/transactions.html` que muestra lista filtrable y compacta.
	- Lógica para mostrar alertas visuales cuando una transacción afecta un `Presupuesto` cercano o sobrepasado.
- **`budgets`** (presupuestos): gestión de presupuestos mensuales por categoría.
	- Modelo `Presupuesto` con campos `usuario`, `categoria`, `mes` (formato `YYYY-MM`), `limite` y `gasto_actual`.
	- Señales que mantienen `gasto_actual` sincronizado cuando se crean/edita/eliminan transacciones.
	- CRUD de presupuestos con modal en la interfaz.
- **`goals`** (metas de ahorro): crear metas, aportar dinero y control de progreso.
	- Nota: existe una vista utilitaria `recalculate_progress_from_transactions` (en `goals/views.py`) que recalcula progreso desde transacciones siguiendo la convención `meta:<id>`, pero actualmente no es usada por otras partes del sistema; se recomienda convertirla en un comando de management o eliminarla si no se necesita.
- **`reports`**: vistas y plantillas que generan reportes por mes y por categoría.
	- Usa `Chart.js` para doughnuts y series de cashflow en dashboard/reports.

**Decisiones de arquitectura**
- Se usa una capa de *services* (por ejemplo `TransactionManager`) para encapsular lógica de negocio y mantener las vistas limpias.
- Las actualizaciones de `Presupuesto.gasto_actual` se realizan mediante *signals* para asegurar un único origen de la verdad.
- El formateo de valores (pesos colombianos) se hace tanto en vistas (`_format_cop`) como, en algunos puntos, con filtros JS para tooltips de Chart.js.

**Flujos y UX relevantes**
- Al crear/editar un gasto se verifica el presupuesto correspondiente al `mes` y `categoria`. Si el gasto lleva el total del presupuesto por encima de un umbral, se muestra:
	- Icono de advertencia (cerca de llenarse, por defecto >= 80%).
	- Icono de error (alcanzado/sobrepasado, >= 100%).
	- Mensajes flash (`messages.warning` / `messages.error`) cuando aplica.
- La lista de transacciones incluye iconos compactos con tooltip indicando el estado del presupuesto.

**Archivos y rutas clave**
- `transactions/views.py` — vistas: `transactions_list`, `transactions_create`, `transaction_edit`, `transaction_delete`.
- `transactions/services/transaction_manager.py` — lógica de creación/edición/listado de transacciones.
- `templates/transactions/transactions.html` — interfaz principal de transacciones y filtros cliente.
- `budgets/models.py` — modelo `Presupuesto`.
- `budgets/signals.py` — señales que sincronizan `gasto_actual` con transacciones.
- `goals/views.py` — gestión de metas (la vista `recalculate_progress_from_transactions` existe pero no se usa automáticamente).
- `reports/views.py` y `templates/reports/reports.html` — cálculo y render de reportes mensuales y gráficos.
- `users/views.py` — `dashboard_view` que construye series diarias y transacciones recientes.

**Instalación y ejecución (desarrollo)**
1. Crear y activar un entorno virtual (por ejemplo `venv`):

```bash
python -m venv venv
source venv/bin/activate
```

2. Instalar dependencias (si tienes `requirements.txt`):

```bash
pip install -r requirements.txt
```

3. Migrar y crear superusuario:

```bash
python manage.py migrate
python manage.py createsuperuser
```

4. Ejecutar servidor de desarrollo:

```bash
python manage.py runserver
```

5. URLs útiles durante desarrollo:
	- Transacciones: `/transactions/`
	- Crear transacción: `/transactions/create/`
	- Presupuestos (CRUD) — ruta depende de la app `budgets` y su URLconf
	- Metas: `/goals/` (la ruta de recalculado existe pero no se integra automáticamente en flujos)

**Estructura de carpetas (resumen)**
Ejemplo de organización esperada en la raíz del proyecto Django:

```
My-Finance-App-Django/
├─ manage.py
├─ requirements.txt
├─ README.md
├─ <project_name>/          # settings, urls, wsgi/asgi
├─ users/
├─ categories/
├─ transactions/
│  ├─ views.py
│  ├─ forms.py
│  ├─ services/
│  │  └─ transaction_manager.py
│  └─ templates/transactions/
├─ budgets/
│  ├─ models.py
│  ├─ signals.py
│  └─ templates/budgets/
├─ goals/
├─ reports/
└─ templates/
```

Nota: acabo de ver que generaste `requirements.txt` — úsalo para instalar dependencias con `pip install -r requirements.txt`.

- **Patrón de diseño y responsabilidades**
- Se sigue una aproximación en capas con una *service layer* para la lógica de negocio (ej. `TransactionManager`) y vistas/plantillas para la presentación. Ventajas:
	- Separa responsabilidades: vistas orquestan, servicios ejecutan reglas de negocio y modelos almacenan estado.
	- Facilita pruebas unitarias de la lógica de negocio (probar servicios aislados).
	- Señales (`signals`) se usan para mantener invariantes cruzadas (por ejemplo sincronizar `Presupuesto.gasto_actual` cuando cambian transacciones).

- **Buenas prácticas**
	- Mantener la lógica que modifica varios modelos en servicios o tareas, no directamente en vistas.
	- Mantener las señales simples y determinísticas; si la actualización es compleja, considerar tareas asíncronas.
	- Documentar comandos/acciones administrativas (p. ej. convertir `recalculate_progress_from_transactions` en `manage.py recalculate_goals`).
- Si solo necesitas recalcular progreso desde transacciones de vez en cuando, considera convertir `recalculate_progress_from_transactions` en un comando de management y eliminar la vista pública.
- Extraer la lógica de evaluación de presupuesto a `budgets/services.py` la hace reutilizable (actualmente está en `transactions/views.py` como helper, se puede mover si prefieres).
- Añadir tests unitarios para `TransactionManager`, signals de `budgets` y `reports/views.py` ayudará a mantener estabilidad al refactorizar.
- Si planeas notificaciones persistentes (email/alertas), añade un modelo `Notification` y una tarea asíncrona (Celery / RQ) para manejar envíos.

Si quieres, puedo:
- Mover el helper de evaluación de presupuesto a `budgets/services.py` para reutilizarlo desde `reports` y `dashboard`.
- Añadir un ejemplo de flujo práctico en el README y capturas de pantalla/ejemplos de comandos.
- Generar tests unitarios básicos para el helper y para las señales.

---

Proyecto mantenido por el autor en el repo `My-Finance-App-Django`.
