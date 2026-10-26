# 屯门 Kindle 日历

为 600×800 Kindle 和 DayPane 提供中文月历、香港屯门站实测气温与全港天气预报。使用香港天文台公开 API，不包含个人日程或账户数据。

GitHub Actions 每小时第 17、47 分钟计划生成图片，由 GitHub Pages 发布。调度可能延迟。Kindle 上的 DayPane 使用 `screen.png` 图源，自动读取旁边的 `manifest.json` 并核对图片 SHA-256。Mac 无需开机；Kindle 需要 Wi-Fi 且看板保持运行，设备真正休眠时插件不会按时刷新。

图上分别标注观测时间与画面生成时间。数据源故障时日期仍更新，气温显示暂无数据，预报为空，不伪造天气。月历不标注公众假期。

公开仓库的定时工作流可能因连续 60 天无仓库活动而被 GitHub 停用；工作流每天在文件中记录运行日期以维持仓库活动。可在 Actions 手动运行或停用。

本地运行：`pip install -r requirements.txt`，设置 `FONT_PATH` 为中文字体路径，然后 `python render.py`。Linux 使用 Noto Sans CJK，macOS 默认使用系统黑体。

数据来源：https://www.hko.gov.hk/en/abouthko/opendata_intro.htm
