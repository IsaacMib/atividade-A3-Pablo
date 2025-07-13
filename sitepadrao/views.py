from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect

def health_check(request):
    return JsonResponse({"status": "ok"}, status=200)

def redirect_if_in_group(request):
    if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.exists()):
        return redirect('/admin/manager/')
    return redirect('/')
