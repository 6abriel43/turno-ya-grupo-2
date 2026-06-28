# TurnoYa

TurnoYa es un sistema web de gestion de turnos medicos para una clinica pequeña.
Permite registrar pacientes, administrar medicos, solicitar turnos, aceptar turnos, 
registrar ausencias, reprogramar turnos afectados y consultar recordatorios.

## Stack
Tecnologia y version:
- Python 3.13+
- Django 5.1+
- SQLite (base de datos)
- Django ORM
- Bootstrap 5 (frontend)
- Git y GitHub

## Funcionalidades principales

- Registro, login y logout de usuarios.
- Perfiles diferenciados para pacientes, medicos y administradores.
- Listado de medicos con filtros por especialidad y obra social.
- Solicitud de turnos por pacientes.
- Listado de turnos propio para medicos.
- Aceptacion y cancelacion de turnos.
- Validacion de franjas horarias y ausencias al crear turnos.
- Historial clinico del paciente para medicos.
- Edicion de observaciones del turno.
- Registro de ausencias medicas.
- Reprogramacion automatica de turnos afectados por ausencias.
- Recordatorios para pacientes.
- Panel de administracion configurado para los modelos principales.
- Templates responsivos con Bootstrap 5.

## Instalacion y uso:

1. Clonar el repositorio:

```bash
git clone https://github.com/6abriel43/turno-ya-grupo-2.git
cd turno-ya-grupo-2
```

2. Crear y activar el entorno virtual:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Aplicar migraciones:

```bash
python manage.py migrate
```

5. Opcionalmente cargar datos iniciales:

```bash
python manage.py loaddata initial_data
```

6. Levantar el servidor:

```bash
python manage.py runserver
```

Panel Aplicacion: http://127.0.0.1:8000/

Panel Admin: http://127.0.0.1:8000/admin/

## Comandos de verificacion

```bash
python manage.py makemigrations --check --dry-run
python manage.py migrate
python manage.py test
python manage.py runserver
```

## Tests

El proyecto usa `django.test.TestCase`.

```bash
# Todos los test con detalle
python manage.py test -v 2

# Solo tests de modelos
python manage.py test app.tests.test_models -v 2

# Solo tests de vistas
python manage.py test app.tests.test_views -v 2

# Test de historial paciente
python manage.py test app.tests.test_historial_paciente -v 2
```

## Rutas principales

- `/` panel de inicio.
- `/medicos/` listado de medicos.
- `/medicos/<id>/` detalle de medico.
- `/pacientes/` listado de pacientes para medicos.
- `/pacientes/<id>/historial/` historial clinico del paciente.
- `/turno/nuevo/` solicitud de turno para pacientes.
- `/turnos/` listado de turnos para medicos.
- `/mis-turnos/` turnos del paciente autenticado.
- `/ausencias/` listado de ausencias para medicos.
- `/ausencias/nueva/` registro de ausencia.
- `/recordatorios/` panel de recordatorios para medicos.
- `/mis-recordatorios/` recordatorios del paciente autenticado.
- `/registro/` registro de paciente.
- `/accounts/login/` login.

## Modelos principales

- `Especialidad`
- `ObraSocial`
- `Medico`
- `Paciente`
- `FranjaHoraria`
- `Turno`
- `Ausencia`
- `Recordatorio`

Los modelos implementan metodos de validacion y negocio:
`validate()`, `new()`, `update()` y al menos un metodo propio segun corresponda.

## Integrantes Grupo 2:
- Nombre:         | Usuario GitHub: 
- Gabriel Guitian | [@usuario](https://github.com/6abriel43)
- Fabrizio Verdu  | [@usuario](https://github.com/Farvi-1986)
- Mateo Mazuela   | [@usuario](https://github.com/soyMat)
- Facundo Zamora  | [@usuario](https://github.com/Facunique)
- Luca Mechulan   | [@usuario](https://github.com/iLuka103)

## Notas de uso

- Las vistas privadas usan `LoginRequiredMixin`.
- Las vistas de medicos, pacientes y administracion validan permisos por rol.
- Los pacientes no pueden ver paneles operativos de medicos.
- Los medicos ven solo los turnos y datos que les corresponden, salvo usuarios staff o superusuarios.


## 🔑 Credenciales de prueba

> ⚠️ Solo para uso del corrector en entorno de desarrollo local.

| Rol      |  Usuario   |  Contraseña    |
|----------|------------|----------------|
| Admin    | `admin`    | `admin1234`    |
| Paciente | `paciente1`| `Paciente1234!`|
| Medico   | `medico1`  | `Medico1234!`  |


## 🧩 Decisiones de diseño

> *(Mínimo 200 palabras — completar antes de la entrega final)*

Describir aquí:
- Por qué eligieron este dominio:
Elegimos el dominio de un sistema de gestión de turnos médicos ("TurnoYa") porque es un problema muy habitual en el mundo real y nos permitía aplicar a fondo todo lo que vimos en la cursada. Nos dio la oportunidad de trabajar con varios roles (médicos, pacientes, admin) y manejar estados de los turnos que cambian en el tiempo (pendientes, reprogramados, cancelados).

- Cómo organizaron las responsabilidades entre modelos y vistas?
Tratamos de seguir la regla de Django: "modelos gordos, vistas flacas". Pusimos la lógica pesada de la aplicación y el patrón validate/new/update directamente en los modelos y usamos Managers personalizados para cosas como las estadísticas de la clínica. Las vistas las dejamos puramente para el flujo web, es decir, recibir la petición HTTP, verificar si el usuario tiene permiso y renderizar el template correspondiente enviando el contexto necesario.

- Qué validaciones decidieron poner en el modelo vs. en el formulario?
En los Modelos dejamos las reglas estrictas para mantener la integridad de la base de datos (campos nulos, largos máximos y las relaciones). Sin embargo, en los Formularios pusimos las reglas de negocio complejas, como verificar que la fecha de un turno no sea en el pasado o que no se reserve fuera de la franja horaria del médico. Hacerlo en los forms nos permite atajar los errores a tiempo y devolverle al usuario mensajes amigables en la pantalla, en lugar de que la aplicación tire un error del servidor.

- Cómo dividieron el trabajo entre los integrantes?
Para organizarnos, aplicamos un enfoque que se nos hiciera mas comodo y sencillo, usamos Inteligencia Artificial pasándole un contexto de nuestro avance con el Trabajo Practico, los requisitos, lo que razonamos que teniamos que hacer y algun que otro dato teorico para que nos ayude a desglosar el desarrollo en tareas más pequeñas y concretas. Con ese listado generado por la IA (de cada etapa), analizamos la propuesta dada, ajustamos las prioridades y nos repartimos los "tickets" basándonos en lo que cada uno entendía mejor o le resultaba más cómodo programar.

- Cualquier decisión de diseño no obvia (ej: por qué usaron FBV en lugar de CBV, cómo manejaron la relación User ↔ Paciente, etc.):
Una decisión importante fue cómo manejar a los usuarios. Decidimos no modificar el modelo User nativo de Django para no complicar la autenticación. En su lugar usamos "Estrategia de Perfil", creando los modelos Paciente y Medico y vinculándolos al usuario con un OneToOneField. Otra decisión importante fue usar 100% Vistas Basadas en Clases (CBV) combinadas con Mixins propios (como MedicoRequiredMixin o PacienteRequiredMixin). Esto nos ahorró tener que escribir un montón de condicionales if repetidos en cada vista para saber qué usuario estaba logueado