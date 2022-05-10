'''
Created on 2022年5月9日

@author: Hsiao-Chien Tsai
'''
from qpt.smart_opt import set_default_pip_source
from qpt.executor import CreateExecutableModule
set_default_pip_source("https://pypi.python.org/simple")
if __name__ == '__main__':
    # 实例化Module - 关于路径的部分建议使用绝对路径                  
    module = CreateExecutableModule(work_dir="../tool/",                # [项目文件夹] 待打包的目录，并且该目录下需要有↓下方提到的py文件，python 路徑
                                    launcher_py_path="../tool/selfie_segmentation_tk.py", # [主程序文件]用户启动EXE文件后，QPT要执行的py文件
                                    save_path="/out",                 # [输出目录]打包后相关文件的输出目录
                                    requirements_file="../requirements.txt",           # [依赖]此处可填入依赖文件路径，也可设置为auto自动搜索依赖
                                    hidden_terminal=True)               # [终端窗口]设置为True后，运行时将不会展示黑色终端窗口             
                                                 
    # 开始打包
    module.make()