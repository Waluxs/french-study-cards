# 法语词汇手册 · 临时公开版

这是独立发布目录，只包含三个学习页面、必要图片/读音资源及发布检查工具，不包含整个 Obsidian 笔记库。

## 使用

站点根网址会自动进入单词卡。支持桌面、iPad 和 iPhone 的浏览器阅读。读音需主动点按；语音引擎与在线音色可用性取决于设备。阅读状态保存在当前浏览器，可以导出/导入；不是自动云同步。

## 自动更新

1. 本地项目执行 `web/build_reader.py`、`web/build_site.py`，完成浏览器验收后执行 `web/prepare_github.py`。
2. 只将此独立目录的改动提交并推送到 `main`。不要在 Vault 根目录执行 `git add .`。
3. GitHub Actions 先核验资源哈希、卡片数量、跨页链接、唯一 ID、JavaScript 语法及发布文件白名单；失败即阻止本轮发布。
4. 检查通过后自动发布 `public/`。GitHub Actions 不会自行修改内容或进行 AI 调优。

首次启用：在仓库 **Settings → Pages → Source** 选择 **GitHub Actions**。工作流可以从 Actions 手动重新运行。

本地检查：`python scripts/check_site.py`（需要已有 Node；不需要安装 npm/Python 包）。

## 访问范围

用户已确认临时公开本学习项目中的原题和学习反馈；保留原始来源及音频署名，不授予第三方素材新的许可。`robots.txt` 仅请求不收录，不是访问控制。该站点不会在一天后自动关闭；需要在 Pages 设置中取消发布，或另行实施已确认的停用操作。

网页中不包含 GitHub 密钥，发布使用 GitHub 内置短期凭据。真实发布结果以 Actions 的 deployment URL 和运行状态为准；构建清单本身不声称已上线。

官方发布工作流参考：https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
