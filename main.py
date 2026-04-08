# -*- coding: utf-8 -*-
"""
LeiTingQuantPro 专业量化终端（Hummingbot 级架构）
运行：在 QuantPro_Hummingbot_OKX 目录执行  python main.py
"""
from __future__ import annotations

import os
import shutil
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QStyleFactory

ROOT = Path(__file__).resolve().parent


def _app_logo_icon() -> QIcon:
    env_logo = (os.getenv("QUANTPRO_LOGO_PATH") or "").strip()
    candidates = [
        Path(env_logo) if env_logo else None,
        ROOT / "assets" / "logo.png",
        ROOT / "config" / "logo.png",
        ROOT / "assets" / "logo.ico",
        ROOT / "config" / "logo.ico",
    ]
    for p in candidates:
        try:
            if p is None:
                continue
            if p.is_file():
                return QIcon(str(p))
        except Exception:
            continue
    return QIcon()


def _ensure_qt_plugin_paths() -> None:
    """避免工程路径含中文等字符时，Qt 找不到 platforms 插件导致窗口无法创建。"""
    try:
        import PyQt5

        base = Path(PyQt5.__file__).resolve().parent
        for sub in ("Qt5", "Qt"):
            plugins = base / sub / "plugins"
            if plugins.is_dir():
                os.environ.setdefault("QT_PLUGIN_PATH", str(plugins))
                plat = plugins / "platforms"
                if plat.is_dir():
                    os.environ.setdefault(
                        "QT_QPA_PLATFORM_PLUGIN_PATH", str(plat)
                    )
                break
    except Exception:
        pass
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def ensure_env_file() -> None:
    """若无 config/.env，则从 .env.example 复制一份，便于直接编辑。"""
    env_path = ROOT / "config" / ".env"
    example = ROOT / "config" / ".env.example"
    env_path.parent.mkdir(parents=True, exist_ok=True)
    if env_path.is_file():
        return
    if example.is_file():
        shutil.copyfile(example, env_path)
        print(
            "提示: 已创建 config/.env（由 .env.example 复制）。"
            "请用编辑器填写 OKX 密钥与国内代理（如 PROXY=http://127.0.0.1:7890），保存后重启。"
        )
    else:
        print("提示: 缺少 config/.env 且无 .env.example，请手动创建 config/.env。")


from core.engine import StrategyEngine
from core.logger import Logger
from core.okx_api import OKXApi
from core.order_manager import OrderManager
from core.risk_manager import RiskManager
from ui.main_window import MainWindow


def load_config() -> dict:
    load_dotenv(dotenv_path=ROOT / "config" / ".env")
    return {
        "api_key": os.getenv("OKX_API_KEY", "").strip(),
        "secret_key": os.getenv("OKX_SECRET_KEY", "").strip(),
        "passphrase": os.getenv("OKX_PASSPHRASE", "").strip(),
        "testnet": os.getenv("OKX_TESTNET", "True").lower() in ("1", "true", "yes"),
        "proxy_host": os.getenv("PROXY_HOST", "").strip(),
        "proxy_port": os.getenv("PROXY_PORT", "").strip(),
    }


def init_okx_api(config: dict) -> OKXApi:
    api = OKXApi(
        config["api_key"],
        config["secret_key"],
        config["passphrase"],
        testnet=config["testnet"],
    )
    url = (os.getenv("PROXY_URL") or os.getenv("PROXY") or "").strip()
    if url:
        api.set_proxy_url(url)
    elif config["proxy_host"] and config["proxy_port"]:
        api.set_proxy(config["proxy_host"], config["proxy_port"])
    # 未配置代理则本地直连（不使用系统 HTTP_PROXY / ALL_PROXY）
    return api


