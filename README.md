# 简介
新增了base分支,base分支只包括后端,其在master分支的后端基础上进行了重新编写,拥有更完善的权限控制、工作流引擎、运维管理、websocket支持并提供多种常用功能集成到utils中.

后期功能变动将以base分支为主,master分支只做兼容性处理,具体可切换至base分支查看

## 下面为master分支介绍
基于RBAC模型权限控制的中小型应用的基础开发平台,前后端分离,后端采用django+django-rest-framework,前端采用vue+ElementUI,移动端采用uniapp+uView(可发布h5和小程序).

JWT认证,可使用simple_history实现审计功能,支持swagger

内置模块有组织机构\用户\角色\岗位\数据字典\文件库\定时任务\工作流(已上传大部分代码, 后端代码位于apps/wf)

使用工作流建议数据库用Postgresql, 下面的预览环境因为是用的sqlite因此有些json查询不支持, 使用方法可参考loonflow文档基本是一致, 主要是做了简化

支持功能权限(控权到每个接口)和简单的数据权限（全部、本级及以下、同级及以下、本人等）

欢迎提issue


## 部分截图
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/ticket.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/user.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/dict.png)
![image](https://github.com/caoqianming/django-vue-admin/blob/master/img/task.png)

## 预览地址
预览地址直接使用的runserver,账户admin,密码admin。请谨慎操作,勿修改密码
<http://49.232.29.236:2222/>

## 启动(以下是在windows下开发操作步骤)


### django后端
定位到server文件夹

建立虚拟环境 `python -m venv venv`

激活虚拟环境 `.\venv\scripts\activate`

安装依赖包 `pip install -r requirements.txt`

复制server文件夹下的conf_e.py为conf.py
根据需要修改里面的数据库连接及DEBUG参数

同步数据库 `python manage.py migrate`

可导入初始数据 `python manage.py loaddata db.json` 或直接使用sqlite数据库(超管账户密码均为admin,每隔一段时间数据库会重置)

创建超级管理员 `python manage.py createsuperuser`

运行服务 `python manage.py runserver 8000` 

### vue前端
定位到client文件夹

安装node.js

安装依赖包 `npm install --registry=https://registry.npmmirror.com`

运行服务 `npm run dev` 

### nginx
本地跑时修改nginx.conf，可显示资源文件

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

接口文档 localhost:8000/api/swagger/

后台地址 localhost:8000/django/admin/

## 部署
部署时注意修改conf.py

可以前后端分开部署, nginx代理。也可打包之后将前端dist替换server/dist, 然后执行collectstatic

使用gunicorn启动: 进入虚拟环境执行 gunicorn -w 5 -b 0.0.0.0:2251 server.wsgi

如果需要webscoket还需要配置daphne启动，可使用supervisor监控

Nginx配置可参考如下:
```
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
                proxy_pass_header  Authorization;
                proxy_pass_header  WWW-Authenticate;
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

### 工作流
工作流模块参考loonflow的实现可查看其文档(逻辑一样, 感谢loonflow)
目前大部分代码已上传, 可查看swagger

### 微信群
愿意交流的话
可以加QQ群 235665873
可以加微信群
![image](http://49.232.29.236:2222/media/wechat_group.jpg)
