from database.mongo_service import MongoService
from database.redis_service import RedisService
from database.neo4j_service import Neo4jService

PRODUTOS_INICIAIS = [
    {
        "sku": "MON-LG-24GN60R",
        "nome": "Monitor LG UltraGear 24\" IPS 144Hz",
        "marca": "LG",
        "categoria": "Monitores",
        "preco": 949.90,
        "estoque": 85,
        "imagem": "src/assets/images/monitor_ultragear_24_1794261944536.jpg",
        "especificacoes": {
            "Tamanho da Tela": "23.8 polegadas Full HD (1920x1080)",
            "Painel": "IPS com 99% sRGB",
            "Taxa de Atualização": "144 Hz",
            "Tempo de Resposta": "1 ms (GtG)",
            "Conexões": "1x HDMI 2.0, 1x DisplayPort 1.4, Saída de Áudio"
        }
    },
    {
        "sku": "MON-DEL-U2723QE",
        "nome": "Monitor Dell UltraSharp 27\" 4K USB-C Hub",
        "marca": "Dell",
        "categoria": "Monitores",
        "preco": 3499.00,
        "estoque": 60,
        "imagem": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Tamanho da Tela": "27 polegadas 4K UHD (3840x2160)",
            "Painel": "IPS Black com 98% DCI-P3",
            "Hub Integrado": "USB-C com Power Delivery de 90W e RJ45 Ethernet",
            "Contraste": "2000:1 nativo",
            "Ajustes": "Altura, inclinação, rotação e pivô"
        }
    },
    {
        "sku": "MOU-LOG-GPROX",
        "nome": "Mouse Logitech G Pro X Superlight",
        "marca": "Logitech G",
        "categoria": "Periféricos",
        "preco": 689.90,
        "estoque": 110,
        "imagem": "src/assets/images/mouse_logitech_gpro_1794261946526.jpg",
        "especificacoes": {
            "Sensor": "HERO 25K (até 25.600 DPI)",
            "Peso": "63 gramas",
            "Conectividade": "Sem fio LIGHTSPEED 2.4 GHz",
            "Autonomia": "Até 70 horas de uso contínuo",
            "Pés": "PTFE puro sem aditivos"
        }
    },
    {
        "sku": "TEC-KEY-K2V2",
        "nome": "Teclado Mecânico Keychron K2 V2",
        "marca": "Keychron",
        "categoria": "Periféricos",
        "preco": 629.00,
        "estoque": 75,
        "imagem": "src/assets/images/keyboard_keychron_k2_1794261947446.jpg",
        "especificacoes": {
            "Layout": "Compacto 75% (84 teclas)",
            "Switches": "Gateron G Pro Brown (Tátil)",
            "Conexão": "Bluetooth 5.1 (até 3 dispositivos) e USB-C",
            "Bateria": "4000 mAh recarregável",
            "Compatibilidade": "Windows, macOS e Linux (Keycaps inclusas)"
        }
    },
    {
        "sku": "PAD-ART-ZEROXL",
        "nome": "Mousepad Artisan FX Zero Soft XL",
        "marca": "Artisan",
        "categoria": "Periféricos",
        "preco": 459.90,
        "estoque": 90,
        "imagem": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Dimensões": "490 x 420 x 4 mm (Tamanho XL)",
            "Superfície": "Tecido de malha circular japonesa de controle preciso",
            "Base": "Espuma Poron antiderrapante de densidade Soft",
            "Bordas": "Costura rebaixada abaixo da superfície",
            "Origem": "Fabricado no Japão"
        }
    },
    {
        "sku": "SSD-KNG-NV21TB",
        "nome": "SSD Kingston NV2 1TB NVMe M.2",
        "marca": "Kingston",
        "categoria": "Armazenamento",
        "preco": 419.90,
        "estoque": 140,
        "imagem": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Capacidade": "1 TB",
            "Interface": "PCIe 4.0 x4 NVMe M.2 2280",
            "Leitura Sequencial": "Até 3.500 MB/s",
            "Gravação Sequencial": "Até 2.100 MB/s",
            "Expectativa de Vida Útil": "1.500.000 horas MTBF"
        }
    },
    {
        "sku": "SSD-SAM-T72TB",
        "nome": "SSD Externo Portátil Samsung T7 Shield 2TB",
        "marca": "Samsung",
        "categoria": "Armazenamento",
        "preco": 1189.00,
        "estoque": 80,
        "imagem": "src/assets/images/ssd_samsung_t7_portable_1794263339708.jpg",
        "especificacoes": {
            "Capacidade": "2 TB",
            "Interface": "USB 3.2 Gen 2 (10 Gbps) USB-C",
            "Velocidade": "Até 1.050 MB/s de leitura e 1.000 MB/s de gravação",
            "Proteção": "Certificação IP65 resistente a água, poeira e quedas de 3m",
            "Criptografia": "Hardware AES de 256 bits"
        }
    },
    {
        "sku": "HDS-HPX-CLOUD3",
        "nome": "Headset HyperX Cloud III",
        "marca": "HyperX",
        "categoria": "Áudio & Streaming",
        "preco": 549.90,
        "estoque": 95,
        "imagem": "src/assets/images/headset_hyperx_cloud_1794261947208.jpg",
        "especificacoes": {
            "Drivers": "Dinâmicos angulados de 53 mm com neodímio",
            "Microfone": "10 mm removível com cancelamento de ruído e LED mudo",
            "Estrutura": "Arco em aço e garfos em alumínio",
            "Espuma": "Memory Foam revestida em couro sintético macio",
            "Conexões": "P3 3.5mm, Adaptador USB-C e USB-A"
        }
    },
    {
        "sku": "MIC-SHU-MV7X",
        "nome": "Microfone Dinâmico Shure MV7 USB/XLR",
        "marca": "Shure",
        "categoria": "Áudio & Streaming",
        "preco": 1899.00,
        "estoque": 65,
        "imagem": "src/assets/images/mic_shure_mv7_1794263338555.jpg",
        "especificacoes": {
            "Cápsula": "Dinâmica com padrão polar cardioide unidirecional",
            "Saídas": "Dupla conectividade USB Micro-B e XLR profissional",
            "Resposta de Frequência": "50 Hz a 16.000 Hz",
            "Monitoramento": "Saída P2 3.5mm integrada com latência zero",
            "Construção": "Corpo inteiramente metálico com suporte em U"
        }
    },
    {
        "sku": "WEB-LOG-C920S",
        "nome": "Webcam Logitech C920s Pro Full HD",
        "marca": "Logitech",
        "categoria": "Áudio & Streaming",
        "preco": 389.90,
        "estoque": 100,
        "imagem": "https://images.unsplash.com/photo-1587826080692-f439cd0b70da?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Resolução Máxima": "Full HD 1080p a 30 fps",
            "Lente": "Vidro Full HD com foco automático",
            "Campo de Visão": "78 graus diagonal",
            "Microfones": "Estéreo duplo integrado",
            "Privacidade": "Protetor físico de lente incluso"
        }
    },
    {
        "sku": "MEM-COR-VENG32",
        "nome": "Memória Corsair Vengeance 32GB (2x16GB) DDR5",
        "marca": "Corsair",
        "categoria": "Hardware",
        "preco": 879.00,
        "estoque": 90,
        "imagem": "https://images.unsplash.com/photo-1562976540-1502c2145186?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Capacidade Total": "32 GB (Kit 2x 16 GB)",
            "Frequência": "5600 MHz (PC5-44800)",
            "Latência": "CL36-36-36-76",
            "Tensão": "1.25V",
            "Dissipador": "Alumínio anodizado de perfil baixo"
        }
    },
    {
        "sku": "GPU-ASU-RTX4070S",
        "nome": "Placa de Vídeo ASUS Dual GeForce RTX 4070 Super 12GB",
        "marca": "ASUS",
        "categoria": "Hardware",
        "preco": 4199.00,
        "estoque": 55,
        "imagem": "src/assets/images/gpu_rtx_4070_1794263337086.jpg",
        "especificacoes": {
            "Memória de Vídeo": "12 GB GDDR6X (192 bits)",
            "Arquitetura": "NVIDIA Ada Lovelace com DLSS 3 e Ray Tracing",
            "Clock Boost": "2550 MHz (Modo OC)",
            "Refrigeração": "2x Ventoinhas Axial-tech com modo 0dB",
            "Saídas de Vídeo": "1x HDMI 2.1a, 3x DisplayPort 1.4a"
        }
    },
    {
        "sku": "FON-XPG-CORE750",
        "nome": "Fonte XPG Core Reactor 750W 80 Plus Gold",
        "marca": "XPG",
        "categoria": "Hardware",
        "preco": 649.90,
        "estoque": 80,
        "imagem": "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Potência": "750W Reais",
            "Certificação": "80 Plus Gold e Cybenetics Platinum",
            "Cabeamento": "100% Modular",
            "Capacitores": "100% Japoneses (105 °C)",
            "Ventoinha": "120 mm FDB silenciosa"
        }
    },
    {
        "sku": "ROT-TPL-AX5400",
        "nome": "Roteador TP-Link Archer AX73 Wi-Fi 6 AX5400",
        "marca": "TP-Link",
        "categoria": "Redes & Energia",
        "preco": 729.90,
        "estoque": 85,
        "imagem": "src/assets/images/router_tp_link_ax5400_1794263338428.jpg",
        "especificacoes": {
            "Padrão Wi-Fi": "Wi-Fi 6 Dual Band (4804 Mbps em 5GHz + 574 Mbps em 2.4GHz)",
            "Antenas": "6 antenas externas de alto desempenho com Beamforming",
            "Portas Ethernet": "1x WAN Gigabit + 4x LAN Gigabit (com Link Aggregation)",
            "Processador": "CPU Triple-Core de 1.5 GHz",
            "Segurança": "WPA3 e TP-Link HomeShield"
        }
    },
    {
        "sku": "NOB-APC-BZ1500",
        "nome": "Nobreak APC Back-UPS 1500VA Bivolt",
        "marca": "APC",
        "categoria": "Redes & Energia",
        "preco": 1249.00,
        "estoque": 70,
        "imagem": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Potência": "1500 VA / 825 W",
            "Tensão": "Entrada Bivolt automático / Saída 115V",
            "Tomadas": "8 tomadas NBR 14136 protegidas contra surtos",
            "Bateria": "2x Baterias seladas 12V 7Ah com engate rápido",
            "Gerenciamento": "Alarme sonoro e estabilizador integrado"
        }
    },
    {
        "sku": "CAD-ERG-AURA",
        "nome": "Cadeira Ergonômica Vértice Aura Mesh",
        "marca": "Vértice",
        "categoria": "Ergonomia & Setup",
        "preco": 1590.00,
        "estoque": 65,
        "imagem": "src/assets/images/chair_ergonomic_mesh_1794263339217.jpg",
        "especificacoes": {
            "Encosto": "Tela Mesh respirável com suporte lombar adaptativo",
            "Braços": "Ajustáveis 4D em poliuretano macio",
            "Mecanismo": "Sincronizado com 4 ângulos de travamento (até 135°)",
            "Pistão e Base": "Pistão a gás Classe 4 e base piramidal em alumínio",
            "Peso Suportado": "Até 136 kg recomendados"
        }
    },
    {
        "sku": "SUP-ELG-F80N",
        "nome": "Suporte Articulado de Mesa ELG F80N com Pistão a Gás",
        "marca": "ELG",
        "categoria": "Ergonomia & Setup",
        "preco": 219.90,
        "estoque": 120,
        "imagem": "https://images.unsplash.com/photo-1593640408182-31c70c8268f5?auto=format&fit=crop&w=800&q=80",
        "especificacoes": {
            "Compatibilidade": "Monitores de 17\" a 35\" (padrão VESA 75x75 e 100x100)",
            "Carga Suportada": "De 2 kg a 9 kg",
            "Articulação": "Pistão a gás com giro 360° e ajuste de altura de 26 cm",
            "Organização": "Calha interna para passagem oculta de cabos",
            "Fixação": "Morsa de borda ou furação passante na mesa"
        }
    }
]

