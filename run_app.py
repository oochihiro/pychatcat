import sys
import os
from pathlib import Path


def main() -> None:
    """
    应用程序入口。
    自动定位主程序所在目录，然后导入并执行 main 模块。
    """
    # 如果是 PyInstaller 打包的 EXE
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # PyInstaller 临时目录
        base_dir = Path(sys._MEIPASS)
        # 添加临时目录到路径
        if str(base_dir) not in sys.path:
            sys.path.insert(0, str(base_dir))
    else:
        # 普通 Python 运行
        base_dir = Path(__file__).resolve().parent
        if str(base_dir) not in sys.path:
            sys.path.insert(0, str(base_dir))
    
    # 确保当前目录在路径中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # 直接导入 main 模块
        import main
        # 调用 main 函数
        main.main()
    except ImportError as exc:
        error_msg = f"无法导入 main 模块: {exc}\n"
        error_msg += f"当前路径: {sys.path}\n"
        error_msg += f"工作目录: {os.getcwd()}\n"
        if getattr(sys, "frozen", False):
            error_msg += f"PyInstaller 临时目录: {sys._MEIPASS}\n"
        error_msg += "\n若在打包 EXE，请确保使用参数: --hidden-import main"
        raise ImportError(error_msg) from exc
    except Exception as exc:
        import traceback
        error_msg = f"启动应用时出错: {exc}\n"
        error_msg += traceback.format_exc()
        raise RuntimeError(error_msg) from exc


if __name__ == "__main__":
    main()


