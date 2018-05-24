# phototransform-back
北京大学2018软件工程图像风格转换后端

# 更新日志

### 更新了项目目录

app，下分auth用于做后端回应，transfer用于存放CNN模型(-pytorch为自己实现的model，-tf为tensorflow，为用来train但非自己实现版本），models用于存放数据库定义

venv，为项目虚拟机，建议解释器使用虚拟机中的环境

tests，为项目单元测试文件

config.py 中设置了一些环境

manage.py 用于启动服务器

详细参考自 https://blog.csdn.net/yannanxiu/article/details/52192849

### UPDATE 2018.05.24 By Qiuls

app/model_deplot/ 下放了模型部署的sample，模型和code已经放在服务器上，可参考README运行。
