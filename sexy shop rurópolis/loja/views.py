from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Produto
from .cart import Carrinho


def home(request):
    categorias = Categoria.objects.all()
    slug = request.GET.get("cat")
    filtro = request.GET.get("filtro", "padrao")  # Pega o filtro da URL (padrão é 'padrao')
    
    produtos = Produto.objects.filter(ativo=True).select_related("categoria")
    
    categoria_ativa = None
    if slug:
        categoria_ativa = get_object_or_404(Categoria, slug=slug)
        produtos = produtos.filter(categoria=categoria_ativa)
    
    # Aplica o filtro de ordenação
    if filtro == "mais_vendidos":
        produtos = produtos.order_by('-vendas')  # Mais vendidos primeiro
    elif filtro == "mais_baratos":
        produtos = produtos.order_by('preco')  # Mais baratos primeiro
    elif filtro == "mais_caros":
        produtos = produtos.order_by('-preco')  # Mais caros primeiro
    # Se filtro == "padrao", mantém a ordem padrão (geralmente por ID ou criação)
    
    carrinho = Carrinho(request)
    
    return render(request, "loja/home.html", {
        "categorias": categorias,
        "produtos": produtos,
        "categoria_ativa": categoria_ativa,
        "carrinho_qtd": carrinho.count(),
        "filtro_ativo": filtro,  # Passa o filtro ativo para o template
    })



def carrinho_detalhe(request):
    carrinho = Carrinho(request)
    return render(
        request,
        "loja/carrinho.html",
        {
            "itens": list(carrinho),
            "total": carrinho.total(),
            "carrinho_qtd": carrinho.count(),
        },
    )


def carrinho_adicionar(request, produto_id):
    if request.method != "POST":
        return redirect("home")

    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    carrinho = Carrinho(request)

    try:
        qtd = int(request.POST.get("qtd", "1"))
    except ValueError:
        qtd = 1

    if qtd <= 0:
        messages.error(request, "Quantidade inválida.")
        return redirect(request.POST.get("next", "home"))

    # Regra simples de estoque
    if produto.estoque > 0:
        atual = 0
        for item in carrinho:
            if item["produto"].id == produto.id:
                atual = item["qtd"]
                break
        if atual + qtd > produto.estoque:
            messages.error(request, f"Estoque insuficiente. Disponível: {produto.estoque}.")
            return redirect(request.POST.get("next", "home"))

    carrinho.add(produto, qtd=qtd)
    messages.success(request, f"Adicionado ao carrinho: {produto.nome}")

    # Redireciona de volta para a página de origem (home ou detalhe)
    return redirect(request.POST.get("next", "home"))


    carrinho.add(produto, qtd=qtd)
    messages.success(request, f"Adicionado ao carrinho: {produto.nome}")
    return redirect("carrinho")


def carrinho_atualizar(request, produto_id):
    if request.method != "POST":
        return redirect("carrinho")

    produto = get_object_or_404(Produto, id=produto_id, ativo=True)
    carrinho = Carrinho(request)

    try:
        qtd = int(request.POST.get("qtd", "1"))
    except ValueError:
        qtd = 1

    if qtd < 0:
        messages.error(request, "Quantidade inválida.")
        return redirect("carrinho")

    if produto.estoque > 0 and qtd > produto.estoque:
        messages.error(request, f"Estoque insuficiente. Disponível: {produto.estoque}.")
        return redirect("carrinho")

    carrinho.add(produto, qtd=qtd, override=True)
    messages.success(request, "Carrinho atualizado.")
    return redirect("carrinho")


def carrinho_remover(request, produto_id):
    carrinho = Carrinho(request)
    carrinho.remove(produto_id)
    messages.success(request, "Item removido.")
    return redirect("carrinho")


def carrinho_limpar(request):
    carrinho = Carrinho(request)
    carrinho.clear()
    messages.success(request, "Carrinho limpo.")
    return redirect("carrinho")

def produto_detalhe(request, id):
    produto = get_object_or_404(Produto, id=id, ativo=True)
    carrinho = Carrinho(request)

    # Sugestões de outros produtos (mesma categoria, excluindo o atual)
    relacionados = Produto.objects.filter(
        ativo=True,
        categoria=produto.categoria
    ).exclude(id=produto.id)[:6]  # limita a 6 itens

    return render(request, "loja/produto_detalhe.html", {
        "produto": produto,
        "carrinho_qtd": carrinho.count(),
        "relacionados": relacionados,
    })



def lista_categorias(request):
    return {
        'categorias_globais': Categoria.objects.all()
    }
