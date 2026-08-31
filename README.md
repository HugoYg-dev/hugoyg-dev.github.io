# Parsonlee 的博客

基于 [Astro](https://astro.build/) 与 [Fuwari](https://github.com/saicaca/fuwari) 主题的个人博客，托管于 GitHub Pages。

**线上地址**：<https://parsonlee.github.io/>

## 本地开发

```bash
pnpm install   # 安装依赖
pnpm dev       # 启动开发服务器 http://localhost:4321
pnpm build     # 构建到 dist/（含 Pagefind 搜索索引）
pnpm preview   # 预览构建产物
```

注意：站内搜索（Pagefind）只在 `pnpm build` 后生效，`pnpm dev` 模式下搜索不可用属正常现象。

## 写新文章

1. 在 `src/content/posts/` 下新建 Markdown 文件（如 `my-post.md`），也可以运行 `pnpm new-post my-post` 生成模板
2. 填写 frontmatter：

```yaml
---
title: 文章标题
published: 2026-08-31
description: "文章摘要，显示在首页卡片上"
tags: ["标签1", "标签2"]
category: 分类名
draft: false # true 则不发布
---
```

3. `git add -A && git commit -m "..." && git push`，GitHub Actions 会自动构建并在 1–2 分钟内发布

## 站点配置

主要配置都在 `src/config.ts`：

- `siteConfig`：站点标题、副标题、语言、主题色、横幅图
- `profileConfig`：头像、昵称、简介、社交链接
- `navBarConfig`：导航栏菜单
- `licenseConfig`：文章版权协议

## 评论系统（giscus）

评论基于 [giscus](https://giscus.app/)（GitHub Discussions），仓库 ID 与分类 ID 已配置完成。

**首次启用需要一步**：安装 [giscus App](https://github.com/apps/giscus) 到本仓库（[直达链接](https://github.com/apps/giscus/installations/select_target?repository=Parsonlee.github.io)），安装后评论区立即可用；未安装时评论区会显示 giscus 的提示信息。

不需要评论时，把 `src/config.ts` 中 `commentConfig.enable` 改为 `false`。

## 访问统计

`src/config.ts` 中的 `analyticsConfig`，默认关闭。启用方式：

```ts
export const analyticsConfig: AnalyticsConfig = {
	enable: true,
	provider: "goatcounter", // 或 "umami"
	goatcounterSite: "https://<name>.goatcounter.com/count",
	// provider 为 umami 时填写:
	// umamiScriptSrc: "https://<umami-host>/script.js",
	// umamiWebsiteId: "<website-id>",
};
```

## 部署

推送到 `main` 分支后，`.github/workflows/deploy.yml` 自动执行构建与发布（Astro 构建 + Pagefind 索引 → GitHub Pages）。运行状态见仓库的 Actions 页。

## 目录速览

```
src/
├── config.ts          # 站点核心配置（标题/个人信息/评论/统计）
├── content/
│   ├── posts/         # 博客文章（Markdown）
│   └── spec/          # 关于页等固定页面
├── components/
│   ├── Comment.astro  # giscus 评论组件
│   └── Analytics.astro# 访问统计脚本注入
└── layouts/           # 页面布局
```
