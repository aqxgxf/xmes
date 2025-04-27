from django.http import FileResponse, Http404
import os
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def pdf_view(request, path):
    # 去除多余的drawings/前缀，确保只拼接一次
    rel_path = path
    if rel_path.startswith('drawings/'):
        rel_path = rel_path[len('drawings'):]
    file_path = os.path.join(settings.MEDIA_ROOT, 'drawings', rel_path)
    if not os.path.exists(file_path):
        raise Http404()
    response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
    if 'X-Frame-Options' in response:
        del response['X-Frame-Options']
    response['X-Frame-Options'] = ''
    return response

def convert_image_to_pdf(file_field, pdf_name):
    """
    将图片文件（bmp/jpg/jpeg/png）转为PDF，返回ContentFile对象和新文件名
    """
    file_ext = file_field.name.split('.')[-1].lower()
    image_exts = ['bmp', 'jpg', 'jpeg', 'png']
    if file_ext in image_exts:
        file_field.seek(0)
        try:
            image = Image.open(file_field)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            pdf_bytes = BytesIO()
            image.save(pdf_bytes, format='PDF')
            pdf_bytes.seek(0)
            return ContentFile(pdf_bytes.read()), pdf_name
        except Exception as e:
            print(f"图片转PDF失败: {e}")
            return None, None
    return None, None