# Changelog

本文件记录了本项目的所有重要变更。

---

## [Released] - 2026-03-04

### Added
- LLM工具函数增加返回值支持，增强与大语言模型的集成能力
  - `get_current_weather_tool()` 现在返回天气文本信息
  - `get_forecast_weather_tool()` 现在返回天气预报文本信息
  - 便于LLM在Function Calling场景中获取结构化返回数据

### Changed
- 代码格式化与风格优化，提升代码可读性和可维护性
  - 重构导入语句：`astrbot.api.all` 的导入项拆分为多行，每行一项
  - 优化函数签名：`weather_current()` 和 `weather_forecast()` 的参数列表改为多行格式
  - 改进长字符串格式：日志输出和提示信息使用多行格式，避免单行过长
  - 规范装饰器语法：`@register` 装饰器参数列表添加尾随逗号
  - 调整空行布局：改善类和方法间的空行分布

### Technical Notes
- **修改文件**: `main.py`
- **改动类型**: 功能增强 (feat) + 代码风格优化 (style)
- **兼容性**: 向后兼容，无破坏性变更
- **影响范围**: 
  - 功能增强：LLM工具调用场景现在可获取返回值
  - 风格优化：纯格式化变更，不影响运行时行为
