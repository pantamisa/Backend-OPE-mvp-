const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageNumber, PageBreak, LevelFormat,
} = require('docx');
const fs = require('fs');

// ─── Paleta ───────────────────────────────────────────────────────────────────
const C = {
  navy:      "0D2137",
  blue:      "1A56A0",
  lightBlue: "2E86C1",
  accent:    "D6EAF8",
  accent2:   "EBF5FB",
  orange:    "CA6F1E",
  green:     "1E8449",
  lightGreen:"D5F5E3",
  red:       "B03A2E",
  lightRed:  "FADBD8",
  yellow:    "F9E79F",
  gray:      "566573",
  lightGray: "F2F3F4",
  white:     "FFFFFF",
  black:     "17202A",
  code:      "ECF0F1",
};

const thin  = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const thick = { style: BorderStyle.SINGLE, size: 6, color: C.blue };
const brd   = { top: thin, bottom: thin, left: thin, right: thin };

// ─── Helpers ──────────────────────────────────────────────────────────────────
const gap = (b=160,a=80) => new Paragraph({ children:[new TextRun("")], spacing:{before:b,after:a} });
const pb  = () => new Paragraph({ children:[new PageBreak()] });

function h1(t) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text: t, bold: true, size: 34, font: "Arial", color: C.navy })],
    spacing: { before: 400, after: 200 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: C.blue, space: 1 } },
  });
}
function h2(t) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text: t, bold: true, size: 27, font: "Arial", color: C.blue })],
    spacing: { before: 280, after: 140 },
  });
}
function h3(t) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    children: [new TextRun({ text: t, bold: true, size: 23, font: "Arial", color: C.orange })],
    spacing: { before: 200, after: 100 },
  });
}
function body(t, opts={}) {
  return new Paragraph({
    children: [new TextRun({ text: t, size: 22, font: "Arial", color: C.black, ...opts })],
    spacing: { before: 80, after: 80 },
    alignment: AlignmentType.JUSTIFIED,
  });
}
function note(t, bg=C.accent2, color=C.blue) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    rows: [new TableRow({ children: [new TableCell({
      borders: brd, shading: { fill: bg, type: ShadingType.CLEAR },
      margins: { top: 100, bottom: 100, left: 180, right: 180 },
      children: [new Paragraph({ children: [new TextRun({ text: t, size: 20, font: "Arial", color, bold: true })], spacing:{before:0,after:0} })]
    })]})]
  });
}
function codeBlock(lines) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    rows: [new TableRow({ children: [new TableCell({
      borders: { top: thick, bottom: thick, left: thick, right: thick },
      shading: { fill: "1E2A38", type: ShadingType.CLEAR },
      margins: { top: 120, bottom: 120, left: 200, right: 200 },
      children: lines.map(l => new Paragraph({
        children: [new TextRun({ text: l, size: 19, font: "Courier New", color: "A8D8EA" })],
        spacing: { before: 20, after: 20 },
      }))
    })]})]
  });
}
function step(num, title, desc) {
  return [
    new Paragraph({
      children: [
        new TextRun({ text: `Paso ${num}  `, bold: true, size: 22, font: "Arial", color: C.blue }),
        new TextRun({ text: title, bold: true, size: 22, font: "Arial", color: C.black }),
      ],
      spacing: { before: 160, after: 60 },
    }),
    body(desc),
  ];
}
function hCell(t, w, bg=C.navy) {
  return new TableCell({
    borders: brd, width:{ size:w, type:WidthType.DXA },
    shading: { fill:bg, type:ShadingType.CLEAR },
    margins: { top:100, bottom:100, left:120, right:120 },
    children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children:[new TextRun({ text:t, bold:true, color:C.white, size:20, font:"Arial" })] })]
  });
}
function dCell(t, w, bg=C.white, bold=false, color=C.black) {
  return new TableCell({
    borders: brd, width:{ size:w, type:WidthType.DXA },
    shading: { fill:bg, type:ShadingType.CLEAR },
    margins: { top:80, bottom:80, left:120, right:120 },
    children: [new Paragraph({ children:[new TextRun({ text:t, bold, color, size:20, font:"Arial" })] })]
  });
}
function bul(t, level=0) {
  return new Paragraph({
    numbering:{ reference:"bullets", level },
    children:[new TextRun({ text:t, size:22, font:"Arial", color:C.black })],
    spacing:{ before:50, after:50 },
  });
}
function num(t, level=0) {
  return new Paragraph({
    numbering:{ reference:"numbers", level },
    children:[new TextRun({ text:t, size:22, font:"Arial", color:C.black })],
    spacing:{ before:60, after:60 },
  });
}

// ─── PORTADA ─────────────────────────────────────────────────────────────────
function cover() {
  return [
    gap(2400, 0),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{before:0,after:200},
      children:[new TextRun({ text:"SOP — PROCEDIMIENTO ESTÁNDAR DE OPERACIÓN", bold:true, size:28, font:"Arial", color:C.gray })] }),
    new Paragraph({ alignment:AlignmentType.CENTER, spacing:{before:0,after:100},
      children:[new TextRun({ text:"Desarrollo del Backend OpE con", size:32, font:"Arial", color:C.lightBlue })] }),
    new Paragraph({
      alignment:AlignmentType.CENTER, spacing:{before:0,after:600},
      border:{ bottom:{ style:BorderStyle.SINGLE, size:10, color:C.blue, space:1 } },
      children:[new TextRun({ text:"Google Antigravity", bold:true, size:56, font:"Arial", color:C.navy })]
    }),
    gap(400,0),
    ...[
      ["Proyecto",      "OpE — Sistema de Gestión y Monitoreo de Flota"],
      ["Documento",     "SOP-OPE-BE-001  v1.0"],
      ["Basado en",     "Entregable #1 y #2 — DSI — ITM 2026"],
      ["Elaborado por", "Samuel Causil Londoño · Juan Pablo León Duque"],
      ["Fecha",         "Abril 22, 2026"],
      ["Herramienta",   "Google Antigravity (Public Preview) + Django 4.2 + DRF"],
    ].map(([k,v]) => new Paragraph({
      alignment:AlignmentType.CENTER, spacing:{before:80,after:80},
      children:[
        new TextRun({ text:k+":  ", bold:true, size:24, font:"Arial", color:C.blue }),
        new TextRun({ text:v, size:24, font:"Arial", color:C.gray }),
      ]
    })),
    pb(),
  ];
}

