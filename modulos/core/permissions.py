"""
apps/core/permissions.py
Sistema de permissões por departamento
"""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps


class DepartamentoRequiredMixin(LoginRequiredMixin):
    """
    Mixin para views baseadas em classes.
    Define 'departamentos_permitidos' na view para controlar acesso.

    Exemplo de uso:
        class MinhaView(DepartamentoRequiredMixin, ListView):
            departamentos_permitidos = ['rh', 'direcao']
    """
    departamentos_permitidos = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if request.user.is_direcao:
            return super().dispatch(request, *args, **kwargs)

        codigo = request.user.codigo_departamento
        if self.departamentos_permitidos and codigo not in self.departamentos_permitidos:
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)


def departamento_required(departamentos):
    """
    Decorator para views baseadas em funções.

    Exemplo de uso:
        @departamento_required(['armazem', 'direcao'])
        def minha_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('core:login')

            if request.user.is_direcao:
                return view_func(request, *args, **kwargs)

            codigo = request.user.codigo_departamento
            if codigo not in departamentos:
                raise PermissionDenied

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# Módulos visíveis por departamento
MODULOS_POR_DEPARTAMENTO = {
    'direcao': ['dashboard', 'utilizadores', 'rh', 'planeamento', 'armazem',
                'producao', 'qualidade', 'expedicao', 'montagem'],
    'rh': ['dashboard', 'rh'],
    'planeamento': ['dashboard', 'planeamento'],
    'armazem': ['dashboard', 'armazem'],
    'producao': ['dashboard', 'producao'],
    'qualidade': ['dashboard', 'qualidade'],
    'expedicao': ['dashboard', 'expedicao'],
    'montagem': ['dashboard', 'montagem'],
}


def get_modulos_disponiveis(user):
    """Retorna lista de módulos disponíveis para o utilizador"""
    if user.is_direcao:
        return MODULOS_POR_DEPARTAMENTO['direcao']
    codigo = user.codigo_departamento
    return MODULOS_POR_DEPARTAMENTO.get(codigo, ['dashboard'])
