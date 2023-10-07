from configparser import ConfigParser
import os
from django.conf import settings


class MyConfig:

    def __init__(self, config_file, encode="utf-8"):
        if os.path.exists(config_file):
            self.__cfg_file = config_file
        else:
            # 此处做其他异常处理或创建配置文件操作
            raise OSError("配置文件不存在!")
        self.__config = ConfigParser()
        self.__config.read(config_file, encoding=encode)

    def get_sections(self):
        """获取配置文件的所有section
        """
        return self.__config.sections()

    def get_options(self, section_name):
        """获取指定section的所有option
        """
        if self.__config.has_section(section_name):
            return self.__config.options(section_name)
        else:
            raise ValueError(section_name)

    def get_option_value(self, section_name, option_name):
        """获取指定section下option的value值
        """
        if self.__config.has_option(section_name, option_name):
            return self.__config.get(section_name, option_name)

    def get_all_items(self, section_name, to_dict: bool=True):
        """获取指定section下的option的键值对
        """
        if self.__config.has_section(section_name):
            if to_dict:
                return dict(self.__config.items(section_name))
            return self.__config.items(section_name)

    def print_all_items(self):
        """打印配置文件所有的值
        """
        for section in self.get_sections():
            print("[" + section + "]")
            for K, V in self.__config.items(section):
                print(K + "=" + V)

    def add_new_section(self, new_section):
        """增加section
        """
        if not self.__config.has_section(new_section):
            self.__config.add_section(new_section)
            self.__update_cfg_file()

    def add_option(self, section_name, option_key, option_value):
        """增加指定section下option
        """
        if self.__config.has_section(section_name):
            self.__config.set(section_name, option_key, option_value)
            self.__update_cfg_file()

    def del_section(self, section_name):
        """删除指定section
        """
        if self.__config.has_section(section_name):
            self.__config.remove_section(section_name)
            self.__update_cfg_file()

    def del_option(self, section_name, option_name):
        """删除指定section下的option
        """
        if self.__config.has_option(section_name, option_name):
            self.__config.remove_option(section_name, option_name)
            self.__update_cfg_file()

    def update_section(self, section_name, option_dict: dict):
        """批量更新指定section下的option的值
        """
        if self.__config.has_section(section_name):
            for k, v in option_dict:
                self.__config.set(section_name, k, v)
            self.__update_cfg_file()
        
    def update_option_value(self, section_name, option_key, option_value):
        """更新指定section下的option的值
        """
        if self.__config.has_option(section_name, option_key):
            self.add_option(section_name, option_key, option_value)

        # 私有方法:操作配置文件的增删改时，更新配置文件的数据
    def __update_cfg_file(self):
        with open(self.__cfg_file, "w") as f:
            self.__config.write(f)


myConfig = MyConfig(os.path.join(settings.BASE_DIR, 'server/conf.ini'))