// ─── SECCIÓN 0 — OBJETIVO Y ALCANCE ──────────────────────────────────────────
function seccionObjetivo() {
  return [
    h1("0. Objetivo y Alcance del SOP"),
    gap(),
    body("Este documento describe paso a paso cómo usar Google Antigravity para construir el backend completo del sistema OpE, siguiendo al pie de la letra los casos de uso, requisitos funcionales, reglas de negocio y modelos definidos en los Entregables 1 y 2 del curso Diseño de Sistemas de Información (ITM, 2026)."),
    gap(120),
    h2("0.1 ¿Qué es Google Antigravity?"),
    body("Google Antigravity es un IDE agente-primero lanzado en noviembre de 2025. A diferencia de asistentes de código tradicionales, en Antigravity los agentes de IA pueden planear, escribir código, ejecutar comandos en terminal y verificar resultados en el navegador de forma autónoma y asíncrona. Opera sobre el modelo Gemini 3.1 Pro (y soporta Claude Sonnet 4.6 y GPT-OSS 120B como alternativas)."),
    gap(80),
    body("Tiene dos vistas principales: el Editor View (IDE clásico con asistente lateral) y el Agent Manager (\"Mission Control\" para orquestar múltiples agentes en paralelo). Para este proyecto usaremos principalmente el Agent Manager en modo Planning, que genera un Plan de Implementación verificable antes de escribir cualquier línea de código."),
    gap(160),
    h2("0.2 Alcance del Backend OpE"),
    body("El backend cubre exactamente el MVP definido en el Entregable 2 (Sprints 1 y 2) más la infraestructura base necesaria para los Sprints 3 y 4:"),
    bul("CU-01 Registrar Vehículo  →  App fleet.vehicles"),
    bul("CU-02 Registrar Conductor  →  App fleet.drivers"),
    bul("CU-03 Crear Contrato de Renta  →  App fleet.contracts (Strategy Pattern)"),
    bul("CU-04 Finalizar Renta  →  App fleet.contracts (Observer Pattern via Django signals)"),
    bul("CU-05 Monitoreo GPS  →  App fleet.telemetry (Sprint 3)"),
    bul("CU-06 Registrar Mantenimiento  →  App fleet.maintenance (Template Method)"),
    bul("CU-07 Reporte de Rentabilidad  →  App fleet.reports (Facade Pattern)"),
    bul("CU-08 Alertas Automáticas  →  App fleet.alerts (Observer Pattern)"),
    gap(160),
    h2("0.3 Restricciones y Reglas de Negocio que el Backend debe hacer cumplir"),
    new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[1200,3600,4560],
      rows:[
        new TableRow({ tableHeader:true, children:[hCell("ID",1200),hCell("Regla",3600),hCell("Implementación Django",4560)] }),
        ...([
          ["RN-01","Un vehículo no puede tener más de una renta activa simultánea.","UNIQUE INDEX parcial en Contrato + validación en ContratoSerializer.validate()"],
          ["RN-02","Un conductor no puede exceder el máximo de horas/día.","Validación en ContratoSerializer + signal post_save en Contrato."],
          ["RN-03","Mantenimiento preventivo obligatorio al alcanzar km definido.","Celery Beat task que revisa km_acumulado diariamente."],
          ["RN-04","No iniciar renta si el vehículo tiene mantenimiento pendiente.","Validación en ContratoSerializer.validate_vehiculo_id()"],
          ["RN-05","Costo de renta por hora, día o km según contrato.","Patrón Strategy: TarifaHora, TarifaDia, TarifaKm."],
          ["RN-06","Costos de mantenimiento asociados obligatoriamente a un vehículo.","FK NOT NULL vehiculo_id en modelo Mantenimiento."],
          ["RN-07","Bloquear vehículos marcados como fuera de servicio.","Estado 'fuera_de_servicio' + validación en ContratoSerializer."],
          ["RN-08","Multas asociadas al contrato correspondiente.","Modelo Penalizacion con FK a Contrato."],
        ].map((r,i) => new TableRow({ children:[
          dCell(r[0],1200,i%2===0?C.accent2:C.white,true,C.blue),
          dCell(r[1],3600,i%2===0?C.accent2:C.white),
          dCell(r[2],4560,i%2===0?C.accent2:C.white),
        ]})))
      ]
    }),
    pb(),
  ];
}

// ─── SECCIÓN 1 — INSTALACIÓN ─────────────────────────────────────────────────
function seccionInstalacion() {
  return [
    h1("1. Instalación y Configuración de Google Antigravity"),
    gap(),
    note("Requisitos previos: Chrome instalado, cuenta personal Gmail, sistema operativo macOS 12+, Windows 10+ o Ubuntu 22.04+.", C.lightGreen, C.green),
    gap(200),

    h2("1.1 Descargar e Instalar Antigravity"),
    ...step("1","Abrir la página de descarga","Ve a https://antigravity.google/download desde Chrome. Selecciona el instalador de tu sistema operativo (macOS .dmg, Windows .exe, Linux .deb/.rpm)."),
    ...step("2","Ejecutar el instalador","Lanza el instalador descargado. En macOS arrastra Antigravity a Applications. En Windows sigue el asistente. En Linux: sudo dpkg -i antigravity_*.deb"),
    ...step("3","Primer lanzamiento","Abre Antigravity. Verás el asistente de configuración inicial. Haz clic en Next en cada pantalla."),
    gap(160),

    h2("1.2 Configuración del Agente (ajustes recomendados para OpE)"),
    body("En la pantalla 'How do you want to use the Antigravity agent?' selecciona los siguientes ajustes para trabajar de forma segura con el backend de Django:"),
    gap(100),
    new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[2800,3200,3360],
      rows:[
        new TableRow({ tableHeader:true, children:[hCell("Política",2800),hCell("Opción recomendada",3200),hCell("Por qué",3360)] }),
        ...([
          ["Terminal Execution Policy","Request Review","Evita que el agente ejecute migraciones o comandos de BD sin tu aprobación."],
          ["Review Policy","Review-driven development","El agente pide aprobación antes de cada fase crítica. Ideal para proyectos académicos."],
          ["JavaScript Execution","Request Review","Controla cuándo el agente abre el navegador integrado para verificar la API."],
        ].map((r,i)=>new TableRow({ children: r.map((v,j)=>dCell(v,[2800,3200,3360][j],i%2===0?C.accent2:C.white,j===0)) })))
      ]
    }),
    gap(200),
    ...step("4","Instalar extensión de herramientas de línea de comandos","En la pantalla 'Configure your Editor', activa 'Command Line' para poder abrir Antigravity con el comando agy desde la terminal. Esto facilita abrir el proyecto Django directamente."),
    ...step("5","Iniciar sesión con Gmail","Haz clic en 'Sign in to Google' y autentica con tu cuenta Gmail personal. Antigravity es gratuito en Public Preview. Después de autenticarte regresa automáticamente a la aplicación."),
    ...step("6","Aceptar Términos de Uso","Lee y acepta los Terms of Use. Luego haz clic en Next para llegar al Agent Manager."),
    gap(160),
    note("Nota sobre cuotas (abril 2026): Antigravity introdujo un sistema de créditos en marzo 2026. La cuenta gratuita tiene cuotas con recarga periódica. Si ves el mensaje 'quota exhausted', espera o activa el plan Pro ($20/mes) para continuar.", C.yellow, C.orange),
    pb(),
  ];
}

