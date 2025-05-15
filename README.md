# xMes 生产管理系统

一个全面的制造执行系统(MES)，用于生产管理，后端基于Django构建，前端使用Vue 3。

## 系统架构

### 后端 (Django)

- 使用Django REST framework构建API端点
- MySQL数据库
- 基于SimpleJWT的JWT认证
- API结构遵循RESTful原则
- 为不同业务领域设计的模块化应用

### 前端 (Vue 3 + TypeScript)

- 现代Vue 3组合式API与TypeScript
- Pinia状态管理
- Vue Router导航
- Element Plus UI组件
- Axios进行API通信

## 主要功能

1. **产品和物料管理**
   - 产品类别和参数管理
   - 带单位支持的物料管理
   - BOM(物料清单)管理
   - 图纸和工艺PDF附件

2. **生产管理**
   - 创建和管理生产订单
   - 跟踪生产过程中的订单状态
   - 管理物料和资源
   - 工序和工作流配置

3. **销售管理**
   - 客户订单管理
   - 销售订单跟踪和履行
   - 订单到生产的工作流

4. **基础数据管理**
   - 带单位支持的产品目录管理
   - 产品参数值配置
   - 客户和供应商数据库
   - 物料库存管理

5. **用户管理**
   - 基于角色的访问控制
   - 用户认证和授权
   - 用户配置文件和偏好设置

## PDF文件上传与命名方案

### 方案说明

- **文件上传**：后端Django的FileField仅设置upload_to参数，不做任何自定义存储、命名、覆盖或清理逻辑。
- **文件命名**：上传时文件名完全由用户决定，Django自动处理同名文件（加随机后缀），前后端均不做任何命名规范或覆盖处理。
- **同名文件**：允许同名文件上传，Django会自动在文件名后加唯一后缀，避免覆盖和冲突。
- **文件删除**：不主动清理旧文件，文件的生命周期由Django和操作系统管理。
- **前端处理**：前端根据后端返回的文件路径/URL进行预览和下载，不依赖文件名规范。
- **历史数据**：本轮迁移后，所有历史数据和文件命名规则作废，数据库和文件存储均为全新结构。

### 注意事项

- **文件锁定问题**：采用Django默认存储和命名，避免了因手动覆盖/删除导致的Windows文件被占用问题。
- **命名冲突**：如需展示原始文件名，可在数据库中单独存储original_name字段（可选）。
- **数据库迁移**：如需重建数据库，需先删除所有migrations目录和数据库文件，再重新makemigrations和migrate。
- **单元测试**：建议为文件上传、下载、预览等功能补充单元测试，确保各类文件名、大小、格式均能正常处理。
- **异常处理**：上传接口建议增加异常捕获和友好提示，防止因文件过大、格式不符等导致系统报错。

### 示例代码

**models.py**
```python
from django.db import models

class Attachment(models.Model):
    file = models.FileField(upload_to='attachments/')
    # 如需保存原始文件名，可加如下字段
    # original_name = models.CharField(max_length=255, blank=True, null=True)
```

**views.py**
```python
def upload_file(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        instance = Attachment.objects.create(file=file)
        # instance.original_name = file.name
        # instance.save()
        return JsonResponse({'url': instance.file.url, 'name': file.name})
    return JsonResponse({'error': 'No file uploaded'}, status=400)
```

## 代码组织

### 前端结构

```
frontend/
├── public/
├── src/
│   ├── api/                # API服务
│   │   └── index.ts        # Axios实例和API端点
│   ├── assets/             # 静态资源(图片、样式)
│   ├── components/         # 可复用Vue组件
│   │   ├── common/         # 通用UI组件
│   │   ├── layout/         # 布局组件
│   │   └── production/     # 生产特定组件
│   ├── router/             # Vue Router配置
│   ├── stores/             # Pinia状态管理
│   │   ├── category.ts     # 产品类别状态管理
│   │   ├── product.ts      # 产品管理状态管理
│   │   ├── param.ts        # 参数管理状态管理
│   │   └── user.ts         # 用户管理状态管理
│   ├── types/              # TypeScript类型定义
│   ├── utils/              # 工具函数
│   ├── views/              # 页面组件
│   │   ├── basedata/       # 基础数据管理视图
│   │   ├── productionmgmt/ # 生产管理视图
│   │   └── salesmgmt/      # 销售管理视图
│   ├── App.vue             # 根组件
│   └── main.ts             # 应用入口点
└── package.json            # 依赖和脚本
```

