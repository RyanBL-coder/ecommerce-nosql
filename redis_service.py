import os
import json
import uuid
import redis
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class RedisService:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "").strip()
        if redis_url:
            self.client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5
            )
        else:
            host = os.getenv("REDIS_HOST", "localhost").strip()
            port = int(os.getenv("REDIS_PORT", 6379))
            username = os.getenv("REDIS_USERNAME", "default").strip() or "default"
            password = os.getenv("REDIS_PASSWORD", "").strip() or None

            self.client = redis.Redis(
                host=host,
                port=port,
                username=username if password else None,
                password=password,
                decode_responses=True,
                socket_connect_timeout=5
            )

    def limpar_dados(self):
        self.client.flushdb()

    # --- Controle de Sessão e Tokens de Login (TTL de 2h = 7200s) ---
    def _chave_sessao(self, token: str) -> str:
        return f"sessao:token:{token}"

    def _chave_sessao_cliente(self, cliente_id: str) -> str:
        return f"sessao:cliente:{cliente_id}"

    def criar_sessao_login(self, cliente: dict, ttl_segundos: int = 7200) -> str:
        token = uuid.uuid4().hex
        payload = {
            "token": token,
            "cliente": cliente,
            "login_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        try:
            token_antigo = self.client.get(self._chave_sessao_cliente(cliente["id"]))
            if token_antigo:
                self.client.delete(self._chave_sessao(token_antigo))

            self.client.setex(
                self._chave_sessao(token),
                ttl_segundos,
                json.dumps(payload)
            )
            self.client.setex(
                self._chave_sessao_cliente(cliente["id"]),
                ttl_segundos,
                token
            )
        except Exception:
            pass
        return token

    def validar_sessao_login(self, token: str) -> dict | None:
        if not token:
            return None
        try:
            chave = self._chave_sessao(token)
            dados_raw = self.client.get(chave)
            if not dados_raw:
                return None
            ttl_restante = self.client.ttl(chave)
            dados = json.loads(dados_raw)
            dados["ttl_restante"] = max(0, int(ttl_restante)) if ttl_restante and ttl_restante > 0 else 0
            return dados
        except Exception:
            return None

    def encerrar_sessao_login(self, token: str = None, cliente_id: str = None):
        try:
            if token:
                self.client.delete(self._chave_sessao(token))
            if cliente_id:
                tok_salvo = self.client.get(self._chave_sessao_cliente(cliente_id))
                if tok_salvo:
                    self.client.delete(self._chave_sessao(tok_salvo))
                self.client.delete(self._chave_sessao_cliente(cliente_id))
        except Exception:
            pass

    # --- Carrinho de Compras Dinâmico ---
    def _chave_carrinho(self, cliente_id: str) -> str:
        return f"carrinho:{cliente_id}"

    def obter_carrinho(self, cliente_id: str) -> list[dict]:
        itens_raw = self.client.hgetall(self._chave_carrinho(cliente_id))
        itens = []
        for sku, payload in itens_raw.items():
            dados = json.loads(payload)
            dados["sku"] = sku
            itens.append(dados)
        return itens

    def adicionar_ao_carrinho(self, cliente_id: str, produto: dict, quantidade: int = 1):
        chave = self._chave_carrinho(cliente_id)
        sku = produto["sku"]
        atual = self.client.hget(chave, sku)

        if atual:
            dados = json.loads(atual)
            dados["quantidade"] += quantidade
        else:
            dados = {
                "nome": produto["nome"],
                "preco": float(produto["preco"]),
                "categoria": produto["categoria"],
                "quantidade": quantidade
            }

        self.client.hset(chave, sku, json.dumps(dados))
        # Mantém o carrinho ativo por 24h sem ocupar memória indefinidamente
        self.client.expire(chave, 86400)

    def atualizar_quantidade(self, cliente_id: str, sku: str, quantidade: int):
        chave = self._chave_carrinho(cliente_id)
        if quantidade <= 0:
            self.client.hdel(chave, sku)
            return

        atual = self.client.hget(chave, sku)
        if atual:
            dados = json.loads(atual)
            dados["quantidade"] = quantidade
            self.client.hset(chave, sku, json.dumps(dados))

    def remover_item(self, cliente_id: str, sku: str):
        self.client.hdel(self._chave_carrinho(cliente_id), sku)

    def limpar_carrinho(self, cliente_id: str):
        self.client.delete(self._chave_carrinho(cliente_id))

    # --- Cache de Catálogo com TTL e Cache Invalidation ---
    def obter_catalogo_cache(self, chave_filtro: str = "todos"):
        dados = self.client.get(f"cache:catalogo:{chave_filtro}")
        return json.loads(dados) if dados else None

    def salvar_catalogo_cache(self, produtos: list[dict], chave_filtro: str = "todos"):
        # Guarda no cache por 60s para evitar leitura repetida no banco
        self.client.setex(
            f"cache:catalogo:{chave_filtro}",
            60,
            json.dumps(produtos)
        )

    def invalidar_cache_catalogo(self):
        chaves = self.client.keys("cache:catalogo:*")
        if chaves:
            self.client.delete(*chaves)