// ─── SECCIÓN 2 — SETUP DEL PROYECTO ──────────────────────────────────────────
function seccionSetup() {
  return [
    h1("2. Configurar el Workspace del Proyecto Django en Antigravity"),
    gap(),

    h2("2.1 Crear la Estructura Inicial del Proyecto"),
    body("Antes de delegarle al agente, crea la estructura de carpetas base en tu máquina. Antigravity trabajará sobre este workspace."),
    gap(120),
    codeBlock([
      "# En tu terminal (fuera de Antigravity por ahora):",
      "mkdir ope-backend && cd ope-backend",
      "python -m venv venv",
      "source venv/bin/activate          # Windows: venv\\Scripts\\activate",
      "pip install django djangorestframework psycopg2-binary",
      "pip install djangorestframework-simplejwt celery redis django-celery-beat",
      "pip install reportlab openpyxl pytest-django factory-boy",
      "django-admin startproject ope_config .",
    ]),
    gap(200),

    h2("2.2 Abrir el Workspace en Antigravity"),
    ...step("1","Abrir Agent Manager","Lanza Antigravity. Verás el Agent Manager (Mission Control). Haz clic en 'Open Workspace'."),
    ...step("2","Seleccionar la carpeta del proyecto","Navega hasta la carpeta ope-backend que creaste y selecciónala. Antigravity indexará los archivos del proyecto. Verás el directorio en la barra lateral del Editor View."),
    ...step("3","Verificar workspace activo","En la esquina superior izquierda del Agent Manager confirma que el workspace muestra 'ope-backend'. Todas las misiones que crees a continuación operarán sobre este directorio."),
    gap(160),

    h2("2.3 Crear el archivo AGENTS.md (Contexto Persistente)"),
    body("Antigravity lee el archivo AGENTS.md del proyecto para mantener contexto entre sesiones. Esto es fundamental para que el agente recuerde la arquitectura del proyecto y los patrones de diseño definidos en el Entregable 2. Crea este archivo en la raíz del proyecto:"),
    gap(100),
    codeBlock([
      "# ope-backend/AGENTS.md",
      "# Contexto persistente del proyecto OpE para Antigravity",
      "",
      "## Proyecto",
      "Sistema de Gestión y Monitoreo de Flota de Vehículos (OpE).",
      "Backend: Django 4.2 + Django REST Framework 3.14 + PostgreSQL 15.",
      "",
      "## Reglas de arquitectura",
      "- SIEMPRE usar el patrón Repository para acceso a datos.",
      "- El cálculo de tarifas de renta usa el patrón Strategy (TarifaHora, TarifaDia, TarifaKm).",
      "- Los efectos secundarios del cierre de contrato se manejan con Django signals (Observer).",
      "- Los reportes usan una clase ReporteService como Facade.",
      "- El mantenimiento usa Template Method (MantenimientoPreventivo / MantenimientoCorrectivo).",
      "",
      "## Convenciones",
      "- Nombres de modelos en español con snake_case para campos.",
      "- Cada app Django tiene: models.py, serializers.py, views.py, urls.py, services.py, tests.py.",
      "- NUNCA poner lógica de negocio en las vistas (ViewSets).",
      "- Las validaciones de reglas de negocio van en los serializers (método validate).",
      "",
      "## Apps del proyecto",
      "fleet/vehicles  → Vehiculo",
      "fleet/drivers   → Conductor",
      "fleet/contracts → Contrato, Factura, Penalizacion",
      "fleet/maintenance → Mantenimiento",
      "fleet/reports   → Reporte (Facade)",
      "fleet/alerts    → Alerta",
      "fleet/telemetry → Telemetria",
    ]),
    gap(200),
    note("Tip Antigravity: El agente lee AGENTS.md automáticamente al inicio de cada conversación. Mantenerlo actualizado es equivalente a darle un briefing antes de cada misión.", C.lightGreen, C.green),
    pb(),
  ];
}

