---
title: Hello World
published: 2026-08-31
description: "博客的第一篇文章：这个站点是如何搭建的。"
tags: []
category: 站点
draft: false
---

欢迎来到我的博客！这是本站的第一篇文章。

## 这个站点是怎么搭的

本站基于 [Astro](https://astro.build/) 静态站点框架和 [Fuwari](https://github.com/saicaca/fuwari) 主题搭建，托管在 GitHub Pages 上：

- **写作**：所有文章都是 Markdown 文件，放在 `src/content/posts/` 目录下
- **搜索**：Pagefind 提供的纯静态全文搜索，无需任何服务端
- **评论**：基于 GitHub Discussions 的 [giscus](https://giscus.app/) 评论系统
- **订阅**：站点提供 RSS 输出，可用任意 RSS 阅读器订阅
- **部署**：推送到 GitHub 后，GitHub Actions 自动构建并发布，约 1–2 分钟生效

## 我会写什么

主要是技术笔记、开发中踩过的坑，偶尔也有一些生活记录。

感谢阅读，欢迎常来。