CLIENTES_INICIAIS = [
    {"id": "cli_01", "nome": "Lucas Andrade", "email": "lucas.andrade@email.com", "senha": "123", "cidade": "São Paulo, SP"},
    {"id": "cli_02", "nome": "Mariana Costa", "email": "mariana.costa@email.com", "senha": "123", "cidade": "Curitiba, PR"},
    {"id": "cli_03", "nome": "Rafael Nogueira", "email": "rafael.nogueira@email.com", "senha": "123", "cidade": "Belo Horizonte, MG"},
    {"id": "cli_04", "nome": "Beatriz Almeida", "email": "beatriz.almeida@email.com", "senha": "123", "cidade": "Porto Alegre, RS"}
]

COMPRAS_INICIAIS = [
    {"cliente_id": "cli_01", "skus": ["MON-LG-24GN60R", "MOU-LOG-GPROX"]},
    {"cliente_id": "cli_02", "skus": ["MON-LG-24GN60R", "MOU-LOG-GPROX", "PAD-ART-ZEROXL", "HDS-HPX-CLOUD3", "MIC-SHU-MV7X", "WEB-LOG-C920S"]},
    {"cliente_id": "cli_03", "skus": ["MON-DEL-U2723QE", "TEC-KEY-K2V2", "CAD-ERG-AURA", "SUP-ELG-F80N", "SSD-SAM-T72TB"]},
    {"cliente_id": "cli_04", "skus": ["GPU-ASU-RTX4070S", "MEM-COR-VENG32", "FON-XPG-CORE750", "SSD-KNG-NV21TB", "NOB-APC-BZ1500", "ROT-TPL-AX5400"]}
]

