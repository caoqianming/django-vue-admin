# 简介
基于RBAC模型的权限控制的基础开发平台,前后端分离,后端采用django+django-rest-framework,前端采用vue+ElementUI.

JWT认证,具有审计功能

内置模块有组织机构\用户\角色\岗位\数据字典\文件库

支持功能权限(控权到每个接口)和简单的数据权限（全部、本级及以下、同级及以下、本人等）

## 部分截图
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/user.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/dict.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/docs.png)

## 启动(以下是在windows下开发操作步骤)


### django后端
定位到server文件夹

新建log和media空文件夹

建立虚拟环境 `python -m venv venv`

激活虚拟环境 `.\venv\scripts\activate`

安装依赖包 `pip install -r requirements.txt`

修改数据库连接 `server\settings_dev.py` 或者直接使用sqlite数据库(超管账户密码均为admin)

同步数据库 `python manage.py makemigrations system`

同步数据库 `python manage.py migrate`

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

### 理念
功能权限的核心代码在server/apps/system/permission.py下重写了has_permission方法

数据权限因为跟具体业务有关,简单定义了几个规则，重写了has_object_permission方法

### 后续
继续完善定时任务配置(借助django-celery-beat包实现定时任务的热更新)

