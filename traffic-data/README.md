# GitHub Traffic 长期统计

本目录用于按天保存本仓库的 GitHub Traffic 数据。数据来自 GitHub 官方 REST API 的仓库 Traffic `views` 与 `clones` 端点，时间按 UTC 日期记录。

## 指标含义

- `views`：当天仓库页面的总浏览次数；同一访客多次浏览会重复计数。
- `unique_visitors`：GitHub 在当天统计到的独立访客数。
- `clones`：当天仓库被 Clone 的总次数；同一用户多次 Clone 会重复计数。
- `unique_cloners`：GitHub 在当天统计到的独立 Clone 用户数。

数据保存在 `traffic.json`。`daily` 数组以 `date` 为键，每个 UTC 日期最多一条记录；`updated_at` 表示最近一次数据发生变化并写入文件的 UTC 时间。若 API 数据没有变化，文件保持不变，也不会产生空洞的自动提交。

## 更新方式与 14 天限制

GitHub Actions 每天 UTC 01:23（北京时间 09:23）自动运行，也可以在 Actions 页面用 `workflow_dispatch` 手动运行。GitHub 的 Traffic API 每次只返回最近 14 天的滚动窗口，因此脚本不会累加接口返回的 14 天汇总值，而是按日期合并每日明细：窗口内的同一日期会被最新结果覆盖，早于窗口且已经保存的数据会保留。这样既能修正 GitHub 后续更新的近期数据，也不会重复计算重叠日期。

统计从本功能首次成功运行时开始积累。首次运行以前、且已超出 GitHub 14 天窗口的数据无法补回。如果自动任务连续超过 14 天没有成功运行，中间滑出窗口的数据同样无法恢复。

## 哪些长期统计可信

- 将每日 `views` 相加，可作为已保存期间的总浏览次数。
- 将每日 `clones` 相加，可作为已保存期间的总 Clone 次数。
- 每天的 `unique_visitors` 和 `unique_cloners` 数值本身可信，可用于观察每日独立访问/Clone 的趋势。

不要把各天的 `unique_visitors` 或 `unique_cloners` 相加后称为“历史累计独立人数”。GitHub 只提供每个统计周期内去重后的数量，不提供匿名用户标识，也不提供跨全部历史的全局去重结果。同一个人可能在不同日期再次访问或 Clone，并在多天中各计一次，所以无法准确得到从建库至今的累计独立访客或独立 Clone 用户人数。

## 权限与令牌

读取 Traffic API 使用仓库 Secret `TRAFFIC_TOKEN`。建议使用仅授权本仓库、仅具有 **Administration: Read-only** 权限的 fine-grained personal access token。工作流自带的 `GITHUB_TOKEN` 仅使用 `contents: write`，负责在数据变化时提交并推送 `traffic.json`。

自动提交使用信息 `chore: update traffic statistics`。由仓库 `GITHUB_TOKEN` 推送的提交不会再次触发普通 `push` 工作流，因此不会形成无限循环；本工作流本身也只监听定时和手动触发事件。
