# MyFinanceApp — Documentación Técnica

**Contexto del Desarrollo**

MyFinanceApp es una aplicación web para el control de finanzas personales. Permite a cada usuario gestionar transacciones (ingresos y gastos), categorías, metas de ahorro, presupuestos mensuales y generar reportes estadísticos y visuales por mes y por año.

**Integrantes del grupo**

- **Juan Pablo García** — Autor / Desarrollador principal

**Tecnologías y librerías implementadas**

- **Backend:** `Django 5.2.8`
- **Base de datos:** `PostgreSQL` (driver: `psycopg2-binary`)
- **Gestión de configuración:** `python-decouple`
- **Frontend:** Tailwind CSS (clases usadas en templates)
- **Dependencias listadas:** ver `requirements.txt`

Resumen de `requirements.txt`:

- `Django==5.2.8`
- `psycopg2-binary==2.9.11`
- `python-decouple==3.8`
- `asgiref==3.10.0`
- `sqlparse==0.5.3`

**Temática / Propósito**

Proveer una herramienta simple y centrada en el usuario final para visualizar y controlar su estado financiero mensual y anual, con atención a: seguimiento de transacciones, categorización, presupuestos por categoría/mes, metas de ahorro y reportes visuales (gráficas de líneas y torta).

**Flujo de Trabajo (resumen funcional por módulos)**

- **Módulo de Usuario**: Registro (nombre, correo, contraseña, saldo inicial), Login (usuario y contraseña). En el `dashboard` se muestra: balance total, ingresos totales mes actual, gastos totales mes actual, gráfica de ingresos/gastos por día, últimas 5 transacciones y botón para nueva transacción. Acceso a configuración de perfil y logout.
- **Módulo de Categorías**: Crear/editar/eliminar categorías (nombre, tipo ingreso/gasto, color). No se permiten duplicados por usuario.
- **Módulo de Transacciones**: Crear/editar/eliminar transacciones con: tipo (ingreso/gasto), categoría, monto, fecha, descripción. Afectan saldo del `Profile`, presupuestos y reportes. Listado con búsqueda y filtros (fechas, categoría, tipo).
- **Módulo de Metas (Goals)**: Crear metas con nombre, monto objetivo y fecha límite. Registrar aportes (no restan del saldo) que incrementan progreso y porcentaje de la meta.
- **Módulo de Presupuestos**: Crear presupuesto por categoría y mes (mes de año) con monto límite; muestra barra progresiva y estado (dentro, cerca, superado). Las transacciones del mes y categoría aumentan `gasto_actual`.
- **Módulo de Reportes**: Vista por mes con ingresos totales, gastos totales, ahorro neto (ingresos - gastos), gráficos de torta por categoría (gastos e ingresos) y estado de presupuestos. Navegador por mes/año.

**Requerimientos funcionales**

- RF1: Registro de usuario con `nombre`, `email`, `contraseña` y `saldo_inicial`.
- RF2: Login y logout seguro (redirecciones configuradas en `settings.py`).
- RF3: Visualización de `dashboard` con métricas (balance, ingresos, gastos, gráfica diaria, últimas 5 transacciones).
- RF4: CRUD de `Categorías` por usuario (nombre, tipo, color); evitar duplicados.
- RF5: CRUD de `Transacciones` (ingresos/gastos) con impacto en el saldo del `Profile`.
- RF6: Búsqueda y filtrado de transacciones por atributos, rango de fechas, categoría y tipo.
- RF7: CRUD de `Metas` y registro de aportes que incrementen su progreso.
- RF8: CRUD de `Presupuestos` por categoría/mes y cálculo de `gasto_actual` impactado por transacciones.
- RF9: Reportes mensuales con gráficas (torta y líneas) y navegador por mes/año.

**Requerimientos no funcionales**

- RNF1: Persistencia de datos en PostgreSQL.
- RNF2: Seguridad básica proporcionada por `Django Auth` (hashing de contraseñas, sesiones).
- RNF3: Respuesta de la UI responsiva (uso de Tailwind CSS para estilos y layout ligero).
- RNF4: Código organizado por apps (`users`, `transactions`, `categories`, `budgets`, `goals`, `reports`).
- RNF5: Rotinas en los servicios para encapsular negocio (clases `*Manager` para lógica de dominio).
- RNF6: Validaciones para evitar duplicidad de categorías y evitar eliminar entidades con dependencias.

**Estructura de modelos y relaciones (resumen extraído del código)**

- `Profile` (`users.models.Profile`)
  - Atributos: `user (OneToOneField->auth.User)`, `moneda_preferida`, `saldo_inicial`, `saldo_actual`
  - Métodos: `actualizar_saldo(monto)`
  - Colaboradores: `Transaccion` (`Ingreso`, `Gasto`), `Category`, `Presupuesto`, `MetaAhorro`

