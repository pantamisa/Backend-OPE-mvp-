# ENTREGABLE #2: DISEÑO DE SISTEMAS DE INFORMACIÓN
**OpE — Sistema de Gestión y Monitoreo de Flota de Vehículos**

**Proyecto:** OpE — Sistema Innovador de Renta de Vehículos
**Integrantes:** Samuel Causil Londoño · Juan Pablo León Duque
**Docente:** Aníbal Antonio Torres Cañas
**Curso:** Diseño de Sistemas de Información
**Institución:** Instituto Tecnológico Metropolitano
**Fecha:** Abril 2026

---

## Tabla de Cambios del Proyecto
La siguiente tabla registra la evolución documental del proyecto OpE desde el Entregable 1, evidenciando las decisiones, correcciones y ampliaciones realizadas en cada versión.

| Versión | Entregable | Fecha | Responsable | Descripción del Cambio |
|---|---|---|---|---|
| v1.0 | Entregable 1 | Mar 3, 2026 | Samuel Causil / Juan Pablo León | Versión inicial: modelo verbal, requisitos, story mapping, casos de uso, diagrama de clases y prototipo Figma. |
| v1.1 | Revisión E1 | Mar 15, 2026 | Samuel Causil | Corrección de inconsistencias en requisitos funcionales RF-11 y RF-14. Ajuste en reglas de negocio RN-04. |
| v2.0 | Entregable 2 | Abr 22, 2026 | Samuel Causil / Juan Pablo León | Definición del MVP, priorización de historias de usuario, arquitectura C4 (4 niveles), modelo de base de datos, patrones de diseño GoF y prototipo funcional. |
| v2.1 | Refactoring BD | Abr 22, 2026 | Juan Pablo León | Refinamiento del diagrama de clases con incorporación de patrones Repository, Observer y Strategy. Actualización de entidades de dominio. |

---

## 1. Definición del Mínimo Producto Viable (MVP)
El MVP de OpE se define considerando las necesidades críticas del negocio identificadas en el Entregable 1: digitalizar el proceso de renta, garantizar el control básico del vehículo y conductor, y producir un reporte de ingresos. Las historias priorizadas en los Sprints 1 y 2 constituyen el MVP.

### 1.1 Criterios de Priorización
Se utilizó la técnica MoSCoW para priorizar:
- **Must Have (Sprint 1–2)**: funcionalidades sin las cuales el sistema no aporta valor alguno.
- **Should Have (Sprint 3)**: funcionalidades importantes que completan la propuesta de valor.
- **Could Have (Sprint 4)**: funcionalidades deseables que se incorporan si el tiempo lo permite.

### 1.2 Historias de Usuario Priorizadas (MVP - Sprints 1 y 2)
| ID | Historia | Actor | Prioridad | Requisitos | CU | Sprint |
|---|---|---|---|---|---|---|
| HU-01 | Registrar vehículo | Administrador | Alta | RF-01, RF-02, RF-03 | CU-01 | Sprint 1 |
| HU-02 | Registrar conductor | Administrador | Alta | RF-04, RF-05, RF-06 | CU-02 | Sprint 1 |
| HU-03 | Crear contrato de renta | Administrador | Alta | RF-07, RF-08, RF-09, RF-10 | CU-03 | Sprint 1 |
| HU-04 | Finalizar renta y facturar | Administrador | Alta | RF-09, RF-12 | CU-04 | Sprint 2 |
| HU-05 | Calcular tarifa automáticamente | Sistema | Alta | RF-09, RN-05 | CU-03 | Sprint 2 |
| HU-06 | Reporte básico de ingresos | Admin Contable | Alta | RF-19, RF-21 | CU-07 | Sprint 2 |

---

## 2. Arquitectura C4

### Nivel 1 — Diagrama de Contexto
El diagrama de contexto muestra el sistema OpE como una caja negra en relación con sus usuarios y sistemas externos.
**Enlace editable:** https://app.diagrams.net/#G_C4_Level1_OpE

*Explicación:* El sistema OpE recibe solicitudes de cuatro tipos de usuarios humanos. El Sistema GPS es el único actor puramente externo automatizado; suministra la telemetría que alimenta los módulos de monitoreo, alertas y cálculo de km. El servicio de correo centraliza las notificaciones de alerta.