// ─── SECCIÓN 3 — MISIONES POR CASO DE USO ────────────────────────────────────
function seccionMisiones() {
  const missions = [
    {
      id:"MISIÓN 1", cu:"CU-01 y CU-02", title:"Modelos Vehiculo y Conductor + Endpoints CRUD",
      sprint:"Sprint 1", hu:"HU-01, HU-02",
      prompt:[
        "Crea la app fleet/vehicles y fleet/drivers en el proyecto Django.",
        "Para fleet/vehicles crea el modelo Vehiculo con los campos:",
        "  placa (unique, max_length=10), modelo, marca, anio (SmallIntegerField),",
        "  tipo (choices: particular|bus|camion|motocicleta|furgon),",
        "  capacidad (PositiveSmallIntegerField), color, km_inicial (Decimal),",
        "  km_acumulado (Decimal default 0), estado (choices: disponible|en_renta|mantenimiento|fuera_de_servicio),",
        "  fecha_registro (auto_now_add), updated_at (auto_now).",
        "Para fleet/drivers crea el modelo Conductor con:",
        "  cedula (unique), nombre, apellido, num_licencia (unique),",
        "  categoria_licencia, fecha_venc_licencia (DateField, null=True),",
        "  telefono, email, estado (choices: activo|inactivo|suspendido),",
        "  horas_hoy (Decimal default 0), horas_totales (Decimal default 0),",
        "  limite_horas_dia (Decimal default 8.00).",
        "Crea serializers con validación de unicidad, ViewSets con DRF y rutas REST.",
        "Registra en INSTALLED_APPS y genera la migración.",
        "Crea tests básicos con pytest-django y factory_boy para cada modelo.",
      ],
      req:["RF-01","RF-02","RF-03","RF-04","RF-05","RN-07"],
      accept:["GET /api/vehiculos/ retorna lista","POST /api/vehiculos/ valida placa única","GET /api/conductores/{id}/ retorna conductor","POST con cédula duplicada retorna HTTP 400"],
    },
    {
      id:"MISIÓN 2", cu:"CU-03 y CU-04", title:"Contratos de Renta con Patrón Strategy",
      sprint:"Sprint 1–2", hu:"HU-03, HU-04, HU-05",
      prompt:[
        "Crea la app fleet/contracts con el modelo Contrato:",
        "  numero_contrato (unique, generado automáticamente),",
        "  vehiculo (FK Vehiculo, on_delete=RESTRICT),",
        "  conductor (FK Conductor, on_delete=RESTRICT),",
        "  creado_por (FK User, null=True),",
        "  tipo_tarifa (choices: hora|dia|km), tarifa_valor (Decimal),",
        "  km_inicial, km_final (null=True), fecha_inicio, fecha_fin (null=True),",
        "  costo_subtotal (null=True), costo_penalizaciones (default 0),",
        "  costo_total (null=True), estado (choices: activa|cerrada|cancelada).",
        "",
        "Implementa el patrón Strategy para el cálculo de tarifa:",
        "  - Clase abstracta TarifaStrategy con método calcular(contrato) -> Decimal",
        "  - TarifaHora: costo = tarifa_valor * horas_transcurridas",
        "  - TarifaDia: costo = tarifa_valor * dias_completos",
        "  - TarifaKm: costo = tarifa_valor * (km_final - km_inicial)",
        "  - Contrato.calcular_costo() delega en la estrategia según tipo_tarifa.",
        "",
        "En el serializer ContratoSerializer implementa validate() que:",
        "  1. Valida RN-01: el vehículo no tiene otra renta activa.",
        "  2. Valida RN-04: el vehículo no tiene mantenimiento programado.",
        "  3. Valida RN-07: el vehículo no está fuera_de_servicio.",
        "  4. Valida RN-02: el conductor no supera limite_horas_dia.",
        "",
        "Crea la acción personalizada finalizar() en el ViewSet que:",
        "  - Recibe km_final, calcula el costo con Strategy, cierra el contrato.",
        "  - Genera Factura automáticamente (via Django signal post_save).",
        "  - Actualiza horas_hoy del conductor.",
        "  - Cambia el estado del vehículo a 'disponible'.",
        "",
        "Genera migración y tests para cada validación de RN.",
      ],
      req:["RF-07","RF-08","RF-09","RF-10","RF-12","RN-01","RN-02","RN-04","RN-05","RN-07"],
      accept:["POST /api/contratos/ con vehículo en renta retorna HTTP 400 (RN-01)","POST con vehículo en mantenimiento retorna HTTP 400 (RN-04)","POST /api/contratos/{id}/finalizar/ calcula costo correcto según tipo_tarifa","Al finalizar, el vehículo cambia a estado='disponible'","Se genera automáticamente una Factura al cerrar"],
    },
    {
      id:"MISIÓN 3", cu:"CU-07", title:"Reporte de Rentabilidad con Patrón Facade",
      sprint:"Sprint 2", hu:"HU-06",
      prompt:[
        "Crea la app fleet/reports con el modelo Reporte:",
        "  tipo (choices: ingresos|mantenimiento|rentabilidad|horas_conductor),",
        "  parametros (JSONField), resultado (JSONField, null=True),",
        "  generado_por (FK User), fecha_generacion (auto_now_add),",
        "  exportado (BooleanField default False), ruta_archivo (null=True).",
        "",
        "Implementa la clase ReporteService (patrón Facade) en services.py con:",
        "  - generar_reporte_ingresos(vehiculo_id=None, desde=None, hasta=None):",
        "      Agrega Contrato.objects.filter(estado='cerrada') con Sum(costo_total),",
        "      Count(), Avg(). Retorna dict con ingresos_totales, num_rentas, promedio.",
        "  - generar_reporte_rentabilidad(vehiculo_id):",
        "      Combina ingresos de contratos y costos de mantenimientos.",
        "      Calcula rentabilidad_neta = ingresos - costos_mantenimiento.",
        "  - exportar_pdf(reporte_id): usa ReportLab para generar PDF.",
        "  - exportar_excel(reporte_id): usa openpyxl para generar .xlsx.",
        "",
        "Crea el endpoint GET /api/reportes/ingresos/ con filtros:",
        "  vehiculo_id (opcional), desde (date, opcional), hasta (date, opcional).",
        "Crea el endpoint GET /api/reportes/{id}/exportar/?formato=pdf|excel",
        "  que retorna el archivo como FileResponse.",
        "",
        "Agrega permisos: solo usuarios con rol admin_contable pueden acceder.",
        "Genera tests con datos de fixtures para verificar los cálculos.",
      ],
      req:["RF-19","RF-20","RF-21","RU-05","RU-14","RU-15","RU-16"],
      accept:["GET /api/reportes/ingresos/ retorna suma correcta de contratos cerrados","Filtro por vehiculo_id filtra correctamente","GET con formato=pdf retorna Content-Type application/pdf","Solo admin_contable puede acceder (otros reciben HTTP 403)"],
    },
    {
      id:"MISIÓN 4", cu:"CU-06", title:"Módulo de Mantenimiento con Template Method",
      sprint:"Sprint 4", hu:"HU-11, HU-12",
      prompt:[
        "Crea la app fleet/maintenance con el modelo Mantenimiento:",
        "  vehiculo (FK Vehiculo, on_delete=RESTRICT),",
        "  tecnico (FK User, null=True),",
        "  tipo (choices: preventivo|correctivo),",
        "  descripcion (TextField, blank=True), fecha (DateField),",
        "  km_al_momento (Decimal), costo (Decimal default 0),",
        "  proximo_km (Decimal, null=True), proximo_fecha (DateField, null=True),",
        "  estado (choices: programado|realizado|cancelado).",
        "",
        "Implementa el patrón Template Method en services.py:",
        "  - Clase abstracta MantenimientoService con método plantilla ejecutar(vehiculo, datos):",
        "      1. validar_vehiculo(vehiculo)  [común]",
        "      2. registrar_intervencion(datos)  [común]",
        "      3. actualizar_historial(vehiculo)  [común]",
        "      4. calcular_proximo()  [ABSTRACTO]",
        "  - MantenimientoPreventivo.calcular_proximo(): proximo_km = km_actual + 5000",
        "  - MantenimientoCorrectivo.calcular_proximo(): retorna None (sin programación).",
        "",
        "En el serializer valida RN-06: vehiculo_id es obligatorio (FK NOT NULL).",
        "Al guardar un mantenimiento con estado='realizado', cambia el estado del",
        "  vehículo de 'mantenimiento' a 'disponible' via signal post_save.",
        "Al programar un mantenimiento, cambia el estado del vehículo a 'mantenimiento'.",
        "",
        "Endpoints: CRUD completo en /api/mantenimientos/",
        "Acción especial: POST /api/mantenimientos/{id}/realizar/ para cerrar el mantenimiento.",
      ],
      req:["RF-15","RF-16","RF-17","RF-18","RN-03","RN-04","RN-06"],
      accept:["POST /api/mantenimientos/ cambia estado del vehículo a 'mantenimiento'","POST /finalizar/ calcula proximo_km para mantenimiento preventivo","Mantenimiento correctivo no genera proximo_km","Intentar rentar vehículo con mantenimiento programado retorna HTTP 400"],
    },
    {
      id:"MISIÓN 5", cu:"CU-08", title:"Sistema de Alertas con Patrón Observer",
      sprint:"Sprint 3", hu:"HU-10",
      prompt:[
        "Crea la app fleet/alerts con el modelo Alerta:",
        "  tipo (choices: exceso_horas|mantenimiento_proximo|zona_prohibida|bajo_rendimiento|falla_sensor),",
        "  vehiculo (FK Vehiculo, null=True), conductor (FK Conductor, null=True),",
        "  contrato (FK Contrato, null=True), mensaje (TextField),",
        "  prioridad (choices: alta|media|baja default='media'),",
        "  resuelta (BooleanField default False),",
        "  fecha_generacion (auto_now_add), fecha_resolucion (null=True),",
        "  resuelta_por (FK User, null=True).",
        "",
        "Implementa observers via Django signals en signals.py:",
        "",
        "1. AlertaExcesoHoras (conectada a post_save de Contrato):",
        "   Cuando un contrato pasa a estado='cerrada', verifica si conductor.horas_hoy",
        "   supera conductor.limite_horas_dia. Si es así, crea Alerta tipo='exceso_horas',",
        "   prioridad='alta'.",
        "",
        "2. AlertaMantenimientoProximo (tarea Celery Beat, diaria):",
        "   Verifica todos los vehículos donde km_acumulado >= mantenimiento.proximo_km - 500.",
        "   Crea Alerta tipo='mantenimiento_proximo', prioridad='media' si no existe una",
        "   alerta activa del mismo tipo para ese vehículo.",
        "",
        "3. AlertaFallaSensor (conectada a señal de fleet/telemetry):",
        "   Si no se reciben datos GPS de un vehículo en renta por más de 10 minutos,",
        "   crea Alerta tipo='falla_sensor', prioridad='alta'.",
        "",
        "Endpoints:",
        "  GET  /api/alertas/          → listar alertas (filtro: resuelta=false)",
        "  PATCH /api/alertas/{id}/resolver/ → marcar como resuelta",
        "Registra las señales en apps.py de cada app afectada.",
      ],
      req:["RF-13","RF-14","RF-18","RNF-04","RN-02"],
      accept:["Al cerrar contrato con horas excedidas, se crea Alerta tipo='exceso_horas'","GET /api/alertas/?resuelta=false retorna solo alertas pendientes","PATCH /resolver/ actualiza resuelta=True y fecha_resolucion","La tarea Celery Beat no duplica alertas existentes"],
    },
    {
      id:"MISIÓN 6", cu:"CU-05", title:"Telemetría GPS y Monitoreo en Tiempo Real",
      sprint:"Sprint 3", hu:"HU-07, HU-08",
      prompt:[
        "Crea la app fleet/telemetry con el modelo Telemetria (usando BigAutoField):",
        "  vehiculo (FK Vehiculo), contrato (FK Contrato, null=True),",
        "  latitud (DecimalField max_digits=10 decimal_places=7),",
        "  longitud (DecimalField max_digits=10 decimal_places=7),",
        "  velocidad_kmh (Decimal), km_acumulado (Decimal),",
        "  timestamp (DateTimeField auto_now_add),",
        "  raw_data (JSONField default=dict).",
        "",
        "Crea el endpoint POST /api/telemetria/ para recibir datos del GPS externo.",
        "  Al recibir datos, actualiza vehiculo.km_acumulado con el valor recibido.",
        "  Protege este endpoint con autenticación por API Key (header X-GPS-Token).",
        "",
        "Crea el endpoint GET /api/vehiculos/{id}/ubicacion/ que retorna el",
        "  último registro de Telemetria del vehículo (latitud, longitud, timestamp,",
        "  velocidad, km_acumulado). Debe responder en menos de 5 segundos (RNF-06).",
        "",
        "Crea la vista de monitoreo GET /api/contratos/activos/mapa/",
        "  que retorna todos los contratos activos con la última ubicación de cada vehículo.",
        "  Usa select_related y prefetch_related para optimizar las consultas.",
        "",
        "Agrega índice en (vehiculo_id, timestamp DESC) para las consultas de ubicación.",
      ],
      req:["RF-11","RF-12","RF-14","RNF-05","RNF-06"],
      accept:["POST /api/telemetria/ actualiza km_acumulado del vehículo","GET /ubicacion/ retorna el registro más reciente","GET /mapa/ retorna todos los contratos activos con ubicación","Petición sin X-GPS-Token retorna HTTP 401"],
    },
  ];

  const result = [
    h1("3. Misiones en Antigravity — Un Agente por Caso de Uso"),
    gap(),
    body("Cada caso de uso del Entregable 1 se convierte en una Misión independiente en Antigravity. El flujo para cada misión es siempre el mismo: escribir el prompt → revisar el Plan de Implementación generado por el agente → aprobar → revisar el código → ejecutar tests."),
    gap(120),
    note("FLUJO ESTÁNDAR DE CADA MISIÓN: (1) Escribir prompt en Agent Manager → (2) El agente genera Plan de Implementación [REVISAR] → (3) Aprobar o comentar correcciones → (4) El agente escribe el código [REVISAR] → (5) El agente ejecuta las migraciones y tests [REVISAR] → (6) El agente abre el navegador y verifica el endpoint [REVISAR].", C.accent2, C.blue),
    gap(200),
  ];

  for (const m of missions) {
    result.push(h2(`${m.id} — ${m.title}`));
    result.push(gap(80));
    new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[1600,2200,1800,3760],
      rows:[
        new TableRow({ tableHeader:true, children:[hCell("Caso de uso",1600),hCell("Sprint",2200),hCell("Historias",1800),hCell("Requisitos",3760)] }),
        new TableRow({ children:[
          dCell(m.cu,1600,C.accent2,true,C.blue),
          dCell(m.sprint,2200,C.accent2),
          dCell(m.hu,1800,C.accent2),
          dCell(m.req.join(", "),3760,C.accent2),
        ]})
      ]
    });
    // Render table inline
    result.push(new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[1600,2200,1800,3760],
      rows:[
        new TableRow({ tableHeader:true, children:[hCell("Caso de uso",1600),hCell("Sprint",2200),hCell("Historias",1800),hCell("Requisitos",3760)] }),
        new TableRow({ children:[
          dCell(m.cu,1600,C.accent2,true,C.blue),
          dCell(m.sprint,2200,C.accent2),
          dCell(m.hu,1800,C.accent2),
          dCell(m.req.join(", "),3760,C.accent2),
        ]})
      ]
    }));

    result.push(gap(140));
    result.push(h3("Prompt para Antigravity (copiar tal cual en Agent Manager):"));
    result.push(codeBlock(m.prompt));
    result.push(gap(140));
    result.push(h3("Criterios de aceptación (verificar antes de aprobar el Plan):"));
    m.accept.forEach(a => result.push(bul(a)));
    result.push(gap(200));
    result.push(note("Después de aprobar el Plan: ve al Editor View para revisar el código generado. Si algo no cumple las convenciones del AGENTS.md, escribe un comentario directamente sobre el artefacto del plan y el agente lo corregirá.", C.lightGreen, C.green));
    result.push(gap(300));
  }

  result.push(pb());
  return result;
}

