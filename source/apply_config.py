# -*- coding: utf-8 -*-
"""把 app/config.json 应用到界面、窗口和安装脚本，方便改成同类监测系统。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG_JSON = ROOT / "app" / "config.json"
CONFIG_JS = ROOT / "app" / "config.js"
SPEC = ROOT / "甲韵康跃监测系统.spec"
ISS = ROOT / "installer" / "甲韵康跃监测系统.iss"
BRANDING_BAT = ROOT / "branding.inc.bat"


def load_config() -> dict:
    if not CONFIG_JSON.exists():
        raise FileNotFoundError(f"找不到配置文件: {CONFIG_JSON}")
    return json.loads(CONFIG_JSON.read_text(encoding="utf-8"))


def write_config_js(cfg: dict) -> None:
    payload = json.dumps(cfg, ensure_ascii=False, indent=2)
    CONFIG_JS.write_text(
        "/* 由 apply_config.py 根据 config.json 生成，请改 json 而不是这份 js */\n"
        "window.APP_CONFIG = " + payload + ";\n",
        encoding="utf-8",
    )


def patch_iss(cfg: dict) -> None:
    if not ISS.exists():
        return
    b = cfg["branding"]
    text = ISS.read_text(encoding="utf-8")
    text = re.sub(r'#define MyAppName ".*"', f'#define MyAppName "{b["short_name"]}"', text, count=1)
    text = re.sub(r'#define MyAppVersion ".*"', f'#define MyAppVersion "{b["version"]}"', text, count=1)
    text = re.sub(r'#define MyAppPublisher ".*"', f'#define MyAppPublisher "{b["publisher"]}"', text, count=1)
    text = re.sub(r'#define MyAppExeName ".*"', f'#define MyAppExeName "{b["short_name"]}.exe"', text, count=1)
    aid = b["installer_id"].strip("{}")
    text = re.sub(r"AppId=\{\{[^}]+\}\}", f"AppId={{{{{{aid}}}}}}", text, count=1)
    text = re.sub(
        r"OutputBaseFilename=.*",
        f"OutputBaseFilename={b['short_name']}安装包",
        text,
        count=1,
    )
    text = re.sub(r"VersionInfoVersion=.*", f"VersionInfoVersion={b['version']}", text, count=1)
    ISS.write_text(text, encoding="utf-8")


def patch_spec(cfg: dict) -> None:
    if not SPEC.exists():
        return
    name = cfg["branding"]["short_name"]
    text = SPEC.read_text(encoding="utf-8")
    text = re.sub(r"name='[^']+'", f"name='{name}'", text)
    SPEC.write_text(text, encoding="utf-8")


def write_branding_bat(cfg: dict) -> None:
    name = cfg["branding"]["short_name"]
    BRANDING_BAT.write_text(
        "@echo off\n"
        f'set "APP_SHORT_NAME={name}"\n',
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="应用 config.json")
    parser.add_argument(
        "--runtime",
        action="store_true",
        help="只生成 config.js，不改安装脚本（启动软件时用）",
    )
    args = parser.parse_args()
    cfg = load_config()
    write_config_js(cfg)
    write_branding_bat(cfg)
    if not args.runtime:
        patch_iss(cfg)
        patch_spec(cfg)
        print("已写入 app/config.js，并更新 spec / Inno Setup 名称与版本。")
        print(f"当前产品：{cfg['branding']['app_name']}  {cfg['branding']['version']}")
        print("请再用 打包成EXE.bat、生成安装包.bat 生成新安装包。")
    else:
        print("已同步 app/config.js")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"应用配置失败: {exc}", file=sys.stderr)
        sys.exit(1)
