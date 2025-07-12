Nombre del Caso de Uso

Atención al Cliente Multicanal con Agentes Especializados

Objetivo

Automatizar el soporte al cliente desde múltiples canales, identificando la intención, generando respuestas automáticas, consultando estados de pedidos y extrayendo insights útiles para el negocio.

Agentes


# Agente


🤖 Agente Clasificador
Detecta la intención del mensaje: compra, queja, devolución, etc.
Azure OpenAI (GPT-4) + prompt

📦 Agente de Pedidos
Consulta Supabase vía API REST para obtener el estado del pedido según el número.
Supabase REST API

💬 Agente de Respuestas
Redacta una respuesta clara y personalizada para el cliente.
Azure OpenAI

📊 Agente Analítico
Agrupa intenciones comunes para generar reportes para el área comercial.
Azure Function + Supabase SQL

# Tecnologías y Servicios

Servicio
Propósito
- Azure Communication Services
Conexión con canales como correo, WhatsApp o SMS
-  Azure OpenAI (GPT-4)
Motor de IA para clasificación, respuestas, análisis
-  Azure Logic Apps
Automatización de flujos de entrada de mensajes
-  Supabase
Base de datos para registrar tickets, pedidos, respuestas y métricas
-  Azure AI Search (opcional)
Búsqueda semántica en documentos FAQ internos


# Flujo General

1.	📨 Entrada multicanal
- El cliente escribe por WhatsApp o correo.
- Azure Logic Apps capta el mensaje y lo pasa al agente orquestador.
2.	🧠 Agente Clasificador (GPT-4)
- Prompt de clasificación de intención.
- Responde: “Intención detectada: Devolución de producto”.
3.	📦 Agente de Pedidos (si aplica)
- Busca el estado del pedido en Supabase usando order_id.
4.	💬 Agente de Respuestas
- Genera una respuesta empática y clara basada en la intención, el historial del cliente y el estado del pedido (si aplica).
5.	✉️ Respuesta al cliente
- Logic App o Communication Services envía el mensaje de vuelta por el canal original.
6.	📊 Agente Analítico (cada hora o día)
- Agrupa las preguntas más comunes y genera insights: “65% de clientes preguntan por demoras de envío”.


ebsoltech

tcd2025

(Tcd2025