// ─── SECCIÓN 4 — CONFIGURACIÓN DE SETTINGS, JWT, CORS ────────────────────────
function seccionConfig() {
  return [
    h1("4. Configuración del Proyecto Django (settings, JWT, CORS, Celery)"),
    gap(),
    h2("4.1 Prompt de Configuración Inicial"),
    body("Una vez creadas las apps, ejecuta esta misión de configuración para unificar settings, seguridad y workers asíncronos:"),
    gap(100),
    codeBlock([
      "Configura el proyecto Django ope_config con los siguientes ajustes:",
      "",
      "1. settings/base.py (separar settings por entorno):",
      "   - INSTALLED_APPS: django, rest_framework, rest_framework_simplejwt,",
      "     corsheaders, django_celery_beat, fleet.vehicles, fleet.drivers,",
      "     fleet.contracts, fleet.maintenance, fleet.reports, fleet.alerts, fleet.telemetry.",
      "   - DATABASES: PostgreSQL (leer credenciales desde variables de entorno con python-decouple).",
      "   - REST_FRAMEWORK: DEFAULT_AUTHENTICATION_CLASSES con JWTAuthentication,",
      "     DEFAULT_PERMISSION_CLASSES con IsAuthenticated,",
      "     DEFAULT_PAGINATION_CLASS con PageNumberPagination, PAGE_SIZE=20.",
      "   - SIMPLE_JWT: ACCESS_TOKEN_LIFETIME=timedelta(hours=8),",
      "     REFRESH_TOKEN_LIFETIME=timedelta(days=30).",
      "   - CELERY_BROKER_URL: leer desde variable de entorno REDIS_URL.",
      "   - CORS_ALLOWED_ORIGINS: leer desde variable de entorno CORS_ORIGINS.",
      "   - LANGUAGE_CODE='es-co', TIME_ZONE='America/Bogota', USE_TZ=True.",
      "",
      "2. settings/development.py: DEBUG=True, ALLOWED_HOSTS=['*'].",
      "3. settings/production.py: DEBUG=False, seguridad HTTPS.",
      "",
      "4. Archivo .env.example con todas las variables:",
      "   SECRET_KEY, DATABASE_URL, REDIS_URL, CORS_ORIGINS, GPS_API_KEY.",
      "",
      "5. urls.py principal:",
      "   /api/token/          → TokenObtainPairView",
      "   /api/token/refresh/  → TokenRefreshView",
      "   /api/vehiculos/      → VehiculoViewSet",
      "   /api/conductores/    → ConductorViewSet",
      "   /api/contratos/      → ContratoViewSet",
      "   /api/mantenimientos/ → MantenimientoViewSet",
      "   /api/reportes/       → ReporteViewSet",
      "   /api/alertas/        → AlertaViewSet",
      "   /api/telemetria/     → TelemetriaViewSet",
      "   /api/schema/         → drf-spectacular para documentación OpenAPI",
    ]),
    gap(200),

    h2("4.2 Permisos y Roles"),
    body("Crea una misión adicional para implementar el sistema de roles descrito en los Entregables:"),
    codeBlock([
      "Crea un sistema de permisos por rol en fleet/permissions.py:",
      "",
      "- EsAdminFlota: el usuario tiene rol 'admin_flota' en PerfilUsuario.",
      "- EsAdminContable: el usuario tiene rol 'admin_contable'.",
      "- EsTecnico: el usuario tiene rol 'tecnico'.",
      "- EsConductorPropietario: el usuario es el conductor del contrato solicitado.",
      "",
      "Aplica en los ViewSets:",
      "- VehiculoViewSet: EsAdminFlota para create/update/destroy.",
      "- ContratoViewSet: EsAdminFlota para create; EsConductorPropietario para retrieve propio.",
      "- ReporteViewSet: EsAdminContable.",
      "- MantenimientoViewSet: EsTecnico para create/update.",
      "- AlertaViewSet: EsAdminFlota para resolver.",
    ]),
    pb(),
  ];
}

