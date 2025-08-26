from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import Http404

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

def redirect_if_in_group(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.exists()):
        return redirect('/admin/manager/')
    return redirect('/')

def acesso_negado(request):
    return render(request, "403.html", status=403)

def erro_404(request, exception):
    return render(request, "404.html", status=404)

def erro_403(request, exception):
    return render(request, "403.html", status=403)
