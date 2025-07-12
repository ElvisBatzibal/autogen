from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from classify.classify_messages import run_classification_process
from orders.agent_orders import run_order_agent_process
from response.agent_responses import run_response_agent_process
from analytics.agent_analytics import generate_analytics_summary


# Herramientas para cada agente
tools = {
    "Clasificador": run_classification_process,
    "Pedidos": run_order_agent_process,
    "Respuestas": run_response_agent_process,
    "Analitico": generate_analytics_summary
}

# Definimos agentes con nombre y función
agent_clasificador = AssistantAgent(
    name="Clasificador",
    system_message="Tu tarea es clasificar mensajes según su intención.",
    code_execution_config={"use_docker": True}
)

agent_pedidos = AssistantAgent(
    name="Pedidos",
    system_message="Tu tarea es verificar el estado de pedidos según el código extraído.",
    code_execution_config={"use_docker": True}
)

agent_respuestas = AssistantAgent(
    name="Respuestas",
    system_message="Tu tarea es generar respuestas naturales y personalizadas para el cliente.",
    code_execution_config={"use_docker": True}
)

agent_analitico = AssistantAgent(
    name="Analitico",
    system_message="Tu tarea es generar resúmenes de intenciones para fines comerciales.",
    code_execution_config={"use_docker": True}
)

# Agente de usuario que inicia el proceso
user_proxy = UserProxyAgent(
    name="Usuario",
    system_message="Simula a un operador que desea orquestar todos los agentes.",
    human_input_mode="NEVER",
    code_execution_config={"use_docker": True}
)

# Grupo de agentes
groupchat = GroupChat(
    agents=[user_proxy, agent_clasificador, agent_pedidos, agent_respuestas, agent_analitico],
    messages=[],
    max_round=5
)

manager = GroupChatManager(groupchat=groupchat, name="Orquestador")

async def main():
    print("🚀 Iniciando orquestación de agentes...")
    
    await run_classification_process()
    await run_order_agent_process()
    await run_response_agent_process()
    await generate_analytics_summary()

    print("✅ Proceso completo.")

if __name__ == "__main__":
    asyncio.run(main())