def main() -> int:
    print("=" * 60)
    print(" LeiTingQuantPro | Hummingbot 级终端")
    print(" 正在启动…")
    print("=" * 60)

    ensure_env_file()

    cfg = load_config()

    _ensure_qt_plugin_paths()
    try:
        from PyQt5.QtCore import Qt as QtCoreQt

        QApplication.setAttribute(QtCoreQt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(QtCoreQt.AA_UseHighDpiPixmaps, True)
    except Exception:
        pass
    app = QApplication(sys.argv)
    app.setApplicationName("LeiTingQuantPro")
    app.setApplicationDisplayName("LeiTingQuantPro")
    app.setOrganizationName("LeiTingQuantPro")
    if sys.platform == "win32":
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "LeiTingQuantPro.App"
            )
        except Exception:
            pass
    icon = _app_logo_icon()
    if not icon.isNull():
        app.setWindowIcon(icon)
    logger = Logger(log_dir=ROOT / "logs")
    try:
        legacy_logs = list((ROOT / "logs").glob("quantpro_*.log"))
        if legacy_logs:
            logger.info(
                "品牌迁移提示：检测到旧日志前缀 quantpro_*.log。"
                "当前版本已切换为 leitingquantpro_*.log；"
                "日报 webhook 事件类型已切换为 leitingquantpro_daily。"
            )
    except Exception:
        pass

    native_ui = (os.getenv("QUANTPRO_NATIVE_UI") or "").strip().lower() in (
        "1",
        "true",
        "yes",
    )
    if native_ui:
        if sys.platform == "win32":
            for _style_name in ("windowsvista", "Windows"):
                if _style_name in QStyleFactory.keys():
                    app.setStyle(_style_name)
                    logger.info(f"界面：系统原生样式（{_style_name}），未加载深色 QSS")
                    break
            else:
                if "Fusion" in QStyleFactory.keys():
                    app.setStyle("Fusion")
                    logger.info("界面：未找到 Windows 原生样式，回退 Fusion（无 QSS）")
        else:
            if "Fusion" in QStyleFactory.keys():
                app.setStyle("Fusion")
                logger.info("界面：非 Windows 下 QUANTPRO_NATIVE_UI 使用 Fusion（无 QSS）")
    else:
        try:
            if "Fusion" in QStyleFactory.keys():
                app.setStyle("Fusion")
        except Exception:
            pass

    from PyQt5.QtGui import QFont

    f = QFont("Microsoft YaHei UI", 13)
    f.setStyleHint(QFont.SansSerif)
    app.setFont(f)

    # 让“激活窗口”等启动前弹窗也套用同款终端风格（否则会是白底系统风）
    if not native_ui:
        qss_path = ROOT / "ui" / "hummingbot_style.qss"
        if (os.getenv("QUANTPRO_NO_QSS") or "").strip().lower() in ("1", "true", "yes"):
            pass
        elif qss_path.is_file():
            try:
                app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
            except Exception:
                pass

    def _global_excepthook(exc_type, value, tb) -> None:
        if exc_type is KeyboardInterrupt:
            sys.__excepthook__(exc_type, value, tb)
            return
        try:
            logger.error(
                "未捕获异常:\n"
                + "".join(traceback.format_exception(exc_type, value, tb))[:2000]
            )
        except Exception:
            pass
        sys.__excepthook__(exc_type, value, tb)

    sys.excepthook = _global_excepthook

    # 本地源码模式：暂不弹出激活窗口（发布版再开启授权闭环）。

    try:
        okx_api = init_okx_api(cfg)
        logger.info("OKX API 对象已创建（密钥为空时仅可访问公共接口）")
        if not (
            (os.getenv("PROXY_URL") or os.getenv("PROXY") or "").strip()
            or (cfg["proxy_host"] and cfg["proxy_port"])
        ):
            logger.info("网络：本地直连（已忽略系统 HTTP_PROXY；需代理请填 .env 或顶栏）")
    except Exception as e:
        logger.error(f"OKX API 初始化异常: {e}")
        okx_api = None

    risk = RiskManager(
        logger,
        daily_equity_state_path=ROOT / "config" / "risk_daily_equity.json",
    )
    order_mgr = OrderManager(okx_api, logger, risk, project_root=ROOT)
    engine = StrategyEngine(
        okx_api, logger, risk, order_mgr, project_root=ROOT
    )

    qss_path = ROOT / "ui" / "hummingbot_style.qss"
    if native_ui:
        pass
    elif (os.getenv("QUANTPRO_NO_QSS") or "").strip().lower() in ("1", "true", "yes"):
        logger.warn("已跳过界面样式表（QUANTPRO_NO_QSS=1），使用系统默认配色以便排查「看不见」问题")
    elif qss_path.is_file():
        try:
            app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
            logger.info("成功加载深色终端样式表（更像交易终端；要系统原生外观请设 QUANTPRO_NATIVE_UI=1）")
        except Exception as e:
            logger.error(f"样式表加载失败: {e}")

    try:
        win = MainWindow(
            okx_api, logger, order_mgr, risk, engine, project_root=ROOT
        )
        if (os.getenv("QUANTPRO_MAXIMIZE") or "").strip().lower() in ("1", "true", "yes"):
            win.showMaximized()
        else:
            win.show()
        logger.info("主界面启动完成")
    except Exception as e:
        import traceback

        tb = traceback.format_exc()
        logger.error(f"主界面创建失败:\n{tb}")
        print(tb, file=sys.stderr)
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.critical(
            None,
            "LeiTingQuantPro 启动失败",
            f"{e}\n\n详细错误已写入 logs 目录，请把最新日志发给开发者。",
        )
        return 1
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
