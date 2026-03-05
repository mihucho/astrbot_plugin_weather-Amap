import aiohttp
import datetime
from typing import Optional, List, Dict
import traceback

from astrbot.api.all import (
    Star,
    Context,
    register,
    AstrMessageEvent,
    command_group,
    command,
    MessageEventResult,
    llm_tool,
)
from astrbot.api.event import filter
from astrbot.api import logger
from astrbot.core.utils.io import download_image_by_url

# ==============================
# 1) HTML 模板
# ==============================

CURRENT_WEATHER_TEMPLATE = """
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    :root {
      --bg-warm: #f2f2ee;       /* 柔砂色 */
      --accent-block: #e9e9e4;  /* 灰泥色 */
      --text-main: #1a1a1a;
      --text-dim: #999990;
      --theme-blue: #4e6ef2;    
    }

    html, body {
      margin: 0; padding: 0;
      width: 1280px; height: 720px;
      background-color: var(--bg-warm);
      color: var(--text-main);
      font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", sans-serif;
      overflow: hidden;
    }

    /* 右侧背景装饰色块 */
    .color-block {
      position: absolute;
      right: 0; top: 0;
      width: 42%; height: 100%;
      background-color: var(--accent-block);
      z-index: 0;
    }

    .container {
      position: relative;
      z-index: 1;
      width: 100%; height: 100%;
      display: flex;
      box-sizing: border-box;
    }

    /* 左侧：纯净排版区 */
    .left-section {
      flex: 1.2;
      padding: 80px 100px;
      display: flex;
      flex-direction: column;
      justify-content: space-between; /* 强制页眉页脚分离 */
    }

    .brand-header {
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 8px;
      text-transform: uppercase;
      color: var(--text-dim);
    }

    .city-hero {
      /* 这里的 margin-top 确保它在视觉中心偏上，不再与底部重叠 */
      margin-top: 60px;
    }

    .city-hero h1 {
      font-size: 180px;
      font-weight: 900;
      line-height: 0.8;
      margin: 0;
      letter-spacing: -10px;
    }

    .province-tag {
      font-size: 26px;
      font-weight: 300;
      color: var(--text-dim);
      margin-top: 30px;
      letter-spacing: 6px;
    }

    /* 底部更新时间：完全独立定位，防止重叠 */
    .footer-metadata {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }

    .line-deco {
      width: 60px;
      height: 4px;
      background: var(--theme-blue);
    }

    .update-time {
      font-size: 14px;
      color: var(--text-dim);
      letter-spacing: 2px;
      text-transform: uppercase;
    }

    /* 右侧：卡片区 */
    .right-section {
      flex: 0.8;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding-right: 120px;
    }

    .weather-card {
      background: #ffffff;
      padding: 70px;
      box-shadow: 50px 50px 100px rgba(0,0,0,0.04);
      border-radius: 2px;
      position: relative;
    }

    .temp-value {
      font-size: 240px;
      font-weight: 100;
      line-height: 0.8;
      margin-left: -12px;
      display: flex;
    }

    .temp-unit {
      font-size: 45px;
      margin-top: 25px;
      font-weight: 400;
    }

    .weather-desc {
      font-size: 48px;
      font-weight: 800;
      color: var(--theme-blue);
      margin: 20px 0 50px 0;
    }

    .stats-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 40px;
      border-top: 1px solid #f0f0f0;
      padding-top: 40px;
    }

    .stat-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 3px;
      color: var(--text-dim);
      margin-bottom: 10px;
    }

    .stat-val {
      font-size: 26px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="color-block"></div>

  <div class="container">
    <div class="left-section">
      <div class="brand-header">Weather Intelligence</div>
      
      <div class="city-hero">
        <h1>{{ city }}</h1>
        <div class="province-tag">{{ province }} / 中国</div>
      </div>

      <div class="footer-metadata">
        <div class="line-deco"></div>
        <div class="update-time">
          Last Updated<br>
          <span style="color: var(--text-main); font-weight: 600;">{{ report_time }}</span>
        </div>
        <div style="font-size: 11px; color: var(--text-dim); margin-top: 5px;">DATA SRC: AMAP API</div>
      </div>
    </div>

    <div class="right-section">
      <div class="weather-card">
        <div class="temp-value">
          {{ temp }}<span class="temp-unit">°C</span>
        </div>
        <div class="weather-desc">{{ desc }}</div>
        
        <div class="stats-grid">
          <div class="metric">
            <div class="stat-label">Humidity</div>
            <div class="stat-val">{{ humidity }}%</div>
          </div>
          <div class="metric">
            <div class="stat-label">Wind Power</div>
            <div class="stat-val">{{ wind_power }} Level</div>
          </div>
          <div class="metric" style="grid-column: span 2;">
            <div class="stat-label">Wind Direction</div>
            <div class="stat-val">{{ wind_direction }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</body>
</html>
"""