### 后端结构

```
backend/
├── basedata/               # 基础数据应用(产品、客户等)
│   ├── models.py           # 数据模型
│   ├── serializers.py      # DRF序列化器
│   ├── views.py            # API视图和端点
│   └── admin.py            # 管理面板配置
├── productionmgmt/         # 生产管理应用
├── salesmgmt/              # 销售管理应用
├── usermgmt/               # 用户管理应用
└── manage.py               # Django管理脚本
```

## 最近功能增加

### 单位功能实现 (2025年5月)

1. **后端变更**
   - 添加了带代码、名称和描述字段的Unit模型
   - 向Product和Material模型添加了单位字段(外键)
   - 更新了ProductSerializer和MaterialSerializer以包含单位数据
   - 创建了UnitSerializer和UnitViewSet，支持导入功能
   - 在管理面板中注册了Unit并添加了迁移

2. **前端变更**
   - 更新了Product和Material接口以包含单位字段
   - 在产品和物料表单中添加了单位选择
   - 在产品和物料数据表中添加了单位列
   - 更新了导入/导出功能以处理单位
   - 添加了单位管理界面

3. **导入增强**
   - 增强了产品导入以包括单位指定
   - 添加了带模板生成的单位导入功能
   - 改进了导入中的参数值处理

## 开发设置

### 前提条件

- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 后端设置

