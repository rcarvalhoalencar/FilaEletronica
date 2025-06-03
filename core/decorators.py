# core/decorators.py

from functools import wraps       # <<<-- adicione esta linha
from django.shortcuts import redirect
from django.contrib import messages

def recepcao_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'recepcao':
            messages.error(request, "Acesso negado: apenas Recepção pode entrar aqui.")
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped

def triagem_required(view_func):
    from functools import wraps   # ou importe no topo, conforme acima
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'triagem':
            messages.error(request, "Acesso negado: apenas Triagem pode entrar aqui.")
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped

def medico_required(view_func):
    from functools import wraps
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'medico':
            messages.error(request, "Acesso negado: apenas Médico pode entrar aqui.")
            return redirect('accounts:login')
        return view_func(request, *args, **kwargs)
    return _wrapped
