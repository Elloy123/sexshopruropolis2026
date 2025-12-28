from decimal import Decimal
from .models import Produto


class Carrinho:
    SESSION_KEY = "carrinho"

    def __init__(self, request):
        self.session = request.session
        carrinho = self.session.get(self.SESSION_KEY)
        if not carrinho:
            carrinho = self.session[self.SESSION_KEY] = {}
        self.carrinho = carrinho

    def add(self, produto: Produto, qtd=1, override=False):
        pid = str(produto.id)
        if pid not in self.carrinho:
            self.carrinho[pid] = {"qtd": 0, "preco": str(produto.preco)}

        if override:
            self.carrinho[pid]["qtd"] = int(qtd)
        else:
            self.carrinho[pid]["qtd"] += int(qtd)

        if self.carrinho[pid]["qtd"] <= 0:
            self.remove(produto.id)

        self.save()

    def remove(self, produto_id: int):
        pid = str(produto_id)
        if pid in self.carrinho:
            del self.carrinho[pid]
            self.save()

    def clear(self):
        self.session[self.SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        produto_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produto_ids, ativo=True).select_related("categoria")

        for p in produtos:
            item = self.carrinho[str(p.id)]
            qtd = int(item["qtd"])
            preco = Decimal(item["preco"])
            subtotal = preco * qtd
            yield {
                "produto": p,
                "qtd": qtd,
                "preco": preco,
                "subtotal": subtotal,
            }

    def total(self):
        total = Decimal("0.00")
        for item in self:
            total += item["subtotal"]
        return total

    def count(self):
        return sum(int(i["qtd"]) for i in self.carrinho.values())