1. 克隆存储库
2. 设置后端:
   ```
   cd backend
   python -m venv venv
   source venv/bin/activate  # 在Windows上: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

### 前端设置

1. 设置前端:
   ```
   cd frontend
   npm install
   npm run dev
   ```

## 开发工具

### Cursor编辑器配置

本项目包含一个`.vscode/settings.json`文件，带有Cursor编辑器配置，提供优化的开发体验:

- TypeScript和Vue.js特定的格式化规则
- Python代码检查和格式化设置
- 一致的代码风格强制执行
- 前端和后端开发的生产力增强

主要设置包括:
- 缩进大小: 前端使用2个空格，Python使用4个空格
- 最大行长度: 120个字符
- 保存时自动格式化
- JavaScript/TypeScript/Vue的ESLint集成
- Python的Pylint集成

要使用这些设置，请确保安装以下扩展:
- Vue Language Features (Volar)
- ESLint
- Python extension for VS Code

## 贡献指南

- 所有新的前端代码都使用TypeScript
- 遵循Vue 3组合式API模式
- 遵循Python代码的PEP 8风格指南
- 编写有意义的提交消息
- 为新功能创建特性分支
- 提交拉取请求进行审核

## 许可证

版权所有 © 2025 xMes团队

## 代码重构

### 2024-06-XX 代码重构

完成了以下重构工作：

1. **PDF页面标题显示问题修复**
   - 为图纸PDF和工艺PDF实现了专用的PDF查看器组件
   - 解决了查看PDF时浏览器标题乱码问题

2. **Store模块化重构**
   - 使用Pinia创建了模块化的数据状态管理
   - `useBomStore`: BOM及BOM明细管理
   - `useMaterialStore`: 物料管理
   - `useUnitStore`: 单位管理
   - `useCategoryStore`: 产品类管理

3. **类型系统完善**
   - 在`types/index.ts`中集中管理所有类型定义
   - 使用TypeScript接口统一定义数据结构
   - 为所有组件和Store提供类型安全

4. **API调用规范化**
   - 统一API调用方式和错误处理
   - 规范化分页参数和响应处理
   - 添加统一的错误处理机制

5. **组件样式统一**
   - 统一表格布局和操作按钮样式
   - 规范化表单样式和布局
   - 提高UI一致性和用户体验

### 2024-06-10 代码重构

完成了以下重构工作：

1. **组件重构**
   - 将表单逻辑从视图组件中抽离，创建专用的表单对话框组件
   - 创建了`ProcessFormDialog.vue`和`MaterialFormDialog.vue`组件
   - 增强了组件的复用性和可测试性

2. **组合式API优化**
   - 创建了`useProcessForm`和`useMaterialForm`组合式函数
   - 将表单逻辑、验证规则和状态管理抽象到可复用的组合式函数中
   - 遵循Vue 3 Composition API的最佳实践

3. **Store功能增强**
   - 优化了`processStore`和`materialStore`的错误处理
   - 统一了API响应处理逻辑
   - 移除了冗余代码，提高了代码可维护性

4. **类型系统整合**
   - 将所有业务实体类型定义集中到`types/common.ts`
   - 添加了`Process`和`ProcessForm`等业务实体接口
   - 提高了代码的类型安全性和开发体验

5. **错误处理标准化**
   - 实现了统一的API错误处理机制
   - 在Store中添加了`handleApiError`辅助方法
   - 简化了组件中的错误处理逻辑

### 2024-06-15 工艺流程代码管理重构

完成了以下重构工作：

1. **工艺流程代码组件重构**
   - 将工艺流程代码表单逻辑抽离，创建`ProcessCodeFormDialog.vue`组件
   - 重构`ProcessCodeList.vue`，分离业务逻辑与UI表现
   - 提高了组件的复用性和代码可维护性

2. **工艺流程代码状态管理**
   - 创建`processCodeStore.ts` Pinia store
   - 集中管理工艺流程代码的数据获取、创建、更新和删除操作
   - 优化API响应处理和错误处理逻辑

3. **组合式API扩展**
   - 实现`useProcessCodeForm`组合式函数
   - 将工艺流程代码表单状态、校验规则和自动生成逻辑抽象化
   - 优化代码复用，减少重复逻辑

4. **类型定义增强**
   - 添加`ProcessCode`和`ProcessCodeForm`等接口到类型系统
   - 增强了TypeScript的类型安全和IDE提示
   - 统一了数据结构定义，提高了代码一致性

5. **错误处理和PDF预览优化**
   - 添加统一的API错误处理策略
   - 优化了PDF文件上传和预览功能
   - 改进了表单验证和用户体验

### 2024-06-20 产品工艺关联代码重构

完成了以下重构工作：

1. **产品工艺关联组件重构**
   - 创建了`ProductProcessCodeFormDialog.vue`组件，用于产品与工艺流程代码的关联管理
   - 重构`ProductProcessCodeList.vue`，将视图逻辑与数据处理逻辑分离
   - 优化了组件结构，提高了代码可读性和可维护性

2. **产品工艺关联状态管理**
   - 新增`productProcessCodeStore.ts` Pinia store
   - 集中管理产品工艺关联的数据获取、创建、更新和删除操作
   - 添加设置默认工艺流程的功能支持
   - 统一错误处理和状态管理机制

3. **组合式API实现**
   - 创建`useProductProcessCodeForm`组合式函数
   - 将表单状态、验证规则和操作逻辑抽象为可复用的组合函数
   - 提高了代码的模块化程度和重用性

4. **类型系统扩展**
   - 在`types/common.ts`中添加`ProductProcessCode`和`ProductProcessCodeForm`接口
   - 为产品工艺关联功能提供完整的类型支持
   - 增强代码编写时的类型检查和IDE智能提示

5. **API错误处理一致性**
   - 在store中实现统一的API错误处理方法
   - 简化了组件中的错误处理代码
   - 提供友好的用户错误提示，增强用户体验

### 2024-06-25 BOM明细管理代码重构

完成了以下重构工作：

1. **BOM明细组件重构**
   - 创建了独立的`BomDetailFormDialog.vue`组件，用于BOM明细的添加和编辑
   - 重构`BomDetailList.vue`，将表单操作和数据处理逻辑分离
   - 减少了组件间的耦合，提高了代码可维护性

2. **BOM明细状态管理**
   - 创建专用的`bomDetailStore.ts` Pinia store
   - 集中管理BOM明细的数据获取、创建、更新、删除和导入操作
   - 优化了BOM筛选和分页功能的处理逻辑
   - 统一了数据加载和操作状态的管理

3. **组合式API实现**
   - 创建`useBomDetailForm`组合式函数
   - 将BOM明细表单逻辑抽象为可重用的组合函数
   - 标准化了表单状态管理和验证规则
   - 增强了开发体验和代码一致性

4. **类型定义完善**
   - 添加了`Bom`、`BomForm`、`BomDetail`和`BomDetailForm`接口到类型系统
   - 为BOM相关功能提供了完整的类型定义
   - 提高了代码可读性和类型安全性

5. **错误处理机制统一**
   - 实现了一致的API错误处理方法
   - 简化了错误信息展示逻辑
   - 优化了用户反馈体验

### 2024-06-30 BOM管理代码重构

完成了以下重构工作：

1. **BOM管理组件重构**
   - 创建了独立的`BomFormDialog.vue`组件，用于BOM的创建和编辑
   - 重构`BomList.vue`组件，将表单逻辑与视图展示分离
   - 优化了组件结构和代码可读性
   - 提高了代码复用性和可维护性

2. **BOM状态管理优化**
   - 创建专用的`bomStore.ts` Pinia store
   - 集中管理BOM的数据获取、创建、更新和删除操作
   - 优化了搜索和分页功能的实现
   - 统一了状态管理和数据加载机制

3. **组合式API应用**
   - 实现`useBomForm`组合式函数
   - 分离BOM表单状态和验证规则逻辑
   - 添加自动根据产品和版本生成BOM名称的功能
   - 提高了代码结构清晰度和可复用性

4. **类型系统使用强化**
   - 完善了BOM和BomForm接口的类型定义
   - 确保了类型安全性和一致性
   - 提高了开发体验和代码质量

5. **错误处理一致性**
   - 实现了与其他模块一致的错误处理机制
   - 统一用户友好的错误提示
   - 增强了用户体验和反馈机制

### 2024-07-05 物料管理代码重构

完成了以下重构工作：

1. **物料管理组件重构**
   - 更新了`MaterialFormDialog.vue`组件，优化了物料的创建和编辑功能
   - 重构`MaterialList.vue`视图组件，将表单逻辑与视图展示分离
   - 简化了组件结构，提高了代码可读性和可维护性
   - 统一了物料上传和PDF预览的处理逻辑

2. **物料状态管理优化**
   - 重构`materialStore.ts` Pinia store
   - 统一了物料的数据获取、创建、更新、删除和导入操作
   - 优化了搜索和分页功能的实现
   - 改进了API错误处理和数据加载机制
   - 将表单数据处理逻辑移至store内部

3. **组合式API应用**
   - 优化`useMaterialForm`组合式函数
   - 分离物料表单状态和验证规则逻辑
   - 完善物料参数值的管理和自动填充功能
   - 提高了代码的模块化和复用性

4. **类型系统完善**
   - 更新了`Material`和`MaterialForm`接口的类型定义
   - 添加了对文件上传的TypeScript类型支持
   - 增强了类型安全性和代码提示

5. **统一的模式和风格**
   - 使物料管理模块的代码结构与其他重构后的模块保持一致
   - 统一了错误处理和用户反馈机制
   - 提高了整体代码库的一致性和可维护性
   - 改进了组件间的数据流和状态共享模式

### 2024-07-10 产品类管理代码重构与文件上传优化

完成了以下重构工作：

1. **产品类管理组件重构**
   - 创建了独立的`CategoryFormDialog.vue`组件，用于产品类的创建和编辑
   - 重构`ProductCategoryList.vue`组件，将表单逻辑与视图展示分离
   - 优化了组件结构和代码可读性
   - 标准化了状态管理模式和组件接口

2. **产品类状态管理优化**
   - 创建专用的`categoryStore.ts` Pinia store
   - 集中管理产品类的数据获取、创建、更新和删除操作
   - 优化了搜索和分页功能的实现
   - 统一了状态管理和数据加载机制

3. **组合式API应用**
   - 实现`useCategoryForm`组合式函数
   - 分离产品类表单状态和验证规则逻辑
   - 提高了代码结构清晰度和可复用性

4. **PDF文件预览优化**
   - 创建了`ImprovedPdfPreview.vue`组件，解决文件上传预览问题
   - 修复了切换文件时预览不更新的问题
   - 使用fileKey属性实现强制渲染预览组件
   - 增强了文件上传体验和预览效果

5. **类型系统使用强化**
   - 添加了`ProductCategory`和`ProductCategoryForm`接口的类型定义
   - 确保了类型安全性和一致性
   - 提高了开发体验和代码质量

6. **统一模式和标准**
   - 实现了与其他模块一致的错误处理机制
   - 统一了操作反馈和用户提示
   - 促进了整个代码库的一致性
   - 提高了代码的可维护性和可读性