// ─── SECCIÓN 5 — COMANDOS Y FLUJO DE TRABAJO ─────────────────────────────────
function seccionFlujo() {
  return [
    h1("5. Flujo de Trabajo Completo en Antigravity"),
    gap(),
    h2("5.1 Ciclo de Trabajo por Misión"),
    body("Cada vez que inicies una nueva misión en Antigravity, sigue exactamente este ciclo:"),
    gap(100),
    num("Abrir Agent Manager → clic en 'Start Conversation' → seleccionar workspace 'ope-backend'."),
    num("Seleccionar modelo: Gemini 3.1 Pro (Planning mode). Para correcciones menores usa Fast mode."),
    num("Pegar el prompt del caso de uso correspondiente (Sección 3 de este SOP)."),
    num("Revisar el Plan de Implementación (Implementation Plan Artifact): verificar que las clases, métodos y validaciones correspondan a los requisitos del Entregable 1."),
    num("Si algo no está bien: dejar un comentario directamente sobre el artefacto (como en Google Docs) indicando la corrección. El agente incorporará el feedback sin interrumpir su flujo."),
    num("Aprobar el plan. El agente comenzará a escribir el código."),
    num("Al finalizar el código, el agente pedirá aprobación para ejecutar: python manage.py makemigrations && python manage.py migrate. Aprobar."),
    num("El agente ejecutará pytest. Revisar el reporte de tests. Si hay fallos, el agente los corregirá automáticamente."),
    num("El agente abrirá el navegador integrado de Antigravity, levantará el servidor con python manage.py runserver y verificará los endpoints con llamadas HTTP. Revisar los screenshots generados."),
    num("Cuando todos los criterios de aceptación estén verdes, la misión está completa. Proceder a la siguiente."),
    gap(200),

    h2("5.2 Comandos Manuales (cuando necesites intervenir directamente)"),
    codeBlock([
      "# Activar entorno virtual",
      "source venv/bin/activate",
      "",
      "# Aplicar migraciones",
      "python manage.py migrate",
      "",
      "# Crear superusuario para pruebas",
      "python manage.py createsuperuser",
      "",
      "# Cargar datos semilla",
      "python manage.py loaddata fleet/fixtures/initial_data.json",
      "",
      "# Ejecutar servidor de desarrollo",
      "python manage.py runserver 0.0.0.0:8000",
      "",
      "# Ejecutar todos los tests",
      "pytest --ds=ope_config.settings.development -v",
      "",
      "# Ejecutar tests de una app específica",
      "pytest fleet/contracts/tests.py -v",
      "",
      "# Iniciar worker de Celery (en otra terminal)",
      "celery -A ope_config worker --loglevel=info",
      "",
      "# Iniciar Celery Beat (scheduler de tareas periódicas)",
      "celery -A ope_config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler",
      "",
      "# Ver logs de migraciones",
      "python manage.py showmigrations",
      "",
      "# Importar el esquema SQL directamente a PostgreSQL",
      "psql -U postgres -d ope_db -f ope_database.sql",
    ]),
    gap(200),

    h2("5.3 Orden de Ejecución de las Misiones"),
    body("El orden importa porque hay dependencias entre apps. Ejecutar las misiones en este orden:"),
    gap(100),
    new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[700,1600,1800,1800,3460],
      rows:[
        new TableRow({ tableHeader:true, children:[hCell("#",700),hCell("Misión",1600),hCell("Sprint",1800),hCell("Dependencia",1800),hCell("App Django generada",3460)] }),
        ...([
          ["1","Config. Base","Previo","Ninguna","ope_config/settings, .env, urls.py, permisos"],
          ["2","MISIÓN 1 — Vehículos y Conductores","Sprint 1","Settings base","fleet/vehicles, fleet/drivers"],
          ["3","MISIÓN 2 — Contratos + Strategy","Sprint 1–2","Vehículos, Conductores","fleet/contracts, fleet/billing (Factura, Penalizacion)"],
          ["4","MISIÓN 3 — Reportes + Facade","Sprint 2","Contratos","fleet/reports"],
          ["5","MISIÓN 5 — Alertas + Observer","Sprint 3","Contratos, Conductores","fleet/alerts"],
          ["6","MISIÓN 6 — Telemetría GPS","Sprint 3","Vehículos, Contratos","fleet/telemetry"],
          ["7","MISIÓN 4 — Mantenimiento + Template","Sprint 4","Vehículos, Alertas","fleet/maintenance"],
          ["8","Tests de integración","Cierre","Todas las apps","conftest.py, test_integration.py"],
        ].map((r,i)=>new TableRow({ children: r.map((v,j)=>dCell(v,[700,1600,1800,1800,3460][j],i%2===0?C.accent2:C.white,j===0)) })))
      ]
    }),
    pb(),
  ];
}