FORECAST_TEMPLATE = """
<html>
<head>
  <meta charset="UTF-8"/>
  <style>
    :root {
      --bg-warm: #f2f2ee;
      --accent-block: #e9e9e4;
      --text-main: #1a1a1a;
      --text-dim: #999990;
      --theme-blue: #6d7fb3;
      --night-deep: #3a3f4b;    
    }

    html, body {
      margin: 0; padding: 0;
      width: 1280px; height: 720px;
      background-color: var(--bg-warm);
      color: var(--text-main);
      font-family: "Helvetica Neue", Helvetica, Arial, "PingFang SC", sans-serif;
      overflow: hidden;
    }

    .container { width: 1280px; height: 720px; display: flex; box-sizing: border-box; }

    /* --- 左侧封面 --- */
    .hero-panel {
      flex: 0.4; padding: 80px; display: flex; flex-direction: column;
      justify-content: space-between; border-right: 1px solid rgba(0,0,0,0.05);
      background: var(--bg-warm);
    }
    .city-info h1 { font-size: 160px; font-weight: 900; line-height: 0.8; margin: 40px 0; letter-spacing: -10px; }
    .forecast-title { font-size: 32px; font-weight: 300; letter-spacing: 5px; color: var(--theme-blue); }

    /* --- 右侧数据面板 --- */
    .data-panel { flex: 0.6; display: flex; flex-direction: column; background: var(--accent-block); }

    /* --- 多日列表：大而轻盈的日期结构 --- */
    .day-row {
      flex: 1; display: flex; align-items: center; justify-content: space-between;
      padding: 0 45px; background: #fff; margin-bottom: 2px;
    }
    .day-row:nth-child(even) { background: #fafafa; }

    /* 白天 */
    .day-part { flex: 1; display: flex; flex-direction: column; align-items: flex-start; }
    .day-part .temp { font-size: 56px; font-weight: 100; color: var(--theme-blue); line-height: 0.9; }
    .day-part .desc { font-size: 24px; font-weight: 800; color: var(--theme-blue); margin-top: 8px; }
    .day-part .wind { font-size: 12px; color: var(--text-dim); text-transform: uppercase; margin-top: 2px; }

    /* 中间日期：优化后的“通透大字” (48px) */
    .date-mid {
      flex: 0.8; display: flex; flex-direction: column; align-items: center; justify-content: center;
      padding: 0 20px;
    }
    .date-text { 
      font-size: 56px; 
      font-weight: 900; 
      color: rgba(0,0,0,0.6); /* 使用极浅的颜色，保证大而不突兀 */
      letter-spacing: -2px;
      line-height: 0.9;
    }
    .week-text { 
      font-size: 20px; 
      letter-spacing: 6px; 
      color: var(--text-dim); 
      font-weight: 700; 
      text-transform: uppercase; 
      margin-top: 8px;
    }

    /* 夜晚 */
    .night-part { flex: 1; display: flex; flex-direction: column; align-items: flex-end; text-align: right; }
    .night-part .temp { font-size: 48px; font-weight: 400; color: var(--text-main); line-height: 0.9; }
    .night-part .desc { font-size: 22px; font-weight: 700; color: var(--text-main); margin-top: 8px; }
    .night-part .wind { font-size: 12px; color: var(--text-dim); text-transform: uppercase; margin-top: 2px; }

    /* --- 单日模式 (补全风力) --- */
    .single-wrapper { flex: 1; display: flex; gap: 2px; }
    .period-box { flex: 1; padding: 60px 45px; display: flex; flex-direction: column; justify-content: space-between; }
    .day-box { background: #fff; }
    .night-box { background: var(--night-deep); color: #fff; }
    .temp-big { font-size: 180px; font-weight: 100; line-height: 0.8; margin-top: 20px; }
    .bottom-info { font-size: 14px; letter-spacing: 3px; opacity: 0.5; border-top: 1px solid rgba(0,0,0,0.05); padding-top: 15px; margin-top: 20px; text-transform: uppercase;}

    .footer-stamp { position: absolute; bottom: 40px; left: 80px; font-size: 11px; color: var(--text-dim); letter-spacing: 2px; }
  </style>
</head>
<body>

  <div class="container">
    <div class="hero-panel">
      <div class="brand-tag">Meteo Report</div>
      <div class="city-info">
        <h1>{{ city }}</h1>
        <div class="forecast-title">
          {% if days|length == 1 %}{{ days[0].date }}{% else %}未来 {{ total_days }} 日预报{% endif %}
        </div>
      </div>
      <div style="height: 100px;"></div> 
    </div>

    <div class="data-panel">
      {% if days|length == 1 %}
        {% set d = days[0] %}
        <div class="single-wrapper">
          <div class="period-box day-box">
            <div>
              <div style="width:40px;height:40px;border:2.5px solid var(--theme-blue);border-radius:50%;margin-bottom:25px;"></div>
              <span style="font-size:36px;font-weight:800;color:var(--theme-blue);">DAYTIME</span>
              <div style="font-size:32px;font-weight:700;margin-top:10px;">{{ d.text_day }}</div>
              <div class="temp-big" style="color:var(--theme-blue);">{{ d.high }}°</div>
            </div>
            <div class="bottom-info" style="color: var(--text-main);">Wind Velocity / {{ d.day_wind }} {{ d.day_power }}级</div>
          </div>
          <div class="period-box night-box">
            <div>
              <div style="width:40px;height:40px;border-radius:50%;box-shadow:8px 8px 0 0 #fff;margin-bottom:25px;"></div>
              <span style="font-size:36px;font-weight:800;opacity:0.7;">NIGHTFALL</span>
              <div style="font-size:32px;font-weight:700;margin-top:10px;">{{ d.text_night }}</div>
              <div class="temp-big">{{ d.low }}°</div>
            </div>
            <div class="bottom-info">Atmospheric / {{ d.night_wind }} {{ d.night_power }}级</div>
          </div>
        </div>
      {% else %}
        {% for day in days %}
        <div class="day-row">
          <div class="day-part">
            <div class="temp">{{ day.high }}°</div>
            <div class="desc">{{ day.text_day }}</div>
            <div class="wind">{{ day.day_wind }} {{ day.day_power }}级</div>
          </div>

          <div class="date-mid">
            <span class="date-text">{{ day.date.split('-')[1] }}-{{ day.date.split('-')[2] }}</span>
            <span class="week-text">{{ day.week }}</span>
          </div>

          <div class="night-part">
            <div class="temp">{{ day.low }}°</div>
            <div class="desc">{{ day.text_night }}</div>
            <div class="wind">{{ day.night_wind }} {{ day.night_power }}级</div>
          </div>
        </div>
        {% endfor %}
      {% endif %}
    </div>

    <div class="footer-stamp">GEN 2026 / ATMOSPHERIC DATA / AMAP API</div>
  </div>

</body>
</html>
"""