AVALIACOES_INICIAIS = [
    {"cliente_id": "cli_01", "sku": "MON-LG-24GN60R", "nota": 5},
    {"cliente_id": "cli_01", "sku": "MOU-LOG-GPROX", "nota": 5},
    {"cliente_id": "cli_02", "sku": "MON-LG-24GN60R", "nota": 5},
    {"cliente_id": "cli_02", "sku": "MOU-LOG-GPROX", "nota": 4},
    {"cliente_id": "cli_02", "sku": "HDS-HPX-CLOUD3", "nota": 5},
    {"cliente_id": "cli_02", "sku": "MIC-SHU-MV7X", "nota": 5},
    {"cliente_id": "cli_03", "sku": "MON-DEL-U2723QE", "nota": 5},
    {"cliente_id": "cli_03", "sku": "TEC-KEY-K2V2", "nota": 4},
    {"cliente_id": "cli_03", "sku": "CAD-ERG-AURA", "nota": 5},
    {"cliente_id": "cli_04", "sku": "GPU-ASU-RTX4070S", "nota": 5},
    {"cliente_id": "cli_04", "sku": "MEM-COR-VENG32", "nota": 5},
    {"cliente_id": "cli_04", "sku": "SSD-KNG-NV21TB", "nota": 4}
]


