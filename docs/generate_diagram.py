#!/usr/bin/env python3
"""
Script para generar el diagrama de arquitectura del Engine Manager
usando la biblioteca Diagrams (https://diagrams.mingrammer.com/)
"""

from diagrams import Diagram, Cluster, Edge
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.onprem.client import Client
from diagrams.generic.blank import Blank
from diagrams.generic.storage import Storage
from diagrams.onprem.compute import Server
from diagrams.custom import Custom

# Configuración del diagrama
graph_attr = {
    "fontsize": "16",
    "bgcolor": "white",
    "pad": "0.5",
    "nodesep": "0.8",
    "ranksep": "1.0",
}

node_attr = {
    "fontsize": "12",
    "height": "1.2",
    "width": "2.0",
}

edge_attr = {
    "fontsize": "10",
}

with Diagram(
    "Arquitectura Engine Manager - Chess Trainer",
    filename="docs/engine_manager_architecture",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
):
    
    # Cliente/Aplicación principal
    app = Client("Aplicación de Ajedrez\n(Frontend/Backend)")
    
    # Archivo de configuración
    config = Storage("config/engines.yaml\n(Configuración)")
    
    with Cluster("Engine Manager System"):
        # EngineManager (Fábrica)
        manager = Python("EngineManager\n(Factory)")
        
        with Cluster("Adaptadores (Adapter Pattern)"):
            # Interfaz abstracta
            interface = Python("EngineInterface\n<<abstract>>")
            
            with Cluster("Implementaciones"):
                # Adaptador UCI
                uci_adapter = Python("UciEngineAdapter\n(Protocolo UCI)")
                
                # Adaptador REST
                rest_adapter = Python("RestEngineAdapter\n(HTTP/REST)")
        
        # Relaciones dentro del Engine Manager
        manager >> Edge(label="carga") >> config
        manager >> Edge(label="crea/gestiona") >> interface
        interface >> Edge(label="implements", style="dashed") >> uci_adapter
        interface >> Edge(label="implements", style="dashed") >> rest_adapter
    
    # Motores externos
    with Cluster("Motores de Ajedrez"):
        # Motor UCI local (Stockfish)
        stockfish = Server("Stockfish\n(Motor UCI Local)")
        
        # API REST remota
        chess_api = FastAPI("Chess API\n(Servicio REST)")
    
    # Flujo de comunicación
    app >> Edge(label="1. solicita motor") >> manager
    manager >> Edge(label="2. devuelve adaptador") >> app
    app >> Edge(label="3. get_best_move(fen, depth)", color="blue") >> interface
    
    # Comunicación con motores
    uci_adapter >> Edge(label="UCI Protocol\n(stdin/stdout)", color="green") >> stockfish
    rest_adapter >> Edge(label="HTTP Request\n(GET/POST)", color="orange") >> chess_api
    
    # Respuestas
    stockfish >> Edge(label="bestmove e2e4", color="green", style="dotted") >> uci_adapter
    chess_api >> Edge(label="JSON Response", color="orange", style="dotted") >> rest_adapter

print("✅ Diagrama generado exitosamente: docs/engine_manager_architecture.png")

