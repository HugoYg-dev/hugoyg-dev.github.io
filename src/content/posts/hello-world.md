---
title: Hello World
published: 2026-08-31
description: "博客的第一篇文章，简单记录这个站点的技术构成与后续写作方向。"
tags: []
category: 站点
draft: false
---

这是我博客的第一篇文章。这个站点基于 [Astro](https://astro.build/) 静态框架和 [Fuwari](https://github.com/saicaca/fuwari) 主题搭建，托管在 GitHub Pages 上。

## 这个博客用了什么

平时写作只需要把 Markdown 文件放进 `src/content/posts/` 目录，推送到 GitHub 后由 GitHub Actions 自动构建并发布，大约一两分钟就会生效。

站内的纯静态全文搜索交给 Pagefind，不需要服务端；评论系统接了基于 GitHub Discussions 的 [giscus](https://giscus.app/)，同时站点也提供 RSS 输出，用常规阅读器就能订阅。

## 后面打算写什么

主要记录技术笔记和开发时踩过的坑，偶尔也会写一点生活记录。