- `Category` (`categories.models.Category`)
  - Atributos: `usuario (ForeignKey->Profile)`, `nombre`, `tipo`, `color`
  - Colaboradores: `Ingreso`, `Gasto`, `Presupuesto`

- `Transaccion` (abstracto) / `Ingreso`, `Gasto` (`transactions.models`)
  - Atributos: `usuario (FK->Profile)`, `categoria (FK->Category)`, `monto`, `fecha`, `descripcion`
  - Métodos: `get_monto()`, `registrar()` (implementado en `Ingreso` y `Gasto` para actualizar saldo)
  - Colaboradores: `Profile`, `Category`, `Presupuesto` (indirectamente)

- `Presupuesto` (`budgets.models.Presupuesto`)
  - Atributos: `usuario (FK->Profile)`, `categoria (FK->Category)`, `mes`, `limite`, `gasto_actual`
  - Métodos: `actualizar_gasto(monto)`, `verificar_limite()`
  - Colaboradores: `Category`, `Transaccion`

- `MetaAhorro` (`goals.models.MetaAhorro`)
  - Atributos: `usuario (FK->Profile)`, `nombre`, `monto_objetivo`, `fecha_limite`, `progreso`
  - Métodos: `actualizar_progreso(monto)`, `porcentaje_progreso()`

**Tarjetas CRC (Clase — Responsabilidades — Colaboradores)**

                                  Profile
---------------------------------------------------------------------
RESPONSABILIDADES:            |  COLABORADORES
- Mantener `saldo_actual`      | `auth.User` (OneToOne)
- Actualizar saldo con trans.  | `Ingreso`, `Gasto` (llaman `actualizar_saldo`)
atributos: user, moneda_preferida, | `Presupuesto` (consulta/actualiza gasto_actual)
saldo_inicial, saldo_actual      | `MetaAhorro` (relacionado por usuario)
metodos: actualizar_saldo(monto)


                                  Category
---------------------------------------------------------------------
RESPONSABILIDADES:            |  COLABORADORES
- Guardar metadata de categoría | `Profile` (propietario)
- Evitar duplicados por usuario| `Ingreso`, `Gasto` (FK), `Presupuesto`
atributos: usuario, nombre, tipo, color | metodos CRUD en `CategoryManager`


                                  Ingreso / Gasto
---------------------------------------------------------------------
RESPONSABILIDADES:            |  COLABORADORES
- Registrar transacción         | `Profile` (actualizar saldo)
- Mantener datos transacción    | `Category` (FK)
atributos: usuario, categoria, monto, fecha, descripcion | `TransactionManager` (crear/listar/editar/eliminar)
metodos: registrar() (aumenta o disminuye saldo)


                                  Presupuesto
---------------------------------------------------------------------
RESPONSABILIDADES:            |  COLABORADORES
- Controlar límite por mes      | `Profile` (pertenece a un usuario)
- Actualizar `gasto_actual`     | `Category` (FK)
atributos: usuario, categoria, mes, limite, gasto_actual | `BudgetManager` (crear / estado)
metodos: actualizar_gasto(monto), verificar_limite()


                                  MetaAhorro
---------------------------------------------------------------------
RESPONSABILIDADES:            |  COLABORADORES
- Mantener progreso de meta     | `Profile` (propietario)
- Calcular porcentaje y evitar overflow | `GoalManager` (crear / añadir progreso)
atributos: usuario, nombre, monto_objetivo, fecha_limite, progreso | metodos: actualizar_progreso(monto), porcentaje_progreso()


**Diagrama de clases (texto / relaciones principales)**

- `auth.User` 1 --- 1 `Profile`
- `Profile` 1 --- * `Category`
- `Profile` 1 --- * `Ingreso`
- `Profile` 1 --- * `Gasto`
- `Profile` 1 --- * `Presupuesto`
- `Profile` 1 --- * `MetaAhorro`
- `Category` 1 --- * `Ingreso` / `Gasto`
- `Category` 1 --- * `Presupuesto`

(Sugerencia: si desea un diagrama visual, puedo generar un diagrama PlantUML o un PNG a partir de esta estructura.)

**Casos de Uso (lista resumida)**

ID | Actor Principal | Nombre
---|-----------------|-------
UC01 | Usuario | Registro de cuenta
UC02 | Usuario | Login al sistema
UC03 | Usuario | Ver Dashboard
UC04 | Usuario | Crear/Cambiar categoría
UC05 | Usuario | Crear transacción (ingreso/gasto)
UC06 | Usuario | Editar/Eliminar transacción
UC07 | Usuario | Crear meta de ahorro
UC08 | Usuario | Aportar a meta
UC09 | Usuario | Crear presupuesto por categoría/mes
UC10 | Usuario | Ver Reportes mensuales


