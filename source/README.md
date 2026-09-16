# 源码说明

本目录是「甲韵康跃 · 监测与预警系统」的桌面程序源码。给对方安装请用仓库根目录的 `甲韵康跃监测系统安装包.exe`，不要发 `dist/` 或解压后的 exe。

需要 **Python 3.10+**（`main.py` 使用了 `list[dict]` 类型标注）和 Windows 10/11 自带的 WebView2。

## 快速开始

```bat
启动监测系统.bat
```

或：

```bat
python -m pip install -r requirements.txt
python main.py
```

调试：

```bat
python main.py --debug
```

## 目录

```text
source/
  main.py                      窗口 + 串口桥
  requirements.txt             pywebview / pyserial / pyinstaller
  app.ico                      窗口与安装包图标
  启动监测系统.bat
  打包成EXE.bat                -> dist\甲韵康跃监测系统\
  生成安装包.bat               需 Inno Setup 6
  甲韵康跃监测系统.spec
  app/index.html               监测界面与算法
  app/chart.umd.min.js
  installer/甲韵康跃监测系统.iss
  installer/ChineseSimplified.isl
```

## 运行时结构

```text
设备 / 手动 / 模拟
        │
        ▼
  main.py 串口线程（仅桌面）
        │  poll 每 80ms
        ▼
  app/index.html
    receiveData()
      ├─ learnBaseline()     20 点去极值均值
      ├─ 分级预警 + 声音
      ├─ 波形 / 斜率图
      └─ 喉返神经热力图
```

- 桌面：`pywebview` 打开本地 `index.html`，JS 通过 `window.pywebview.api` 调 Python。
- 浏览器：可手动输入；若支持 Web Serial 也可连设备。没有网页串口时会提示改用桌面软件。

## `index.html` 里的关键常量

| 名称 | 值 | 含义 |
|------|----|------|
| `BASELINE_LEARN_COUNT` | 20 | 学习点数 |
| 学习有效范围 | 10～300 μV | 超出不计点 |
| 去极值 | 排序后去掉高低各 2 个再平均 | 基线 |
| `BASELINE_MULTIPLIER_WARN` | 4 | 警戒 = 基线×4 |
| `BASELINE_MULTIPLIER_DANGER` | 6 | 危险 = 基线×6 |
| 警戒夹紧 | 150～650 | |
| 危险夹紧 | 250～800 | |
| 未学成默认 | 550 / 650 | |
| `SLOPE_THRESHOLD` | 8 | 趋势预判 |
| 斜率公式 | 最近 4 点差 / 3 | |
| `MAX_POINTS` | 200 | 波形长度 |
| 模拟间隔 | 500 ms | |
| 显示夹紧 | 100～800 | |
| 红色警报 | 900 Hz / 300 ms | |
| 黄色警报 | 600 Hz / 1000 ms | |

预设序列会循环播放一条先升后降的刺激曲线（约 320→730→300 μV），每 0.5 秒一点，并叠加少量噪声。

## 打包注意

`甲韵康跃监测系统.spec` **不要**把 `ucrtbase.dll` 和 `api-ms-win-*` 打进安装包。打进去后，部分电脑覆盖系统文件会提示拒绝访问。安装脚本同样 `Excludes: "ucrtbase.dll"`。

安装包图标使用 `app.ico`。改图标后请重新执行 `打包成EXE.bat` 和 `生成安装包.bat`。