@register(
    "astrbot_plugin_weather-Amap-mihuc",
    "BB0813",
    "一个基于高德开放平台API的天气查询插件",
    "v1.0.4",
    "https://github.com/mihucho/astrbot_plugin_weather-Amap",
)
class WeatherPlugin(Star):
    """
    这是一个调用高德开放平台API的天气查询插件示例。
    支持 /weather current /weather forecast /weather help
    - current: 查询当前实况
    - forecast: 查询未来4天天气预报
    """

    def __init__(self, context: Context, config: dict):
        super().__init__(context)
        self.config = config
        # 使用配置中的 amap_api_key
        self.api_key = config.get("amap_api_key", "")
        self.default_city = config.get("default_city", "北京")
        # 新增配置项：send_mode，控制发送模式 "image" 或 "text"
        self.send_mode = config.get("send_mode", "image")
        # 缓存过期时间（秒）：实况天气1小时，预报天气4小时
        self.current_cache_expire = 3600  # 1小时
        self.forecast_cache_expire = 14400  # 4小时
        logger.debug(
            f"WeatherPlugin initialized with API key: {self.api_key}, default_city: {self.default_city}, send_mode: {self.send_mode}"
        )

    # =============================
    # 命令组 "weather"
    # =============================
    @command_group("weather")
    def weather_group(self):
        """
        天气相关功能命令组。
        使用方法：
        /weather <子指令> <城市或其它参数>
        子指令包括：current, forecast, help
        """
        pass

    @weather_group.command("current")
    async def weather_current(
        self, event: AstrMessageEvent, city: Optional[str] = None
    ):
        """
        查看当前实况天气
        用法: /weather current <城市>
        示例: /weather current 北京
        """
        logger.info(f"User called /weather current with city={city}")
        if not city:
            city = self.default_city
        if not self.api_key:
            yield event.plain_result(
                "未配置 Amap API Key，无法查询天气。请在管理面板中配置后再试。"
            )
            return
        data = await self.get_current_weather_by_city(city)
        if data is None:
            yield event.plain_result(f"查询 [{city}] 的当前天气失败，请稍后再试。")
            return
        
        # 根据配置决定发送模式
        if self.send_mode == "image":
            result_img_url = await self.render_current_weather(data)
            yield event.image_result(result_img_url)
        else:
            text = (
                f"当前天气：\n\n"
                f"省份: {data['province']}\n\n"
                f"城市: {data['city']}\n\n"
                f"天气: {data['desc']}\n\n"
                f"温度: {data['temp']}℃\n\n"
                f"湿度: {data['humidity']}%\n\n"
                f"风向: {data['wind_direction']}\n\n"
                f"风力: {data['wind_power']}级\n\n"
                f"发布时间: {data['report_time']}"
            )
            yield event.plain_result(text)

    @weather_group.command("forecast")
    async def weather_forecast(
        self, event: AstrMessageEvent, city: Optional[str] = None
    ):
        """
        查看未来4天天气预报
        用法: /weather forecast <城市>
        示例: /weather forecast 北京
        """
        logger.info(f"User called /weather forecast with city={city}")
        if not city:
            city = self.default_city
        if not self.api_key:
            yield event.plain_result(
                "未配置 Amap API Key，无法查询天气。请在管理面板中配置后再试。"
            )
            return
        forecast_data = await self.get_forecast_weather_by_city(city)
        if forecast_data is None:
            yield event.plain_result(f"查询 [{city}] 的未来天气失败，请稍后再试。")
            return
        suggestion_data = await self.get_life_suggestion_by_city(city)

        # 根据配置决定发送模式
        if self.send_mode == "image":
            forecast_img_url = await self.render_forecast_weather(
                city, days_data=forecast_data, suggestions=suggestion_data
            )
            yield event.image_result(forecast_img_url)
        else:
            text = f"未来{len(forecast_data)}天天气预报\n\n城市: {city}\n\n"
            for day in forecast_data:
                text += (
                    f"{day['date']} {day['week']}:\n"
                    f"白天: {day['text_day']} {day['high']}℃ {day['day_wind']}{day['day_power']}级\n"
                    f"夜晚: {day['text_night']} {day['low']}℃ {day['night_wind']}{day['night_power']}级\n\n"
                )
            if suggestion_data:
                text += "生活指数:\n"
                for s in suggestion_data:
                    text += f"{s['name']}: {s['brief']}\n"
            yield event.plain_result(text)

    @weather_group.command("help")
    async def weather_help(self, event: AstrMessageEvent):
        """
        显示天气插件的帮助信息
        用法: /weather help
        """
        logger.info("User called /weather help")
        msg = (
            "=== 高德开放平台插件命令列表 ===\n\n"
            "/weather current <城市>  查看当前实况\n\n"
            "/weather forecast <城市> 查看未来4天天气预报\n\n"
            "/weather help            显示本帮助\n\n"
        )
        yield event.plain_result(msg)

    # =============================
    # LLM Function-Calling (可选)
    # =============================
    @llm_tool(name="get_current_weather")
    async def get_current_weather_tool(
        self, event: AstrMessageEvent, city: str
    ) -> MessageEventResult:
        """当用户对某个城市的天气情况感兴趣时，用于获取当前天气信息。

        Args:
            city (string): 地点，例如：杭州，或者浙江杭州
        """
        if not city:
            city = self.default_city
        data = await self.get_current_weather_by_city(city)
        if not data:
            yield event.plain_result(f"查询 [{city}] 天气失败，请稍后再试。")
            return

        if self.send_mode == "image":
            url = await self.render_current_weather(data)
            yield event.image_result(url)
        else:
            text = (
                f"当前天气：\n\n"
                f"省份: {data['province']}\n\n"
                f"城市: {data['city']}\n\n"
                f"天气: {data['desc']}\n\n"
                f"温度: {data['temp']}℃\n\n"
                f"湿度: {data['humidity']}%\n\n"
                f"风向: {data['wind_direction']}\n\n"
                f"风力: {data['wind_power']}级\n\n"
                f"发布时间: {data['report_time']}"
            )
            yield event.plain_result(text)

    @llm_tool(name="get_forecast_weather")
    async def get_forecast_weather_tool(
        self, event: AstrMessageEvent, city: str, day: Optional[str] = None
    ) -> MessageEventResult:
        """当用户对某个城市未来天气预报感兴趣时，用于获取天气预报信息。

        Args:
            city (string): 地点，例如：杭州，或者浙江杭州
            day (string, optional): 指定日期，格式如 "2026-03-05"，如果不提供则返回所有预报天数
        """
        if not city:
            city = self.default_city
        forecast_data = await self.get_forecast_weather_by_city(city)
        suggestion_data = await self.get_life_suggestion_by_city(city)
        if not forecast_data:
            yield event.plain_result(f"查询 [{city}] 天气失败，请稍后再试。")
            return
        
        # 如果指定了 day，则只返回该天的天气
        if day:
            filtered_data = [d for d in forecast_data if d['date'] == day]
            if filtered_data:
                forecast_data = filtered_data
            else:
                day = None  # 无效日期，返回全部预报
        
        if self.send_mode == "image":
            url = await self.render_forecast_weather(
                city, forecast_data, suggestion_data
            )
            yield event.image_result(url)
        else:
            # 根据是否指定 day 优化标题
            if day:
                text = f"{city} - {day} 天气预报\n\n"
            else:
                text = f"未来{len(forecast_data)}天天气预报\n\n城市: {city}\n\n"
            
            for day_item in forecast_data:
                if day:
                    # 指定了日期，使用多行格式展示详细信息
                    text += (
                        f"{day_item['week']}\n\n"
                        f"白天: {day_item['text_day']}  {day_item['high']}℃  {day_item['day_wind']}{day_item['day_power']}级\n\n"
                        f"夜晚: {day_item['text_night']}  {day_item['low']}℃  {day_item['night_wind']}{day_item['night_power']}级"
                    )
                else:
                    # 未指定日期，显示完整的日期前缀
                    text += (
                        f"{day_item['date']} {day_item['week']}:\n"
                        f"白天: {day_item['text_day']} {day_item['high']}℃ {day_item['day_wind']}{day_item['day_power']}级\n"
                        f"夜晚: {day_item['text_night']} {day_item['low']}℃ {day_item['night_wind']}{day_item['night_power']}级\n\n"
                    )
            if suggestion_data:
                text += "\n生活指数:\n\n"
                for s in suggestion_data:
                    text += f"{s['name']}: {s['brief']}\n\n"
            yield event.plain_result(text)

    # =============================
    # 核心逻辑
    # =============================
    async def get_current_weather_by_city(self, city: str) -> Optional[dict]:
        """
        调用高德开放平台API，返回城市当前实况
        缓存策略：实况天气每小时更新多次，缓存1小时
        """
        logger.debug(f"get_current_weather_by_city city={city}")
        
        # 检查缓存
        cache_key = f"{city}_current"
        cached = await self.get_kv_data(cache_key, None)
        
        if cached and isinstance(cached, dict) and "time" in cached and "data" in cached:
            # 检查缓存是否过期
            time_diff = datetime.datetime.now().timestamp() - cached["time"]
            if time_diff < self.current_cache_expire:
                logger.debug(f"返回缓存的当前天气数据，剩余有效时间: {self.current_cache_expire - time_diff:.0f}秒")
                return cached["data"]
            else:
                logger.debug(f"缓存已过期 ({time_diff:.0f}秒)，重新获取数据")
        
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {"key": self.api_key, "city": city, "extensions": "base"}
        logger.debug(f"Requesting: {url}, params={params}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    logger.debug(f"Response status: {resp.status}")
                    if resp.status == 200:
                        data = await resp.json()
                        logger.debug(f"Amap now raw data: {data}")
                        lives = data.get("lives", [])
                        if not lives:
                            return None
                        now = lives[0]
                        result = {
                            "province": now.get("province", ""),
                            "city": now.get("city", city),
                            "adcode": now.get("adcode", ""),
                            "desc": now.get("weather", "未知"),
                            "temp": now.get("temperature", "0"),
                            "wind_direction": now.get("winddirection", ""),
                            "wind_power": now.get("windpower", "0"),
                            "humidity": now.get("humidity", "0"),
                            "report_time": now.get("reporttime", ""),
                        }
                        # 存储到缓存
                        await self.put_kv_data(cache_key, {
                            "time": datetime.datetime.now().timestamp(),
                            "data": result
                        })
                        logger.debug(f"当前天气数据已缓存，有效期: {self.current_cache_expire}秒")
                        return result

                    else:
                        logger.error(
                            f"get_current_weather_by_city status={resp.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"get_current_weather_by_city error: {e}")
            logger.error(traceback.format_exc())
            return None

    async def get_forecast_weather_by_city(self, city: str) -> Optional[List[dict]]:
        """
        调用高德开放平台API，获取未来4天天气预报
        缓存策略：预报天气每天更新3次（8、11、18点），缓存4小时
        """
        logger.debug(f"get_forecast_weather_by_city city={city}")
        
        # 检查缓存
        cache_key = f"{city}_forecast"
        cached = await self.get_kv_data(cache_key, None)
        
        if cached and isinstance(cached, dict) and "time" in cached and "data" in cached:
            # 检查缓存是否过期
            time_diff = datetime.datetime.now().timestamp() - cached["time"]
            if time_diff < self.forecast_cache_expire:
                logger.debug(f"返回缓存的预报天气数据，剩余有效时间: {self.forecast_cache_expire - time_diff:.0f}秒")
                return cached["data"]
            else:
                logger.debug(f"缓存已过期 ({time_diff:.0f}秒)，重新获取数据")
        
        url = "https://restapi.amap.com/v3/weather/weatherInfo"
        params = {"key": self.api_key, "city": city, "extensions": "all"}
        logger.debug(f"Requesting forecast: {url}, params={params}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as resp:
                    logger.debug(f"Response status: {resp.status}")
                    if resp.status == 200:
                        data = await resp.json()
                        logger.debug(f"Amap daily raw data: {data}")
                        forecasts = data.get("forecasts", [])
                        if not forecasts:
                            return None
                        daily_list = forecasts[0].get("casts", [])
                        if not daily_list:
                            return None
                        result = []
                        for day_data in daily_list:
                            result.append(
                                {
                                    "date": day_data.get("date", "1970-01-01"),
                                    "week": day_data.get("week", ""),
                                    "text_day": day_data.get("dayweather", "未知"),
                                    "text_night": day_data.get("nightweather", "未知"),
                                    "high": day_data.get("daytemp", "0"),
                                    "low": day_data.get("nighttemp", "0"),
                                    "day_wind": day_data.get("daywind", ""),
                                    "night_wind": day_data.get("nightwind", ""),
                                    "day_power": day_data.get("daypower", "0"),
                                    "night_power": day_data.get("nightpower", "0"),
                                }
                            )
                        # 存储到缓存
                        await self.put_kv_data(cache_key, {
                            "time": datetime.datetime.now().timestamp(),
                            "data": result
                        })
                        logger.debug(f"预报天气数据已缓存，有效期: {self.forecast_cache_expire}秒")
                        return result
                    else:
                        logger.error(
                            f"get_forecast_weather_by_city status={resp.status}"
                        )
                        return None
        except Exception as e:
            logger.error(f"get_forecast_weather_by_city error: {e}")
            logger.error(traceback.format_exc())
            return None

    async def get_life_suggestion_by_city(self, city: str) -> Optional[List[dict]]:
        """
        调用高德开放平台API，获取生活指数
        """
        logger.debug(f"get_life_suggestion_by_city city={city}")
        # 高德开放平台不提供生活指数API，故此功能暂时无法实现
        return None

    async def render_current_weather(self, data: dict) -> str:
        """
        渲染当前天气图文信息
        """
        logger.debug(f"render_current_weather for {data}")
        url = await self.html_render(
            CURRENT_WEATHER_TEMPLATE,
            {
                "province": data["province"],
                "city": data["city"],
                "desc": data["desc"],
                "temp": data["temp"],
                "humidity": data["humidity"],
                "wind_direction": data["wind_direction"],
                "wind_power": data["wind_power"],
                "report_time": data["report_time"],
            },
            return_url=True,
        )
        # 下载图片并转换为文件路径
        image_file_path = await download_image_by_url(url)
        return image_file_path

    async def render_forecast_weather(
        self, city: str, days_data: List[dict], suggestions: Optional[List[dict]] = None
    ) -> str:
        """
        渲染未来4天天气预报图文信息
        """
        logger.debug(
            f"render_forecast_weather for city={city}, days={days_data}, suggestions={suggestions}"
        )
        url = await self.html_render(
            FORECAST_TEMPLATE,
            {
                "city": city,
                "days": days_data,
                "total_days": len(days_data),
                "suggestions": suggestions or [],
            },
            return_url=True,
        )
        # 下载图片并转换为文件路径
        image_file_path = await download_image_by_url(url)
        return image_file_path