// ─── SECCIÓN 6 — VERIFICACIÓN FINAL ──────────────────────────────────────────
function seccionVerificacion() {
  return [
    h1("6. Checklist de Verificación Final"),
    gap(),
    body("Antes de considerar el backend completo, verifica que cada ítem de esta lista esté confirmado:"),
    gap(120),
    h2("6.1 Funcionalidad (Casos de Uso)"),
    ...[
      ["CU-01", "POST /api/vehiculos/ crea vehículo con estado='disponible'"],
      ["CU-02", "POST /api/conductores/ valida cédula y licencia únicas"],
      ["CU-03", "POST /api/contratos/ aplica RN-01, RN-02, RN-04, RN-07"],
      ["CU-04", "POST /api/contratos/{id}/finalizar/ calcula costo por Strategy y genera Factura"],
      ["CU-05", "GET /api/vehiculos/{id}/ubicacion/ retorna última telemetría"],
      ["CU-06", "POST /api/mantenimientos/ cambia estado del vehículo, aplica Template Method"],
      ["CU-07", "GET /api/reportes/ingresos/ retorna datos correctos, exportable en PDF/Excel"],
      ["CU-08", "Señal Django crea Alerta al detectar exceso de horas"],
    ].map(([id, desc]) => new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[700,8660],
      rows:[new TableRow({ children:[
        dCell("[ ]",700,C.accent2,true,C.blue,true),
        dCell(`${id}: ${desc}`,8660,C.white),
      ]})]
    })),
    gap(200),

    h2("6.2 Seguridad y No Funcionales"),
    ...[
      ["RNF-01","JWT funciona: token inválido retorna HTTP 401"],
      ["RNF-02","Roles: admin_contable no puede crear contratos (HTTP 403)"],
      ["RNF-03","Contraseñas hasheadas en BD (Django auth nativo)"],
      ["RNF-04","Tabla fleet_auditoria registra cambios de estado"],
      ["RNF-05","GET /api/vehiculos/ responde en menos de 3 segundos"],
      ["RNF-10","Servidor levanta con gunicorn sin errores"],
    ].map(([id, desc]) => new Table({
      width:{size:9360,type:WidthType.DXA}, columnWidths:[700,8660],
      rows:[new TableRow({ children:[
        dCell("[ ]",700,C.lightGreen,true,C.green,true),
        dCell(`${id}: ${desc}`,8660,C.white),
      ]})]
    })),
    gap(200),

    h2("6.3 Último Prompt de Antigravity — Revisión General"),
    body("Cuando hayas completado todas las misiones, ejecuta este prompt final en Antigravity para que el agente haga una revisión integral:"),
    gap(100),
    codeBlock([
      "Revisa el proyecto completo fleet/ y verifica lo siguiente:",
      "1. Que todos los modelos tienen sus migraciones aplicadas correctamente.",
      "2. Que no hay lógica de negocio en los ViewSets (todo debe estar en services.py o serializers.py).",
      "3. Que los patrones Strategy, Observer, Repository, Facade y Template Method están implementados.",
      "4. Que todos los endpoints del /api/schema/ están documentados con OpenAPI.",
      "5. Ejecuta pytest --cov=fleet --cov-report=term-missing y reporta la cobertura.",
      "6. Abre el navegador y verifica que /api/schema/swagger-ui/ carga correctamente.",
      "7. Genera un archivo BACKEND_STATUS.md en la raíz con el estado de cada endpoint.",
    ]),
    gap(200),
    note("¡Importante! Guarda una copia del archivo AGENTS.md actualizado y del BACKEND_STATUS.md generado. Estos documentos evidencian el trabajo realizado con Antigravity para el Entregable 2.", C.lightRed, C.red),
    pb(),
  ];
}

