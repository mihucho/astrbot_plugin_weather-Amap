# Changelog

本文件记录了本项目的所有重要变更。

---

## [v1.0.4] - 2026-03-05

### Added
- 天气数据缓存机制
  - 实况天气缓存：有效期1小时 (3600秒)
  - 预报天气缓存：有效期4小时 (14400秒)
  - 使用 `get_kv_data()` 和 `put_kv_data()` 实现缓存读写
  - 缓存键名格式：`{城市名}_current` 和 `{城市名}_forecast`
  - 自动检测缓存过期并重新获取数据
  - 添加详细的缓存日志输出，便于调试

### Changed
- **图片处理优化**：移除图片转换为base64功能，改为直接返回文件路径
  - `render_current_weather()` 和 `render_forecast_weather()` 现在返回本地文件路径
  - 新增导入 `from astrbot.core.utils.io import download_image_by_url`
  - 提升图片处理性能，避免base64转换开销
- **插件名称更新**：确保唯一性
  - 注册名称从 `astrbot_plugin_weather-Amap` 改为 `astrbot_plugin_weather-Amap-mihuc`
  - 避免与其他插件命名冲突
- **文本输出格式优化**
  - 天气预报文本显示：温度分隔符从 `-` 改为空格，提升可读性
  - 优化多行格式展示，更清晰的层次结构
  - 改进日期选择场景下的输出格式

### Fixed
- 修复日期过滤逻辑
  - 当用户指定的日期无数据时，不再返回错误提示
  - 改为自动降级返回全部预报数据，提升用户体验
  - 优化 `day` 参数处理逻辑，避免空结果集

### Technical Notes
- **修改文件**: `main.py`, `metadata.yaml`
- **改动类型**: 功能增强 (feat) + 性能优化 (perf) + 修复 (fix) + 代码重构 (refactor)
- **兼容性**: 向后兼容，无破坏性变更
- **影响范围**: 
  - 缓存机制：减少API调用频率，提升响应速度
  - 图片处理：提升性能，降低内存占用
  - 插件名称：确保唯一性，避免冲突
  - 用户体验：更友好的输出格式和错误处理

---

## [v1.0.3] - 2026-03-04

### Added
- `get_forecast_weather_tool()` 增加 `day` 参数支持
  - 新增可选参数 `day: Optional[str]`，用于指定查询特定日期的天气预报
  - 支持日期格式如 "2026-03-05"
  - 当未提供 `day` 参数时，返回所有预报天数（默认行为）
  - 当提供 `day` 参数时，仅返回该日期的天气数据
  - 若指定日期无数据，返回友好的错误提示

### Changed
- 天气预报数据持久化到 KV 存储
  - 使用 `put_kv_data()` 存储查询到的预报数据，键名格式为 `{城市名}_forecast`
  - 便于后续复用和缓存管理
- 优化循环变量命名：将 `day` 改为 `day_item`，避免与参数名冲突

### Technical Notes
- **修改文件**: `main.py`
- **改动类型**: 功能增强 (feat)
- **兼容性**: 向后兼容，`day` 参数为可选参数
- **影响范围**: 
  - LLM Function Calling 场景：现在可以精确查询特定日期的天气
  - 数据存储：所有预报数据自动持久化到 KV 存储

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
