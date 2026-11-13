import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jService:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "neo4j+s://d316318f.databases.neo4j.io").strip()
        # Corrige caso o usuário tenha colado o prefixo duplicado no .env
        if uri.startswith("neo4j+s:neo4j+s://"):
            uri = uri.replace("neo4j+s:neo4j+s://", "neo4j+s://", 1)

        user = os.getenv("NEO4J_USERNAME", "neo4j").strip()
        password = os.getenv(
            "NEO4J_PASSWORD",
            "7hZ2SFDWNy--PPwepbGigKc-Za89Pj-rDRebFy7ZcL8"
        ).strip()
        self.database = os.getenv("NEO4J_DATABASE", "neo4j").strip()

        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception:
            self.driver = None

    def fechar(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass

    def criar_constraints(self):
        if not self.driver:
            return
        queries = [
            "CREATE CONSTRAINT cliente_id_unique IF NOT EXISTS FOR (c:Cliente) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT produto_sku_unique IF NOT EXISTS FOR (p:Produto) REQUIRE p.sku IS UNIQUE",
            "CREATE CONSTRAINT categoria_nome_unique IF NOT EXISTS FOR (cat:Categoria) REQUIRE cat.nome IS UNIQUE"
        ]
        try:
            with self.driver.session(database=self.database) as session:
                for q in queries:
                    session.run(q)
        except Exception:
            pass

    def limpar_dados(self):
        if not self.driver:
            return
        try:
            with self.driver.session(database=self.database) as session:
                session.run("MATCH (n) DETACH DELETE n")
        except Exception:
            pass

    def sincronizar_cliente(self, cliente_id: str, nome: str):
        if not self.driver:
            return
        query = """
        MERGE (c:Cliente {id: $id})
        SET c.nome = $nome
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, id=cliente_id, nome=nome)
        except Exception:
            pass

    def sincronizar_produto(self, sku: str, nome: str, categoria: str):
        if not self.driver:
            return
        # Cria nós (:Produto) e (:Categoria) conectados por [:PERTENCE_A]
        query = """
        MERGE (p:Produto {sku: $sku})
        SET p.nome = $nome, p.categoria = $categoria
        MERGE (cat:Categoria {nome: $categoria})
        MERGE (p)-[:PERTENCE_A]->(cat)
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, sku=sku, nome=nome, categoria=categoria)
        except Exception:
            pass

    def registrar_compra(self, cliente_id: str, skus: list[str]):
        if not self.driver or not skus:
            return
        query = """
        MATCH (c:Cliente {id: $cliente_id})
        UNWIND $skus AS sku
        MATCH (p:Produto {sku: sku})
        MERGE (c)-[r:COMPROU]->(p)
        ON CREATE SET r.vezes = 1
        ON MATCH SET r.vezes = r.vezes + 1
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, cliente_id=cliente_id, skus=skus)
        except Exception:
            pass

    def registrar_avaliacao(self, cliente_id: str, sku: str, nota: int):
        if not self.driver or not cliente_id or not sku:
            return
        # Cria ou atualiza o relacionamento [:AVALIOU {nota}] entre (:Cliente) e (:Produto)
        query = """
        MATCH (c:Cliente {id: $cliente_id})
        MATCH (p:Produto {sku: $sku})
        MERGE (c)-[a:AVALIOU]->(p)
        SET a.nota = toInteger($nota), a.atualizado_em = timestamp()
        """
        try:
            with self.driver.session(database=self.database) as session:
                session.run(query, cliente_id=cliente_id, sku=sku, nota=int(nota))
        except Exception:
            pass

    def obter_estatisticas_avaliacoes(self) -> dict[str, dict]:
        if not self.driver:
            return {}
        query = """
        MATCH (:Cliente)-[a:AVALIOU]->(p:Produto)
        RETURN p.sku AS sku, round(avg(toFloat(a.nota)), 1) AS media, count(a) AS total
        """
        try:
            with self.driver.session(database=self.database) as session:
                resultado = session.run(query)
                return {
                    r["sku"]: {"media": float(r["media"]), "total": int(r["total"])}
                    for r in resultado
                }
        except Exception:
            return {}

    def obter_avaliacoes_cliente(self, cliente_id: str) -> dict[str, int]:
        if not self.driver or not cliente_id:
            return {}
        query = """
        MATCH (c:Cliente {id: $cliente_id})-[a:AVALIOU]->(p:Produto)
        RETURN p.sku AS sku, a.nota AS nota
        """
        try:
            with self.driver.session(database=self.database) as session:
                resultado = session.run(query, cliente_id=cliente_id)
                return {r["sku"]: int(r["nota"]) for r in resultado}
        except Exception:
            return {}

    def recomendar_para_cliente(self, cliente_id: str, limite: int = 6) -> list[str]:
        if not self.driver:
            return []
        # Combina filtragem colaborativa ([:COMPROU] e [:AVALIOU]) + navegação pelo nó (:Categoria)
        query = """
        MATCH (c:Cliente {id: $cliente_id})
        OPTIONAL MATCH (c)-[:COMPROU|AVALIOU]->(p:Produto)<-[:COMPROU|AVALIOU]-(outro:Cliente)-[r_outro:COMPROU|AVALIOU]->(rec_colab:Produto)
        WHERE c <> outro AND NOT (c)-[:COMPROU]->(rec_colab)
        WITH c, collect(DISTINCT {sku: rec_colab.sku, peso: COALESCE(r_outro.nota, 4)}) AS colab
        OPTIONAL MATCH (c)-[r2:COMPROU|AVALIOU]->(p2:Produto)-[:PERTENCE_A]->(cat:Categoria)<-[:PERTENCE_A]-(rec_cat:Produto)
        WHERE NOT (c)-[:COMPROU]->(rec_cat)
        WITH c, colab + collect(DISTINCT {sku: rec_cat.sku, peso: COALESCE(r2.vezes, 1) * 2}) AS candidatos
        UNWIND candidatos AS item
        WITH item.sku AS sku, sum(item.peso) AS relevancia
        WHERE sku IS NOT NULL
        RETURN sku
        ORDER BY relevancia DESC
        LIMIT $limite
        """
        try:
            with self.driver.session(database=self.database) as session:
                resultado = session.run(query, cliente_id=cliente_id, limite=limite)
                skus = [registro["sku"] for registro in resultado]

                if len(skus) < limite:
                    complemento_query = """
                    MATCH (c:Cliente {id: $cliente_id})
                    MATCH (:Cliente)-[r:COMPROU|AVALIOU]->(rec:Produto)
                    WHERE NOT (c)-[:COMPROU]->(rec) AND NOT rec.sku IN $atuais
                    RETURN rec.sku AS sku, count(r) AS popularidade
                    ORDER BY popularidade DESC
                    LIMIT $faltam
                    """
                    faltam = limite - len(skus)
                    extra = session.run(
                        complemento_query,
                        cliente_id=cliente_id,
                        atuais=skus,
                        faltam=faltam
                    )
                    skus.extend([r["sku"] for r in extra])
                return skus
        except Exception:
            return []

    def comprados_juntos(self, skus_carrinho: list[str], limite: int = 3) -> list[str]:
        if not self.driver or not skus_carrinho:
            return []
        query = """
        MATCH (p:Produto)<-[:COMPROU]-(c:Cliente)-[:COMPROU]->(outro:Produto)
        WHERE p.sku IN $skus AND NOT outro.sku IN $skus
        RETURN outro.sku AS sku, count(DISTINCT c) AS frequencia
        ORDER BY frequencia DESC
        LIMIT $limite
        """
        try:
            with self.driver.session(database=self.database) as session:
                resultado = session.run(query, skus=skus_carrinho, limite=limite)
                return [r["sku"] for r in resultado]
        except Exception:
            return []
