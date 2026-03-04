# Changelog

本文件记录了本项目的所有重要变更。

---

## [v1.0.2] - 2026-03-04

### Added
- 命令函数增加返回值支持
  - `weather_current()` 现在返回天气文本信息
  - `weather_forecast()` 现在返回天气预报文本信息
  - 便于在命令链或自动化场景中获取结构化返回数据

### Changed
- 优化文本输出格式，提升用户可读性
  - 所有天气信息字段之间使用双换行符 `\n\n` 分隔
  - 当前天气：城市、天气、温度、湿度、风速等信息增加空行分隔
  - 天气预报：每天的天气数据之间增加空行分隔
  - 生活指数条目之间增加空行分隔
  - 帮助信息各项命令之间增加空行分隔
- 版本号更新：v1.0.1 → v1.0.2

### Technical Notes
- **修改文件**: `main.py`, `metadata.yaml`
- **改动类型**: 功能增强 (feat) + 用户体验优化 (ux)
- **兼容性**: 向后兼容，无破坏性变更
- **影响范围**: 
  - 命令函数返回值：现在可在编程场景中获取返回值
  - 文本输出格式：段落层次更清晰，可读性提升

---

## [v1.0.1] - 2026-03-04

### Added
- LLM工具函数增加返回值支持，增强与大语言模型的集成能力
  - `get_current_weather_tool()` 现在返回天气文本信息
  - `get_forecast_weather_tool()` 现在返回天气预报文本信息
  - 便于LLM在Function Calling场景中获取结构化返回数据

### Changed
- 仓库地址迁移：从 `BB0813/astrbot_plugin_weather-Amap` 迁移到 `mihucho/astrbot_plugin_weather-Amap`
  - 更新 `main.py` 中 @register 装饰器的仓库URL
  - 更新 `metadata.yaml` 中的 repo 字段
  - 更新 `README.md` 中的仓库链接
- 代码格式化与风格优化，提升代码可读性和可维护性
  - 重构导入语句：`astrbot.api.all` 的导入项拆分为多行，每行一项
  - 优化函数签名：`weather_current()` 和 `weather_forecast()` 的参数列表改为多行格式
  - 改进长字符串格式：日志输出和提示信息使用多行格式，避免单行过长
  - 规范装饰器语法：`@register` 装饰器参数列表添加尾随逗号
  - 调整空行布局：改善类和方法间的空行分布

### Technical Notes
- **修改文件**: `main.py`, `metadata.yaml`, `README.md`, `CHANGELOG.md`
- **改动类型**: 仓库迁移 (chore) + 功能增强 (feat) + 代码风格优化 (style)
- **兼容性**: 向后兼容，无破坏性变更
- **影响范围**: 
  - 仓库迁移：所有仓库链接已更新为新地址
  - 功能增强：LLM工具调用场景现在可获取返回值
  - 风格优化：纯格式化变更，不影响运行时行为
