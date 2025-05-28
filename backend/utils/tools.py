from django.http import FileResponse, Http404
import os
from django.conf import settings
from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
import re
import urllib.parse
import traceback

@csrf_exempt
def pdf_view(request, path):
    # 去除多余的drawings/前缀，确保只拼接一次
    rel_path = path
    if rel_path.startswith('drawings/'):
        rel_path = rel_path[len('drawings/'):]
    file_path = os.path.join(settings.MEDIA_ROOT, 'drawings', rel_path)

    # 记录请求信息，方便调试
    print(f"PDF查看请求: 原始路径={path}, 处理后路径={file_path}")

    # 检查文件存在性并确保它是一个有效的文件
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print(f"文件不存在: {file_path}")
        raise Http404('文件不存在')

    # 检查文件是否可读
    if not os.access(file_path, os.R_OK):
        print(f"文件不可读: {file_path}")
        raise Http404('文件不可读')

    # 检查文件大小
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            print(f"文件为空: {file_path}")
            raise Http404('文件为空')
    except Exception as e:
        print(f"无法访问文件: {file_path}, 错误: {e}")
        raise Http404(f'无法访问文件: {str(e)}')

    # 解析文件名，从路径中提取，不使用原始文件名
    # 默认名称为 "文档.pdf"，如果能解析出更好的名称则使用解析结果
    filename = os.path.basename(file_path)
    display_filename = "文档.pdf"

    # 尝试从文件名中解析出更有意义的名称
    # 文件名模式: 产品类代码-公司代码-图纸.pdf 或 产品类代码-公司代码-工艺.pdf
    if '-图纸' in filename:
        # 已经是新的命名格式
        display_filename = filename
    elif '-工艺' in filename:
        # 已经是新的命名格式
        display_filename = filename
    else:
        # 尝试旧格式
        pattern = r'([^-]+)-([^-]+)(?:-工艺)?\.pdf'
        match = re.match(pattern, filename)
        if match:
            code = match.group(1)
            company = match.group(2)
            if '工艺' in filename:
                display_filename = f"{code}-{company}-工艺.pdf"
            else:
                display_filename = f"{code}-{company}-图纸.pdf"

    # 尝试读取文件的前几个字节，确保它是一个有效的PDF
    try:
        with open(file_path, 'rb') as f:
            header = f.read(5)
            # PDF文件应该以%PDF-开头
            if not header.startswith(b'%PDF-'):
                print(f"无效的PDF文件: {file_path}, 头部: {header}")
                raise Http404('无效的PDF文件')
    except Exception as e:
        print(f"文件读取错误: {file_path}, 错误: {e}")
        raise Http404(f'文件读取错误: {str(e)}')

    # 创建响应
    try:
        file_handle = open(file_path, 'rb')
        response = FileResponse(file_handle, content_type='application/pdf')
    except Exception as e:
        print(f"打开文件失败: {file_path}, 错误: {e}")
        raise Http404(f'打开文件失败: {str(e)}')

    # URL编码文件名
    encoded_filename = urllib.parse.quote(display_filename)

    # 设置文件名 (UTF-8编码)，完全符合RFC规范
    response['Content-Disposition'] = f'inline; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'

    # 清除X-Frame-Options，允许在iframe中显示
    if 'X-Frame-Options' in response:
        del response['X-Frame-Options']

    # 添加必要的CORS和缓存控制头
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type, Range'
    response['Accept-Ranges'] = 'bytes'

    # 设置Content-Type头，确保浏览器正确处理
    response['Content-Type'] = 'application/pdf'

    # 避免缓存问题
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'

    print(f"PDF文件成功响应: {file_path}")
    return response

def convert_image_to_pdf(file_field, pdf_name):
    """
    将图片文件（bmp/jpg/jpeg/png）转为PDF，返回ContentFile对象和新文件名
    增加详细日志，便于排查问题。
    """
    file_ext = file_field.name.split('.')[-1].lower()
    image_exts = ['bmp', 'jpg', 'jpeg', 'png']
    if file_ext in image_exts:
        file_field.seek(0)
        try:
            image = Image.open(file_field)
            print(f'[convert_image_to_pdf] 图片格式: {image.format}, 模式: {image.mode}, 大小: {image.size}')
            if image.mode != 'RGB':
                image = image.convert('RGB')
            pdf_bytes = BytesIO()
            image.save(pdf_bytes, format='PDF')
            pdf_bytes.seek(0)
            # 保存一份调试用PDF
            try:
                import os
                debug_dir = os.path.join(settings.BASE_DIR, 'attachment')
                os.makedirs(debug_dir, exist_ok=True)
                debug_path = os.path.join(debug_dir, 'debug_test.pdf')
                with open(debug_path, 'wb') as f:
                    f.write(pdf_bytes.getvalue())
            except Exception as e:
                print(f'[convert_image_to_pdf] 保存调试PDF失败: {e}')
            return ContentFile(pdf_bytes.read()), pdf_name
        except Exception as e:
            print(f'[convert_image_to_pdf] 图片转PDF失败: {e}')
            print(traceback.format_exc())
            return None, None
    print(f'[convert_image_to_pdf] 文件扩展名不支持: {file_ext}')
    return None, None
