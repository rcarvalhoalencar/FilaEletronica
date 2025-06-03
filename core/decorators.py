from django.core.exceptions import PermissionDenied

def recepcao_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'recepcao':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper

def medico_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'medico':
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
