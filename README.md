# 羊了个羊

## 简介

羊了个羊游戏搭建及人工智能算法实现。

## 安装
1. 本项目使用python 3.11.4,不确定在此版本以下能否正常运行。
2. 本项目依赖 PyQt6,pytorch,NumPy 库。可以使用以下命令来安装 PyQt6：
    ```bash
    pip install PyQt6
    pip install torch torchvision torchaudio
    pip install numpy
    ```
   训练过程依赖DI-engine,gym，如果需要自己训练，可以使用以下命令安装：
    ```bash
    pip install DI-engine
    pip install gym
    ```

3. 下载全部源文件。
## 使用
1. 运行`main.py`。
- 在文本编辑器/IDE中运行。在文本编辑器/IDE中打开整个项目，进入`main.py`，点击运行。
- 命令行运行。
     ```bash
     cd 项目文件夹
     python main.py
     ```
1. 自定义设置。
   - 设定暂存区容量（推荐7），不超过10.
   - 设定层数。
   - 设定每层牌数量。
   - 选择模式。(效果：赋分>PPO>DQN)
   - 点击确定。
2. 开始游戏！
   - 手动模式：点击卡牌进行选择。
   - 其他模式：不需要操作。
3. 游戏结束。按退出键退出。