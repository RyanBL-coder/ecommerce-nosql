import os
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

load_dotenv()


class MongoService:
    def __init__(self):
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        self.db = self.client["loja_informatica"]
        self.produtos = self.db["produtos"]
        self.clientes = self.db["clientes"]
        self.pedidos = self.db["pedidos"]

    def criar_indices(self):
        self.produtos.create_index([("sku", ASCENDING)], unique=True)
        self.produtos.create_index([("categoria", ASCENDING)])
        self.clientes.create_index([("email", ASCENDING)], unique=True)
        self.pedidos.create_index([("cliente_id", ASCENDING), ("criado_em", DESCENDING)])

    def limpar_dados(self):
        self.produtos.delete_many({})
        self.clientes.delete_many({})
        self.pedidos.delete_many({})

    def listar_produtos(self, categoria: str = None, busca: str = None):
        filtro = {}
        if categoria and categoria != "Todas":
            filtro["categoria"] = categoria
        if busca:
            filtro["nome"] = {"$regex": busca.strip(), "$options": "i"}

        # Retorna sem o _id interno do Mongo para facilitar serialização no cache
        return list(self.produtos.find(filtro, {"_id": 0}).sort("nome", ASCENDING))

    def buscar_produto_por_sku(self, sku: str):
        return self.produtos.find_one({"sku": sku}, {"_id": 0})

    def buscar_produtos_por_skus(self, skus: list[str]):
        if not skus:
            return []
        return list(self.produtos.find({"sku": {"$in": skus}}, {"_id": 0}))

    def listar_clientes(self):
        return list(self.clientes.find({}, {"_id": 0, "senha": 0}).sort("nome", ASCENDING))

    def autenticar_cliente(self, email: str, senha: str):
        if not email or not senha:
            return None
        cliente = self.clientes.find_one(
            {"email": email.strip().lower(), "senha": senha.strip()},
            {"_id": 0, "senha": 0}
        )
        return cliente

    def cadastrar_cliente(self, nome: str, email: str, senha: str, cidade: str):
        email_limpo = email.strip().lower()
        if self.clientes.find_one({"email": email_limpo}):
            return None

        total_atual = self.clientes.count_documents({})
        novo_cliente = {
            "id": f"cli_{total_atual + 1:02d}",
            "nome": nome.strip(),
            "email": email_limpo,
            "senha": senha.strip(),
            "cidade": cidade.strip() or "São Paulo, SP"
        }
        self.clientes.insert_one(novo_cliente.copy())
        novo_cliente.pop("senha", None)
        return novo_cliente

    def registrar_pedido(self, cliente_id: str, itens: list[dict]):
        total = sum(item["preco"] * item["quantidade"] for item in itens)

        # Abate o estoque de cada item comprado
        for item in itens:
            self.produtos.update_one(
                {"sku": item["sku"], "estoque": {"$gte": item["quantidade"]}},
                {"$inc": {"estoque": -item["quantidade"]}}
            )

        pedido = {
            "codigo": f"PED-{int(datetime.now().timestamp())}",
            "cliente_id": cliente_id,
            "itens": itens,
            "total": round(total, 2),
            "status": "Confirmado",
            "criado_em": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        self.pedidos.insert_one(pedido)
        pedido.pop("_id", None)
        return pedido

    def listar_pedidos_cliente(self, cliente_id: str):
        return list(
            self.pedidos.find({"cliente_id": cliente_id}, {"_id": 0})
            .sort("codigo", DESCENDING)
        )

