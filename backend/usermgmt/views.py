from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.models import User, Group
import json
from .models import Menu

@csrf_exempt
def register(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        groups = data.get('groups', [])
        if not username or not password:
            return JsonResponse({'error': '用户名和密码必填'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户已存在'}, status=400)
        user = User.objects.create_user(username=username, password=password)
        if groups:
            for g in groups:
                group, _ = Group.objects.get_or_create(name=g)
                user.groups.add(group)
        return JsonResponse({'msg': '注册成功'})
    return JsonResponse({'error': '只支持POST'}, status=405)

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'msg': '登录成功'})
        else:
            return JsonResponse({'error': '用户名或密码错误'}, status=400)
    return JsonResponse({'error': '只支持POST'}, status=405)

@csrf_exempt
def user_info(request):
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list('name', flat=True))
        return JsonResponse({
            'username': request.user.username,
            'avatar': 'https://avatars.githubusercontent.com/u/1?v=4',
            'groups': groups
        })
    else:
        return JsonResponse({'error': '未登录'}, status=401)

@csrf_exempt
def user_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    users = User.objects.all()
    data = []
    for u in users:
        data.append({
            'id': u.id,
            'username': u.username,
            'groups': list(u.groups.values_list('name', flat=True))
        })
    return JsonResponse({'users': data})

@csrf_exempt
def group_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    groups = Group.objects.all().values_list('name', flat=True)
    return JsonResponse({'groups': list(groups)})

@csrf_exempt
def update_user(request, user_id):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    data = json.loads(request.body)
    try:
        user = User.objects.get(id=user_id)
        if 'username' in data:
            user.username = data['username']
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        if 'groups' in data:
            user.groups.clear()
            for g in data['groups']:
                group, _ = Group.objects.get_or_create(name=g)
                user.groups.add(group)
        user.save()
        return JsonResponse({'msg': '更新成功'})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)

@csrf_exempt
def update_group(request, group_name):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    data = json.loads(request.body)
    group, _ = Group.objects.get_or_create(name=group_name)
    if 'new_name' in data:
        group.name = data['new_name']
        group.save()
    return JsonResponse({'msg': '更新成功'})

@csrf_exempt
def add_group(request):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    data = json.loads(request.body)
    name = data.get('name')
    if not name:
        return JsonResponse({'error': '组名必填'}, status=400)
    group, created = Group.objects.get_or_create(name=name)
    if created:
        return JsonResponse({'msg': '创建成功'})
    else:
        return JsonResponse({'error': '组已存在'}, status=400)

@csrf_exempt
def delete_group(request, group_name):
    if request.method != 'POST':
        return JsonResponse({'error': '只支持POST'}, status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    try:
        group = Group.objects.get(name=group_name)
        group.delete()
        return JsonResponse({'msg': '删除成功'})
    except Group.DoesNotExist:
        return JsonResponse({'error': '组不存在'}, status=404)

@csrf_exempt
def menu_list(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    user_groups = list(request.user.groups.values_list('name', flat=True))
    if '超级管理员' in user_groups:
        menus = Menu.objects.all()
    else:
        menus = Menu.objects.filter(groups__name__in=user_groups).distinct()
    # 构建菜单树
    menu_dict = {}
    for m in menus:
        menu_dict[m.id] = {
            'id': m.id,
            'name': m.name,
            'path': m.path,
            'parent': m.parent_id,
            'groups': list(m.groups.values_list('name', flat=True)),
            'children': []
        }
    menu_tree = []
    for m in menu_dict.values():
        if m['parent'] is not None and m['parent'] in menu_dict:
            menu_dict[m['parent']]['children'].append(m)
        else:
            menu_tree.append(m)
    return JsonResponse({'menus': menu_tree})

@csrf_exempt
def menu_save(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    data = json.loads(request.body)
    menu_id = data.get('id')
    name = data.get('name')
    path = data.get('path', '')
    parent = data.get('parent')
    groups = data.get('groups', [])
    if menu_id:
        menu = Menu.objects.get(id=menu_id)
        menu.name = name
        menu.path = path
        menu.parent_id = parent
        menu.save()
    else:
        menu = Menu.objects.create(name=name, path=path, parent_id=parent)
    menu.groups.clear()
    for g in groups:
        group = Group.objects.filter(name=g).first()
        if group:
            menu.groups.add(group)
    return JsonResponse({'msg': '保存成功'})

@csrf_exempt
def menu_delete(request, menu_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': '未登录'}, status=401)
    # 仅超级管理员组可操作
    if not request.user.groups.filter(name='超级管理员').exists():
        return JsonResponse({'error': '无权限'}, status=403)
    Menu.objects.filter(id=menu_id).delete()
    return JsonResponse({'msg': '删除成功'})

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({'csrftoken': request.META.get('CSRF_COOKIE', '')})