Formato detallado de casos de uso

Nombre: Registro de cuenta
Codigo: UC01
Creado por: Juan Pablo García
Fecha de Creacion: 01-12-2025
Actores: Usuario (no autenticado)
Descripcion: Permite a un usuario crear una cuenta proporcionando nombre de usuario, correo, contraseña y saldo inicial.
Disparador: Usuario accede a la página de registro y envía el formulario.
Pre-Condiciones: El usuario no debe estar autenticado; el nombre/correo no deben existir ya.
Post-Condiciones: Usuario creado en `auth.User` y `Profile` con `saldo_inicial` establecido; sesión iniciada o redirigido al login.
Flujo normal:
1. Usuario llena formulario con nombre, correo, contraseña y saldo inicial.
2. Sistema valida datos y crea `User` y `Profile`.
3. Sistema redirige al dashboard o login.
Flujos Alternativos:
- Si correo/usuario ya existe -> mostrar error y pedir corrección.
- Si datos inválidos -> mostrar validaciones.


Nombre: Crear transacción
Codigo: UC05
Creado por: Juan Pablo García
Fecha de Creacion: 01-12-2025
Actores: Usuario autenticado
Descripcion: Permite registrar una transacción (ingreso o gasto) ligada a una categoría y fecha.
Disparador: Usuario completa el formulario de nueva transacción y lo envía.
Pre-Condiciones: Usuario autenticado; categoría existente para el usuario.
Post-Condiciones: Nueva `Ingreso` o `Gasto` creada; `Profile.saldo_actual` actualizado; `Presupuesto.gasto_actual` actualizado si aplica; reportes considerarán la transacción.
Flujo normal:
1. Usuario selecciona tipo, categoría, monto, fecha y descripción.
2. Sistema valida datos y crea objeto `Ingreso` o `Gasto`.
3. Se ejecuta `registrar()` que modifica saldo del `Profile`.
4. Sistema muestra confirmación y actualiza vistas afectadas.
Flujos Alternativos:
- Si la categoría no pertenece al usuario -> error.
- Si hay validaciones de monto -> error.


Nombre: Crear presupuesto
Codigo: UC09
Creado por: Juan Pablo García
Fecha de Creacion: 01-12-2025
Actores: Usuario autenticado
Descripcion: Crear un límite de gasto para una categoría en un mes específico.
Disparador: Usuario crea un presupuesto desde el panel de presupuestos.
Pre-Condiciones: Usuario autenticado; categoría existente.
Post-Condiciones: `Presupuesto` creado con `gasto_actual` inicializado en 0.
Flujo normal:
1. Usuario elige categoría, mes y monto límite.
2. Sistema valida y crea `Presupuesto`.
3. Si se registran transacciones posteriores para la categoría/mes, `gasto_actual` se actualiza.
Flujos Alternativos:
- Si ya existe un presupuesto para la misma categoría y mes -> opción para editar o error.


**Resúmen de organización del código (para entregables y lectura rápida)**

- Aplicaciones principales: `users/`, `transactions/`, `categories/`, `budgets/`, `goals/`, `reports/`.
- Lógica de negocio encapsulada en `services/*_manager.py` por cada app: `TransactionManager`, `CategoryManager`, `BudgetManager`, `GoalManager`, `UserManagerService`.
- Templates centralizados en `templates/` con subcarpetas por módulo.
- Configuración en `MyFinanceApp/settings.py` (uso de `decouple` para vars sensibles y `DATABASES` para PostgreSQL).

**Instrucciones de despliegue (local)**

1. Crear entorno virtual e instalar dependencias:

```bash
python -m venv ./venv
source ./venv/bin/activate
pip install -r requirements.txt
```

2. Configurar variables de entorno (ejemplo con `.env` usando `python-decouple`):

```
SECRET_KEY=tu_secret_key
DEBUG=True
DB_NAME=tu_db
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

3. Migraciones y creación de superusuario:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

4. Ejecutar servidor de desarrollo:

```bash
python manage.py runserver
```

5. (Opcional) Configurar compilación de assets Tailwind según su flujo (no incluido explícitamente en `requirements.txt`).

**Notas y recomendaciones**

- Si necesita diagramas UML o imágenes para incluir en la entrega, puedo generar PlantUML y exportar PNG/SVG con las relaciones extraídas.
- Puedo agregar nombres reales de integrantes del grupo si me los proporciona para la sección `Integrantes`.
- Si desea, genero un `docs/` con diagramas y plantillas de casos de prueba.

---

Si quiere que inserte este `README.md` en otro formato (PDF, DOCX) o que agregue imágenes (diagramas UML/PlantUML), indíquelo y lo genero.
