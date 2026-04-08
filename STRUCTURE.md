## 目录分类（你要的“分类好”）

### 你日常要用/要打包的入口（放在 `apps/`）
- `apps/trader_main.py`：主交易软件入口（启动会先授权）
- `apps/installer_assistant_main.py`：安装环境检测与缺失安装助手（独立）
- `apps/license_generator_main.py`：激活码生成器（独立、持有私钥）

> 兼容：根目录的 `main.py`、`installer_assistant_main.py`、`license_generator_main.py` 仍保留可运行，但推荐统一从 `apps/` 启动/打包。

### 主程序代码
- `ui/`：界面
- `core/`：核心逻辑（引擎/风控/AI/授权等）
- `strategies/`：策略实现
- `utils/`：工具函数

### 工具程序（被 `apps/` 调用）
- `tools/installer_assistant.py`：安装助手主体
- `tools/license_generator.py`：激活码生成器主体

### 配置与数据
- `config/`：配置、logo、公钥/激活信息等
  - `config/license_public.pem`：主程序验签公钥（随软件发布）
  - `config/license_private.pem`：生成器私钥（仅开发者保管，严禁发给客户）
  - `config/license.json`：本机激活信息（用户输入激活码后生成）
- `logs/`：日志

### 打包
- `packaging/pyinstaller_build.ps1`：一键打包脚本（输出到 `dist/`）

