# 简介
基于RBAC模型的权限控制的基础开发平台,前后端分离,后端采用django+django-rest-framework,前端采用vue+ElementUI.

内置模块有组织机构\用户\角色\岗位,支持功能权限(控权到每个接口)和简单的数据权限,采用JWT认证.

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

## vue前端
定位到client文件夹

安装node.js

安装依赖包 `npm install --registry=https://registry.npm.taobao.org`

运行服务 `npm run dev` 

## nginx
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

## 运行
打开localhost:8012即可访问

接口文档 localhost:8000/docs

后台地址 localhost:8000/admin

