# 简介
基于RBAC模型权限控制的中小型应用的基础开发平台,前后端分离,后端采用django+django-rest-framework,前端采用vue+ElementUI,移动端采用uniapp+uView(可发布h5和小程序).

JWT认证,可使用simple_history实现审计功能,支持swagger

内置模块有组织机构\用户\角色\岗位\数据字典\文件库\定时任务\工作流(已上传大部分代码, 后端代码位于apps/wf)

使用工作流建议数据库用Postgresql, 下面的预览环境因为是用的sqlite因此有些json查询不支持, 使用方法可参考loonflow文档基本是一致, 主要是做了简化

支持功能权限(控权到每个接口)和简单的数据权限（全部、本级及以下、同级及以下、本人等）

欢迎提issue


## 部分截图
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/user.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/dict.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/task.png)

## 预览地址
预览地址直接使用的runserver,账户admin,密码admin。请谨慎操作,勿修改密码
<http://47.95.0.242:1111/>

## 启动(以下是在windows下开发操作步骤)


### django后端
定位到server文件夹

建立虚拟环境 `python -m venv venv`

激活虚拟环境 `.\venv\scripts\activate`

安装依赖包 `pip install -r requirements.txt`

修改数据库连接 `server\settings_dev.py` 

同步数据库 `python manage.py migrate`

可导入初始数据 `python manage.py loaddata db.json` 或直接使用sqlite数据库(超管账户密码均为admin,每隔一段时间数据库会重置)

创建超级管理员 `python manage.py createsuperuser`

运行服务 `python manage.py runserver 8000` 

### vue前端
定位到client文件夹

安装node.js

安装依赖包 `npm install --registry=https://registry.npm.taobao.org`

运行服务 `npm run dev` 

### nginx
修改nginx.conf

```
listen 8012
location /media {
    proxy_pass http://localhost:8000;
}
location / {
    proxy_pass http://localhost:9528;
}
```

运行nginx.exe

### 运行
打开localhost:8012即可访问

接口文档 localhost:8000/docs

后台地址 localhost:8000/admin

## 部署
部署时使用的是settings_pro.py。注意修改

可以前后端分开部署, nginx代理。也可打包之后放在server/vuedist文件夹, 然后执行collectstatic

### docker-compose 方式运行

前端 `./client` 和后端 `./server` 目录下都有Dockerfile，如果需要单独构建镜像，可以自行构建。

这里主要说docker-compose启动这种方式。

按照注释修改docker-compose.yml文件。里面主要有两个服务，一个是`backend`后端,一个是`frontend`前端。

默认是用开发模式跑的后端和前端。如果需要单机部署，又想用docker-compose的话，改为生产模式性能会好些。


启动
```
cd <path-to-your-project>
docker-compose up -d
```

启动成功后，访问端口同前面的，接口8000端口，前端8012端口，如需改动，自己改docker-compose.yml

如果要执行里面的命令
docker-compose exec <服务名> <命令>

举个栗子：

如果我要执行后端生成数据变更命令。`python manage.py makemigrations`

则用如下语句

```
docker-compose exec backend python manage.py makemigrations
```

### 理念
首先得会使用django-rest-framework, 理解vue-element-admin前端方案

本项目采用前端路由，后端根据用户角色读取用户权限代码返回给前端，由前端进行加载(核心代码是路由表中的perms属性以及checkpermission方法)

后端功能权限的核心代码在server/apps/system/permission.py下重写了has_permission方法, 在APIView和ViewSet中定义perms权限代码

数据权限因为跟具体业务有关,简单定义了几个规则,重写了has_object_permission方法;根据需要使用即可

由于实际情况比较复杂，这里建议根据不同情况自己写drf的permission_class

### 关于定时任务
使用celery以及django_celery_beat包实现

需要安装redis并在默认端口启动, 并启动worker以及beat

进入虚拟环境并启动worker: `celery -A server worker -l info -P eventlet`, linux系统不用加-P eventlet

进入虚拟环境并启动beat: `celery -A server beat -l info`

### 后续
工作流模块参考loonflow的实现可查看其文档(逻辑一样, 感谢loonflow)
目前大部分代码已上传, 可查看swagger

### 下一步
功能权限和数据权限的处理有大的优化空间, 可实现更加合理的权限划分, 但对目前代码改动较大，在考虑中