### Nivel 2 — Diagrama de Contenedores
El nivel de contenedores descompone OpE en las aplicaciones y servicios de software que lo conforman, mostrando sus tecnologías y responsabilidades.
**Enlace editable:** https://app.diagrams.net/#G_C4_Level2_OpE

*Explicación:* La arquitectura de contenedores implementa el patrón de 3 capas (presentación, lógica, datos) con la adición de un adaptador GPS y una cola de tareas asíncronas. Esta separación garantiza escalabilidad y crecimiento modular. El backend Django implementa directamente los módulos del MVP.

### Nivel 3 — Diagrama de Componentes (API Backend)
El nivel de componentes descompone el contenedor 'API Backend' en sus módulos internos de Django.
**Enlace editable:** https://app.diagrams.net/#G_C4_Level3_OpE

*Explicación:* Los componentes corresponden a las aplicaciones Django del proyecto (`fleet.vehicles`, `fleet.drivers`, `fleet.contracts`, `fleet.billing`, `fleet.maintenance`, `fleet.reports`, `fleet.alerts`, `fleet.telemetry`). Cada uno encapsula una responsabilidad del dominio mapeada a un módulo del Entregable 1, aislando las distintas reglas de negocio y patrones.

### Nivel 4 — Código / Clases de Dominio
El nivel 4 refina el diagrama de clases del Entregable 1 incorporando los patrones de diseño seleccionados y las relaciones ORM.
**Enlace editable:** https://app.diagrams.net/#G_C4_Level4_OpE

*Explicación:* El diagrama de clases original se refina incorporando los atributos completos para implementar las reglas de negocio, se agregan las clases de patrón (TarifaStrategy, AlertaObserver, ReporteFacade, MantenimientoTemplate), y se establecen explícitamente las relaciones de dependencia.

---

## 3. Análisis y Selección de Patrones de Diseño GoF

### P-01: Patrón Repository (Comportamiento/Estructural)
- **Necesidad:** Desacoplar la capa de dominio de la capa de persistencia (ORM Django) para Vehículos, Conductores y Contratos.
- **Implementación:** `VehiculoRepository`, `ConductorRepository` para encapsular las llamadas al ORM.
- **Justificación:** Centraliza y estandariza las operaciones CRUD sin sobreingeniería, lo que facilita las pruebas.

### P-02: Patrón Strategy (Comportamiento)
- **Necesidad:** Calcular el costo de una renta de tres maneras (por hora, por día, por kilómetro) según el contrato (RN-05).
- **Implementación:** Clase abstracta `TarifaStrategy` con `TarifaHora`, `TarifaDia` y `TarifaKm`.
- **Justificación:** Evita condicionales anidados (if/else), permite agregar nuevos modos sin modificar código existente.

### P-03: Patrón Observer (Comportamiento)
- **Necesidad:** Al cerrar un contrato, ejecutar múltiples acciones automáticas (generar factura, actualizar horas, evaluar alertas).
- **Implementación:** Django Signals (`post_save`) sobre `Contrato`. Los observadores son `FacturaObserver`, `HorasConductorObserver`, etc.
- **Justificación:** Desacopla las responsabilidades. El proceso de cierre no necesita conocer las reglas de facturación o alertas.

### P-04: Patrón Facade (Estructural)
- **Necesidad:** Agregar datos de múltiples fuentes (Contrato, Mantenimiento, Factura, Telemetría) para el módulo de reportes.
- **Implementación:** Clase `ReporteService` (Facade) que expone métodos limpios para el `ReporteViewSet`.
- **Justificación:** Simplifica la interfaz del módulo de reportes ocultando la complejidad de las consultas SQL/ORM.

### P-05: Patrón Template Method (Comportamiento)
- **Necesidad:** Pasos comunes en el mantenimiento preventivo y correctivo, pero con lógica diferente en la reprogramación (RN-03).
- **Implementación:** `MantenimientoService.ejecutar_mantenimiento()` con método abstracto `calcular_proximo()`.
- **Justificación:** Evita duplicar código de registro y actualización, formalizando el proceso de mantenimiento.
