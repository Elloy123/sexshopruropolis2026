from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    path("carrinho/", views.carrinho_detalhe, name="carrinho"),
    path("carrinho/adicionar/<int:produto_id>/", views.carrinho_adicionar, name="carrinho_adicionar"),
    path("carrinho/atualizar/<int:produto_id>/", views.carrinho_atualizar, name="carrinho_atualizar"),
    path("carrinho/remover/<int:produto_id>/", views.carrinho_remover, name="carrinho_remover"),
    path("carrinho/limpar/", views.carrinho_limpar, name="carrinho_limpar"),
     path("produto/<int:id>/", views.produto_detalhe, name="produto_detalhe"),
]
