DEBUG = True
# 复制为 conf.py 后分别生成两个随机值并填入；不要提交 conf.py。
# 每个值运行一次：python -c "import secrets; print(secrets.token_urlsafe(64))"
SECRET_KEY = ''
JWT_SIGNING_KEY = ''

DATABASES = {
    # 'default': {
    #     'ENGINE': 'django.db.backends.postgresql',
    #     'NAME': 'demo',
    #     'USER': 'postgres',
    #     'PASSWORD': '123456',
    #     'HOST': 'localhost',
    #     'PORT': '5432',
    # }
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3'
    }
}