// ─── ENSAMBLADO ───────────────────────────────────────────────────────────────
async function build() {
  const doc = new Document({
    numbering: {
      config: [
        { reference:"bullets", levels:[
          { level:0, format:LevelFormat.BULLET, text:"•", alignment:AlignmentType.LEFT,
            style:{ paragraph:{ indent:{ left:720, hanging:360 } } } },
          { level:1, format:LevelFormat.BULLET, text:"◦", alignment:AlignmentType.LEFT,
            style:{ paragraph:{ indent:{ left:1080, hanging:360 } } } },
        ]},
        { reference:"numbers", levels:[
          { level:0, format:LevelFormat.DECIMAL, text:"%1.", alignment:AlignmentType.LEFT,
            style:{ paragraph:{ indent:{ left:720, hanging:360 } } } },
        ]},
      ]
    },
    styles: {
      default: { document: { run:{ font:"Arial", size:22 } } },
      paragraphStyles:[
        { id:"Heading1", name:"Heading 1", basedOn:"Normal", next:"Normal", quickFormat:true,
          run:{ size:34, bold:true, font:"Arial", color:C.navy },
          paragraph:{ spacing:{ before:400, after:200 }, outlineLevel:0 } },
        { id:"Heading2", name:"Heading 2", basedOn:"Normal", next:"Normal", quickFormat:true,
          run:{ size:27, bold:true, font:"Arial", color:C.blue },
          paragraph:{ spacing:{ before:280, after:140 }, outlineLevel:1 } },
        { id:"Heading3", name:"Heading 3", basedOn:"Normal", next:"Normal", quickFormat:true,
          run:{ size:23, bold:true, font:"Arial", color:C.orange },
          paragraph:{ spacing:{ before:200, after:100 }, outlineLevel:2 } },
      ]
    },
    sections:[{
      properties:{
        page:{
          size:{ width:12240, height:15840 },
          margin:{ top:1200, right:1200, bottom:1200, left:1440 }
        }
      },
      headers:{
        default: new Header({ children:[
          new Paragraph({
            children:[new TextRun({ text:"SOP-OPE-BE-001  |  Backend OpE con Google Antigravity  |  ITM 2026", size:18, font:"Arial", color:C.gray })],
            border:{ bottom:{ style:BorderStyle.SINGLE, size:4, color:C.lightBlue, space:1 } },
            spacing:{ after:100 },
          })
        ]})
      },
      footers:{
        default: new Footer({ children:[
          new Paragraph({
            children:[
              new TextRun({ text:"Samuel Causil L. · Juan Pablo León D.  |  Pág. ", size:18, font:"Arial", color:C.gray }),
              new TextRun({ children:[PageNumber.CURRENT], size:18, font:"Arial", color:C.gray }),
            ],
            border:{ top:{ style:BorderStyle.SINGLE, size:4, color:C.lightBlue, space:1 } },
            spacing:{ before:100 },
          })
        ]})
      },
      children:[
        ...cover(),
        ...seccionObjetivo(),
        ...seccionInstalacion(),
        ...seccionSetup(),
        ...seccionMisiones(),
        ...seccionConfig(),
        ...seccionFlujo(),
        ...seccionVerificacion(),
      ]
    }]
  });

  const buf = await Packer.toBuffer(doc);
  fs.writeFileSync('/home/claude/SOP_OpE_Antigravity.docx', buf);
  console.log('SOP created!');
}

build().catch(console.error);