def executar_seed():
    mongo = MongoService()
    redis_srv = RedisService()
    neo4j_srv = Neo4jService()

    try:
        print("Limpando dados anteriores...")
        mongo.limpar_dados()
        redis_srv.limpar_dados()
        neo4j_srv.limpar_dados()

        print("Criando índices e constraints...")
        mongo.criar_indices()
        neo4j_srv.criar_constraints()

        print("Cadastrando clientes, categorias e produtos...")
        mongo.clientes.insert_many([c.copy() for c in CLIENTES_INICIAIS])
        mongo.produtos.insert_many([p.copy() for p in PRODUTOS_INICIAIS])

        for cliente in CLIENTES_INICIAIS:
            neo4j_srv.sincronizar_cliente(cliente["id"], cliente["nome"])

        for produto in PRODUTOS_INICIAIS:
            neo4j_srv.sincronizar_produto(
                produto["sku"],
                produto["nome"],
                produto["categoria"]
            )

        print("Registrando histórico de compras e avaliações no grafo...")
        mapa_produtos = {p["sku"]: p for p in PRODUTOS_INICIAIS}
        for compra in COMPRAS_INICIAIS:
            itens_pedido = []
            for sku in compra["skus"]:
                prod = mapa_produtos[sku]
                itens_pedido.append({
                    "sku": prod["sku"],
                    "nome": prod["nome"],
                    "categoria": prod["categoria"],
                    "preco": prod["preco"],
                    "quantidade": 1
                })
            mongo.registrar_pedido(compra["cliente_id"], itens_pedido)
            neo4j_srv.registrar_compra(compra["cliente_id"], compra["skus"])

        for aval in AVALIACOES_INICIAIS:
            neo4j_srv.registrar_avaliacao(
                aval["cliente_id"],
                aval["sku"],
                aval["nota"]
            )

        # Adiciona um item inicial no carrinho do primeiro cliente para facilitar o teste imediato
        redis_srv.adicionar_ao_carrinho("cli_01", mapa_produtos["SSD-KNG-NV21TB"], 1)

        print("Carga inicial concluída com sucesso!")
    finally:
        neo4j_srv.fechar()


if __name__ == "__main__":
    executar_seed()
