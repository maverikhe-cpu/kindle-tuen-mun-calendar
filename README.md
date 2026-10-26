# 屯门 Kindle 日历

为 600×800 Kindle 和 DayPane 提供中文月历、香港屯门站实测气温与全港天气预报。使用香港天文台公开 API，不包含个人日程或账户数据。

Cloudflare Worker 每 5 分钟检查图片时间，超过 25 分钟且没有运行中的任务时，通过 GitHub API 触发生成；由 GitHub Actions 渲染、GitHub Pages 发布。GitHub 原有每小时第 17、47 分钟调度保留作备用。更新不是实时保证，任务排队和设备拉取仍会增加延迟。Kindle 上的 DayPane 使用 `screen.png` 图源，自动读取旁边的 `manifest.json` 并核对图片 SHA-256。Mac 无需开机；Kindle 需要 Wi-Fi 且看板保持运行，设备真正休眠时插件不会按时刷新。

图上分别标注观测时间与画面生成时间。数据源故障时日期仍更新，气温显示暂无数据，预报为空，不伪造天气。月历不标注公众假期。

公开仓库的定时工作流可能因连续 60 天无仓库活动而被 GitHub 停用；工作流每天在文件中记录运行日期以维持仓库活动。可在 Actions 手动运行或停用。

本地运行：`pip install -r requirements.txt`，设置 `FONT_PATH` 为中文字体路径，然后 `python render.py`。Linux 使用 Noto Sans CJK，macOS 默认使用系统黑体。

数据来源：https://www.hko.gov.hk/en/abouthko/opendata_intro.htm

农历日期由香港天文台公历与农历对照 API 按香港当天日期取得，显示干支年份和月日（包括闰月）。接口失败时明确显示农历暂不可用。

调度器源码位于 `scheduler/`，部署使用 `npx wrangler deploy --config scheduler/wrangler.jsonc`。GitHub 凭证只存于 Cloudflare 加密 secret `GITHUB_TOKEN`，不写入源码；凭证撤销后需要重新配置。`node --test scheduler/worker.test.mjs` 验证新鲜图片跳过、过期补跑、运行中去重和接口失败。Cloudflare 日志记录 fresh / already-running / dispatched，可核对真实定时调用。
