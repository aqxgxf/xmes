from django.http import FileResponse, Http404
import os
from django.conf import settings

def pdf_view(request, path):
    # 去除多余的drawings/前缀，确保只拼接一次
    rel_path = path
    if rel_path.startswith('drawings/'):
        rel_path = rel_path[len('drawings/'):]
    file_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    if not os.path.exists(file_path):
        raise Http404()
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    if 'X-Frame-Options' in response:
        del response['X-Frame-Options']
    return response
