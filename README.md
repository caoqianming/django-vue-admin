# django-vue-admin

基于 RBAC 权限模型的前后端分离后台管理平台，适合作为中小型业务系统的基础开发骨架。

后端使用 Django + Django REST Framework，前端使用 Vue 2 + Element UI，移动端目录中提供了基于 uni-app + uView 的实现。

## 项目特性

- 前后端分离：后端提供 REST API，前端按权限动态加载路由和菜单
- RBAC 权限控制：支持接口级功能权限控制
- 数据权限：内置全部、本级及以下、同级及以下、本人等基础规则
- JWT 认证：默认使用 `djangorestframework-simplejwt`
- 审计能力：可结合 `django-simple-history` 记录变更历史
- 定时任务：集成 Celery + `django-celery-beat`
- 接口文档：内置 Swagger 页面
- 工作流模块：参考 loonflow 思路做了简化实现

## 内置模块

- 组织机构
- 用户管理
- 角色管理
- 岗位管理
- 权限管理
- 数据字典
- 文件库
- 定时任务
- 工作流
- 系统监控

## 技术栈

### 后端

- Django 4.2.27
- Django REST Framework 3.14.0
- Simple JWT 5.5.1
- django-celery-beat 2.5.0
- django-simple-history 3.4.0
- drf-yasg 1.21.7
- Redis

### 前端

- Vue 2.6
- Element UI 2.15
- Vue Router 3
- Vuex 3
- Axios 1.6

## 目录结构

```text
.
├─ client/       Web 管理端
├─ client_mp/    移动端（uni-app + uView）
├─ img/          README 截图资源
├─ server/       Django 后端
├─ docker-compose.yml
└─ README.md
```

## 快速开始

### 运行环境

- Python 3.10+（建议）
- Node.js 16 或更高版本
- Redis 6+（使用定时任务时需要）
- PostgreSQL（如需完整使用工作流模块，建议使用）

### 1. 启动后端

进入目录：`server`

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

项目使用 `server/server/conf.py` 读取数据库和调试配置。
如果是首次初始化，可参考同目录下的 `conf_e.py` 创建或调整配置。

执行数据库迁移：

```bash
python manage.py migrate
```

可选：导入初始化数据

```bash
python manage.py loaddata db.json
```

说明：仓库当前已包含 `server/db.sqlite3`，本地体验时也可以直接使用。

创建超级管理员：

```bash
python manage.py createsuperuser
```

启动开发服务：

```bash
python manage.py runserver 8000
```

### 2. 启动前端

进入目录：`client`

```bash
npm install --registry=https://registry.npmmirror.com
npm run dev
```

默认开发环境下，前端接口地址为：`http://localhost:8000/api`

### 3. 访问入口

前端开发服务默认端口通常为 `9528`。如果通过 Nginx 代理，可统一从 `8012` 访问。

- 前端页面：`http://localhost:8012/` 或 `http://localhost:9528/`
- Swagger 文档：`http://localhost:8000/api/swagger/`
- Django Admin：`http://localhost:8000/django/admin/`

## 本地联调 Nginx 示例

如果你希望本地通过一个端口同时访问前端页面和后端媒体文件，可以参考以下配置：

```nginx
listen 8012;

location /media {
    proxy_pass http://localhost:8000;
}

location / {
    proxy_pass http://localhost:9528;
}
```

## Docker Compose 运行

仓库根目录提供了 `docker-compose.yml`，默认包含以下服务：

- `backend`：Django 后端
- `frontend`：Vue 前端
- `redis`：Redis

启动：

```bash
docker-compose up -d
```

启动后默认访问：

- 后端：`http://localhost:8000/`
- 前端：`http://localhost:8012/`

在容器内执行命令示例：

```bash
docker-compose exec backend python manage.py makemigrations
```

说明：当前 `docker-compose.yml` 默认更偏向开发模式，若用于单机生产部署，建议切换为生产镜像和生产配置。

## 生产部署说明

部署时请重点检查以下配置：

- `server/server/conf.py` 中的数据库连接、`DEBUG`、主机配置
- 静态资源和媒体文件目录
- Nginx 反向代理配置
- Redis、Celery、数据库的网络连通性

前后端可以分开部署，也可以先构建前端，再将前端 `dist` 内容替换到后端 `server/dist` 中统一托管，然后执行 `collectstatic`。

Gunicorn 启动示例：

```bash
gunicorn -w 5 -b 0.0.0.0:2251 server.wsgi
```

如需 WebSocket，可额外使用 Daphne 并配合 Supervisor 管理进程。

Nginx 可参考：

```nginx
server {
    listen 2250;
    client_max_body_size 1024m;

    location /media/ {
        alias /home/lighthouse/xx/media/;
        limit_rate 800k;
    }

    location / {
        alias /home/lighthouse/xx/dist/;
        index index.html;
    }

    location ~ ^/(api|django)/ {
        set $CSRFTOKEN "";
        if ($http_cookie ~* "CSRFTOKEN=(.+?)(?=;|$)") {
            set $CSRFTOKEN "$1";
        }
        proxy_set_header X-CSRFToken $CSRFTOKEN;
        proxy_pass http://localhost:2251;
        proxy_pass_header Authorization;
        proxy_pass_header WWW-Authenticate;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /ws/ {
        proxy_pass http://localhost:2252;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
    }
}
```

## 权限设计说明

本项目采用“前端路由 + 后端权限码”的方式控制访问：

- 前端在路由配置中通过 `meta.perm` 等字段控制页面显示与按钮权限
- 后端在接口层通过 `RbacPermission` 校验用户权限码
- 数据权限在 `has_object_permission` 中做了基础规则扩展，可按业务继续自定义

核心代码位置：

- 后端权限：`server/apps/system/permission.py`
- 前端权限控制：`client/src/permission.js`
- 前端路由与权限生成：`client/src/store/modules/permission.js`

## 定时任务说明

定时任务使用 Celery 和 `django-celery-beat` 实现。

需要先启动 Redis，然后分别启动 worker 和 beat：

```bash
celery -A server worker -l info -P eventlet
celery -A server beat -l info
```

说明：Linux 环境下通常不需要 `-P eventlet`。

## 工作流说明

工作流模块参考 loonflow 的实现思路，并做了简化。后端主要代码位于 `server/apps/wf`。

建议：

- 如果需要稳定使用复杂工作流能力，优先使用 PostgreSQL
- 预览或轻量体验可直接使用 SQLite，但部分 JSON 查询能力会受限

## 预览地址

演示环境：<http://49.232.14.174:7777/>

默认演示账户：

- 用户名：`admin`
- 密码：`admin`

说明：演示环境直接使用 `runserver`，请谨慎操作，不要修改默认密码。

## 部分截图

![工单页面](https://github.com/caoqianming/django-vue-admin/blob/master/img/ticket.png)
![用户管理](https://github.com/caoqianming/django-vue-admin/blob/master/img/user.png)
![数据字典](https://github.com/caoqianming/django-vue-admin/blob/master/img/dict.png)
![定时任务](https://github.com/caoqianming/django-vue-admin/blob/master/img/task.png)

## 相关项目

如果你需要更复杂、更完整的能力，可以查看：

- [xt_server](https://github.com/caoqianming/xt_server)

该仓库在这一套后端基础上做了进一步重写，包含更完善的权限控制、工作流引擎、运维管理、WebSocket 支持以及更多通用能力。

## 交流

- QQ 群：`235665873`
- 微信群：

![微信群](http://49.232.14.174:7777/media/wechat_group.jpg)
