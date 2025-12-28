from .models import Categoria

def lista_categorias(request):
    # Retorna todas as categorias para ficarem disponíveis em qualquer template
    return {
        'categorias_globais': Categoria.objects.all()
    }
