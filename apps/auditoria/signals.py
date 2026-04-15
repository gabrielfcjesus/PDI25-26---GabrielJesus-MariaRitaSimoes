"""
apps/auditoria/signals.py
Registo automático de eventos de autenticação via signals do Django.
"""
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.dispatch import receiver
from .service import audit


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    audit(
        'login',
        request=request,
        utilizador=user,
        modulo='core',
        descricao=f'Login com sucesso — {user.username}',
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    nome = user.username if user else 'desconhecido'
    audit(
        'logout',
        request=request,
        utilizador=user,
        modulo='core',
        descricao=f'Logout — {nome}',
    )


@receiver(user_login_failed)
def on_login_failed(sender, credentials, request, **kwargs):
    audit(
        'login_falhado',
        request=request,
        modulo='core',
        descricao=f'Tentativa de login falhada — utilizador: {credentials.get("username", "?")}',
    )
