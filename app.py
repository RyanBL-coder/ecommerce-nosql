import os
import base64
import streamlit as st
from database.mongo_service import MongoService
from database.redis_service import RedisService
from database.neo4j_service import Neo4jService

st.set_page_config(
    page_title="Vértice Hardware & Periféricos",
    layout="wide",
    initial_sidebar_state="expanded"
)


def aplicar_estilos_alinhamento():
    st.markdown(
        """
        <style>
        /* Container fixo para todas as imagens dos produtos */
        .box-imagem-produto {
            width: 100%;
            height: 210px;
            border-radius: 8px;
            overflow: hidden;
            background-color: #1e293b;
            margin-bottom: 0.65rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .box-imagem-produto img {
            width: 100% !important;
            height: 210px !important;
            object-fit: cover !important;
            object-position: center !important;
            display: block;
        }

        /* Altura rigorosamente fixa para os títulos (2 ou 3 linhas) */
        .titulo-produto-card {
            font-size: 1.15rem;
            font-weight: 700;
            line-height: 1.35;
            height: 4.1rem;
            margin-top: 0.2rem;
            margin-bottom: 0.35rem;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


@st.cache_data(show_spinner=False)
def obter_src_imagem(caminho_ou_url: str) -> str:
    if not caminho_ou_url:
        return ""
    if caminho_ou_url.startswith("http"):
        return caminho_ou_url
    if os.path.exists(caminho_ou_url):
        with open(caminho_ou_url, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    return ""


@st.cache_resource
def iniciar_servicos():
    mongo = MongoService()
    redis_srv = RedisService()
    neo4j_srv = Neo4jService()

    try:
        cliente_teste = mongo.clientes.find_one({"email": "lucas.andrade@email.com"})
        produto_teste = mongo.produtos.find_one({"sku": "MON-LG-24GN60R"})
        if (
            not cliente_teste
            or "senha" not in cliente_teste
            or mongo.produtos.count_documents({}) < 10
            or not produto_teste
            or "imagem" not in produto_teste
        ):
            from seed import executar_seed
            executar_seed()
    except Exception:
        pass

    return mongo, redis_srv, neo4j_srv


def formatar_moeda(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def carregar_catalogo(mongo: MongoService, redis_srv: RedisService, categoria: str, busca: str):
    chave_cache = f"{categoria or 'Todas'}:{busca.strip().lower() if busca else 'tudo'}"
    try:
        em_cache = redis_srv.obter_catalogo_cache(chave_cache)
        if em_cache is not None:
            return em_cache
    except Exception:
        pass

    produtos = mongo.listar_produtos(categoria=categoria, busca=busca)
    try:
        redis_srv.salvar_catalogo_cache(produtos, chave_cache)
    except Exception:
        pass
    return produtos


def renderizar_tela_login(mongo: MongoService, redis_srv: RedisService, neo4j_srv: Neo4jService):
    col_esq, col_centro, col_dir = st.columns([1, 1.4, 1])
    with col_centro:
        st.title("Vértice Tech")
        st.caption("Acesse sua conta para gerenciar seu carrinho, pedidos e recomendações.")

        aba_entrar, aba_cadastro = st.tabs(["Entrar", "Criar Conta"])

        with aba_entrar:
            with st.container(border=True):
                with st.form("form_login"):
                    email = st.text_input("E-mail", placeholder="lucas.andrade@email.com")
                    senha = st.text_input("Senha", type="password", placeholder="Sua senha")
                    submetido = st.form_submit_button("Entrar na Loja", type="primary", use_container_width=True)
                    if submetido:
                        cliente = mongo.autenticar_cliente(email, senha)
                        if cliente:
                            token = redis_srv.criar_sessao_login(cliente)
                            st.session_state["cliente_logado"] = cliente
                            st.session_state["token_sessao"] = token
                            st.toast(f"Bem-vindo(a), {cliente['nome']}!")
                            st.rerun()
                        else:
                            st.error("E-mail ou senha inválidos.")

        with aba_cadastro:
            with st.container(border=True):
                with st.form("form_cadastro"):
                    nome_novo = st.text_input("Nome completo", placeholder="Ex.: Gabriel Souza")
                    email_novo = st.text_input("E-mail", placeholder="gabriel@email.com")
                    cidade_nova = st.text_input("Cidade / UF", placeholder="Ex.: São Paulo, SP")
                    senha_nova = st.text_input("Senha", type="password", placeholder="Crie uma senha")
                    cadastrar = st.form_submit_button("Criar minha conta", type="primary", use_container_width=True)
                    if cadastrar:
                        if not nome_novo.strip() or not email_novo.strip() or not senha_nova.strip():
                            st.warning("Preencha nome, e-mail e senha para continuar.")
                        else:
                            novo = mongo.cadastrar_cliente(nome_novo, email_novo, senha_nova, cidade_nova)
                            if not novo:
                                st.error("Este e-mail já está cadastrado.")
                            else:
                                neo4j_srv.sincronizar_cliente(novo["id"], novo["nome"])
                                token = redis_srv.criar_sessao_login(novo)
                                st.session_state["cliente_logado"] = novo
                                st.session_state["token_sessao"] = token
                                st.toast("Conta criada com sucesso!")
                                st.rerun()


def renderizar_card_produto(
    produto: dict,
    cliente_id: str,
    redis_srv: RedisService,
    neo4j_srv: Neo4jService,
    sufixo_chave: str,
    qtd_no_carrinho: int = 0,
    stats_avaliacao: dict = None,
    nota_cliente: int = None
):
    with st.container(border=True):
        src_img = obter_src_imagem(produto.get("imagem", ""))
        if src_img:
            st.markdown(
                f'<div class="box-imagem-produto"><img src="{src_img}" alt="{produto["nome"]}"></div>',
                unsafe_allow_html=True
            )

        media = stats_avaliacao.get("media", 5.0) if stats_avaliacao else 5.0
        total_av = stats_avaliacao.get("total", 0) if stats_avaliacao else 0
        texto_av = f"⭐ {media:.1f} ({total_av})" if total_av > 0 else "⭐ Novo"

        st.caption(f"{produto['marca']} • {produto['categoria']} • {texto_av}")
        st.markdown(f'<div class="titulo-produto-card">{produto["nome"]}</div>', unsafe_allow_html=True)

        estoque_total = produto.get("estoque", 0)
        disponivel = max(0, estoque_total - qtd_no_carrinho)

        col_preco, col_estoque = st.columns([2, 1])
        with col_preco:
            st.metric(label="Preço à vista", value=formatar_moeda(produto["preco"]))
        with col_estoque:
            status_estoque = f"{disponivel} un. disponíveis" if disponivel > 0 else "Limite atingido"
            st.caption(status_estoque)

        with st.expander("Especificações & Avaliação"):
            especificacoes = produto.get("especificacoes", {})
            for chave, valor in especificacoes.items():
                st.markdown(f"**{chave}:** {valor}")

            st.divider()
            indice_padrao = (nota_cliente - 1) if nota_cliente and 1 <= nota_cliente <= 5 else 4
            col_nota, col_btn_av = st.columns([2, 1])
            with col_nota:
                nota_escolhida = st.selectbox(
                    "Sua nota (Neo4j [:AVALIOU])",
                    options=[1, 2, 3, 4, 5],
                    index=indice_padrao,
                    format_func=lambda x: f"{x} ★",
                    key=f"sel_av_{sufixo_chave}_{produto['sku']}"
                )
            with col_btn_av:
                st.write("")
                if st.button("Avaliar", key=f"btn_av_{sufixo_chave}_{produto['sku']}", use_container_width=True):
                    neo4j_srv.registrar_avaliacao(cliente_id, produto["sku"], nota_escolhida)
                    st.toast(f"Avaliação ({nota_escolhida}★) salva no grafo Neo4j!")
                    st.rerun()

        desabilitado = disponivel <= 0
        texto_botao = (
            f"Adicionar ao carrinho ({qtd_no_carrinho} no carrinho)"
            if qtd_no_carrinho > 0 and not desabilitado
            else ("Adicionar ao carrinho" if not desabilitado else "Estoque máximo no carrinho")
        )

        if st.button(
            texto_botao,
            key=f"add_{sufixo_chave}_{produto['sku']}",
            use_container_width=True,
            type="primary",
            disabled=desabilitado
        ):
            redis_srv.adicionar_ao_carrinho(cliente_id, produto, 1)
            st.toast(f"{produto['nome']} adicionado ao carrinho.")
            st.rerun()


def renderizar_grade_produtos(
    lista_produtos: list[dict],
    cliente_id: str,
    redis_srv: RedisService,
    neo4j_srv: Neo4jService,
    sufixo_chave: str,
    mapa_qtd_carrinho: dict[str, int],
    mapa_stats_av: dict[str, dict],
    mapa_notas_cli: dict[str, int]
):
    for i in range(0, len(lista_produtos), 3):
        colunas = st.columns(3)
        for j, produto in enumerate(lista_produtos[i:i + 3]):
            sku = produto["sku"]
            with colunas[j]:
                renderizar_card_produto(
                    produto,
                    cliente_id,
                    redis_srv,
                    neo4j_srv,
                    sufixo_chave=sufixo_chave,
                    qtd_no_carrinho=mapa_qtd_carrinho.get(sku, 0),
                    stats_avaliacao=mapa_stats_av.get(sku),
                    nota_cliente=mapa_notas_cli.get(sku)
                )


def main():
    aplicar_estilos_alinhamento()
    mongo, redis_srv, neo4j_srv = iniciar_servicos()

    token_atual = st.session_state.get("token_sessao")
    dados_sessao = redis_srv.validar_sessao_login(token_atual) if token_atual else None

    if "cliente_logado" not in st.session_state or st.session_state["cliente_logado"] is None:
        renderizar_tela_login(mongo, redis_srv, neo4j_srv)
        return

    cliente_atual = st.session_state["cliente_logado"]
    cliente_id = cliente_atual["id"]

    # Caso a chave de sessão no Redis tenha sido limpa por um seed recente, recria o token ativo
    if not dados_sessao:
        token_atual = redis_srv.criar_sessao_login(cliente_atual)
        st.session_state["token_sessao"] = token_atual
        dados_sessao = redis_srv.validar_sessao_login(token_atual)

    with st.sidebar:
        st.title("Vértice Tech")
        st.caption("Informática e Periféricos de Alta Performance")
        st.divider()
        st.markdown(f"**{cliente_atual['nome']}**")
        st.caption(f"{cliente_atual['email']} • {cliente_atual.get('cidade', '')}")

        if dados_sessao and dados_sessao.get("token"):
            ttl_min = dados_sessao.get("ttl_restante", 7200) // 60
            st.caption(f"🔐 Token Redis: `{dados_sessao['token'][:8]}...` (TTL: {ttl_min}m)")

        if st.button("Sair da conta", use_container_width=True):
            redis_srv.encerrar_sessao_login(token=token_atual, cliente_id=cliente_id)
            st.session_state["cliente_logado"] = None
            st.session_state["token_sessao"] = None
            st.rerun()

        st.divider()
        itens_carrinho = redis_srv.obter_carrinho(cliente_id)
        qtd_total = sum(i["quantidade"] for i in itens_carrinho)
        valor_total = sum(i["preco"] * i["quantidade"] for i in itens_carrinho)

        col_resumo1, col_resumo2 = st.columns(2)
        with col_resumo1:
            st.metric("Itens no carrinho", qtd_total)
        with col_resumo2:
            st.metric("Subtotal", formatar_moeda(valor_total))

    aba_catalogo, aba_recomendacoes, aba_carrinho, aba_pedidos = st.tabs([
        "Catálogo de Produtos",
        "Sugestões para Você",
        f"Meu Carrinho ({qtd_total})",
        "Meus Pedidos"
    ])

    mapa_qtd_carrinho = {i["sku"]: i["quantidade"] for i in itens_carrinho}
    mapa_stats_av = neo4j_srv.obter_estatisticas_avaliacoes()
    mapa_notas_cli = neo4j_srv.obter_avaliacoes_cliente(cliente_id)

    with aba_catalogo:
        col_busca, col_cat = st.columns([3, 1])
        with col_busca:
            termo_busca = st.text_input(
                "Buscar equipamento",
                placeholder="Ex.: Monitor 144Hz, Teclado Mecânico, SSD 1TB..."
            )
        with col_cat:
            categoria_filtro = st.selectbox(
                "Categoria",
                options=[
                    "Todas",
                    "Monitores",
                    "Periféricos",
                    "Hardware",
                    "Armazenamento",
                    "Áudio & Streaming",
                    "Redes & Energia",
                    "Ergonomia & Setup"
                ]
            )

        produtos = carregar_catalogo(mongo, redis_srv, categoria_filtro, termo_busca)

        if not produtos:
            st.info("Nenhum produto encontrado para os filtros selecionados.")
        else:
            renderizar_grade_produtos(
                produtos,
                cliente_id,
                redis_srv,
                neo4j_srv,
                "cat",
                mapa_qtd_carrinho,
                mapa_stats_av,
                mapa_notas_cli
            )

    with aba_recomendacoes:
        st.subheader(f"Selecionados para {cliente_atual['nome'].split()[0]}")
        st.caption("Sugestões geradas via Neo4j considerando nós (:Cliente), (:Produto) e (:Categoria) e relações [:COMPROU] e [:AVALIOU].")

        skus_recomendados = neo4j_srv.recomendar_para_cliente(cliente_id, limite=6)
        produtos_recomendados = mongo.buscar_produtos_por_skus(skus_recomendados)

        mapa_rec = {p["sku"]: p for p in produtos_recomendados}
        produtos_ordenados = [mapa_rec[sku] for sku in skus_recomendados if sku in mapa_rec]

        if not produtos_ordenados:
            st.info("Continue navegando, avaliando e realizando pedidos para receber sugestões personalizadas.")
        else:
            renderizar_grade_produtos(
                produtos_ordenados,
                cliente_id,
                redis_srv,
                neo4j_srv,
                "rec",
                mapa_qtd_carrinho,
                mapa_stats_av,
                mapa_notas_cli
            )

    with aba_carrinho:
        st.subheader("Seu Carrinho de Compras")

        if not itens_carrinho:
            st.info("Seu carrinho está vazio no momento. Explore o catálogo para adicionar produtos.")
        else:
            for item in itens_carrinho:
                with st.container(border=True):
                    c_nome, c_preco, c_qtd, c_subtotal, c_remover = st.columns([3, 1.5, 1.5, 1.5, 1])
                    with c_nome:
                        st.markdown(f"**{item['nome']}**")
                        st.caption(item.get("categoria", ""))
                    with c_preco:
                        st.caption("Preço unitário")
                        st.write(formatar_moeda(item["preco"]))
                    with c_qtd:
                        nova_qtd = st.number_input(
                            "Qtd",
                            min_value=1,
                            max_value=50,
                            value=int(item["quantidade"]),
                            key=f"qtd_{item['sku']}",
                            label_visibility="collapsed"
                        )
                        if nova_qtd != item["quantidade"]:
                            redis_srv.atualizar_quantidade(cliente_id, item["sku"], nova_qtd)
                            st.rerun()
                    with c_subtotal:
                        st.caption("Subtotal")
                        st.markdown(f"**{formatar_moeda(item['preco'] * item['quantidade'])}**")
                    with c_remover:
                        if st.button("Remover", key=f"rem_{item['sku']}", use_container_width=True):
                            redis_srv.remover_item(cliente_id, item["sku"])
                            st.toast("Item removido do carrinho.")
                            st.rerun()

            st.divider()
            col_frete, col_total, col_acao = st.columns([2, 1.5, 1.5])
            with col_frete:
                st.metric("Frete Expresso", "Grátis")
            with col_total:
                st.metric("Total do Pedido", formatar_moeda(valor_total))
            with col_acao:
                st.write("")
                if st.button("Finalizar Compra", type="primary", use_container_width=True):
                    pedido = mongo.registrar_pedido(cliente_id, itens_carrinho)
                    skus_comprados = [i["sku"] for i in itens_carrinho]
                    neo4j_srv.registrar_compra(cliente_id, skus_comprados)
                    redis_srv.limpar_carrinho(cliente_id)
                    redis_srv.invalidar_cache_catalogo()
                    st.toast(f"Pedido {pedido['codigo']} confirmado com sucesso!")
                    st.rerun()

            skus_no_carrinho = [i["sku"] for i in itens_carrinho]
            skus_complementares = neo4j_srv.comprados_juntos(skus_no_carrinho, limite=3)
            complementares = mongo.buscar_produtos_por_skus(skus_complementares)

            if complementares:
                st.divider()
                st.subheader("Frequentemente comprados juntos")
                renderizar_grade_produtos(
                    complementares,
                    cliente_id,
                    redis_srv,
                    neo4j_srv,
                    "comp",
                    mapa_qtd_carrinho,
                    mapa_stats_av,
                    mapa_notas_cli
                )

    with aba_pedidos:
        st.subheader("Histórico de Pedidos")
        pedidos = mongo.listar_pedidos_cliente(cliente_id)

        if not pedidos:
            st.info("Você ainda não realizou nenhum pedido nesta conta.")
        else:
            for pedido in pedidos:
                with st.container(border=True):
                    cab1, cab2, cab3 = st.columns([2, 1.5, 1.5])
                    with cab1:
                        st.markdown(f"**Pedido {pedido['codigo']}**")
                        st.caption(f"Realizado em {pedido['criado_em']}")
                    with cab2:
                        st.caption("Status")
                        st.markdown(f"**{pedido['status']}**")
                    with cab3:
                        st.metric("Valor Total", formatar_moeda(pedido["total"]))

                    st.divider()
                    for item in pedido["itens"]:
                        lin1, lin2, lin3 = st.columns([4, 1, 1.5])
                        with lin1:
                            st.write(item["nome"])
                        with lin2:
                            st.caption(f"{item['quantidade']}x")
                        with lin3:
                            st.write(formatar_moeda(item["preco"] * item["quantidade"]))


if __name__ == "__main__":
    main()
