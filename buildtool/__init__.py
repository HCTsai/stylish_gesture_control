
from qpt.executor import CreateExecutableModule
from qpt.smart_opt import set_default_pip_source
#set_default_pip_source("https://mirrors.sustech.edu.cn/pypi/simple")
set_default_pip_source("https://pypi.org/simple")

if __name__ == '__main__':
    # 实例化Module - 关于路径的部分建议使用绝对路径
    module = CreateExecutableModule(work_dir="../",                # [项目文件夹]待打包的目录，并且该目录下需要有↓下方提到的py文件
                                    launcher_py_path="../gesture_powerpoint_control_tk.py", # [主程序文件]用户启动EXE文件后，QPT要执行的py文件
                                    save_path="./out",
                                    requirements_file="../requirements_full.txt",
                                    hidden_terminal=True )                          # [输出目录]打包后相关文件的输出目录
                                  # requirements_file="auto"                    # [依赖]此处可填入依赖文件路径，也可设置为auto自动搜索依赖
                                  # hidden_terminal=False                       # [终端窗口]设置为True后，运行时将不会展示黑色终端窗口    
    # 开始打包
    module.make()