# 🍥 Hugo Yang's Blog

[![Astro](https://img.shields.io/badge/Astro-5.x-BC52EE?style=flat-square&logo=astro&logoColor=white)](https://astro.build/)
[![Svelte](https://img.shields.io/badge/Svelte-5.x-FF3E00?style=flat-square&logo=svelte&logoColor=white)](https://svelte.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Pagefind](https://img.shields.io/badge/Search-Pagefind-blue?style=flat-square)](https://pagefind.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

基于 [Astro 5](https://astro.build/) 与 [Fuwari](https://github.com/saicaca/fuwari) 主题构建的高性能静态个人博客，托管于 GitHub Pages。

- 🌐 **在线站点**：<https://hugoyg-dev.github.io/blogs/>
- 📰 **RSS 订阅**：<https://hugoyg-dev.github.io/blogs/rss.xml>

---

## ✨ 特性

- ⚡ **Astro 5 + Svelte 5**：极速静态生成与 Islands 架构，默认零 JS。
- 🎨 **精美设计**：Material / 卡片式响应式布局，支持亮暗色切换与主题色自定义。
- 🔍 **站内搜索**：基于 [Pagefind](https://pagefind.app/) 的客户端全文静态检索。
- 🌊 **平滑过渡**：基于 Swup 的 SPA 级无刷新路由切换。
- 📝 **丰富扩展**：代码高亮 (Expressive Code)、KaTeX 数学公式、Admonitions 提示块、GitHub 卡片等。
- 💬 **评论与统计**：集成 [giscus](https://giscus.app/) 评论系统与轻量隐私统计（GoatCounter / Umami）。
- 🤖 **自动部署**：基于 GitHub Actions 推送即自动编译发布至 GitHub Pages。

---

## 🚀 快速开始

### 前置要求

- Node.js >= 20
- pnpm >= 9

### 常用命令

```bash
# 1. 克隆仓库与安装依赖
git clone https://github.com/HugoYg-dev/blogs.git
cd blogs
pnpm install

# 2. 本地开发 (http://localhost:4321)
pnpm dev

# 3. 静态构建与索引生成
pnpm build

# 4. 本地预览构建产物
pnpm preview
```

---

## ✍️ 内容与配置

### 1. 新建文章

```bash
pnpm new-post my-first-post
```

生成的 Markdown 文件位于 `src/content/posts/my-first-post.md`，Frontmatter 示例：

```yaml
---
title: "文章标题"
published: 2026-08-31
description: "文章简述或摘要"
tags: ["Astro", "前端"]
category: "技术分享"
draft: false
---
```

### 2. 站点配置

所有核心配置集中在 [`src/config.ts`](src/config.ts)：

| 配置项 | 作用 |
| :--- | :--- |
| `siteConfig` | 站点标题、副标题、默认语言、主题色、横幅等 |
| `profileConfig` | 个人资料、头像、简介及社交链接（GitHub、RSS 等） |
| `navBarConfig` | 顶部导航栏菜单项 |
| `commentConfig` | [giscus](https://giscus.app/) 评论系统参数（仓库 ID、分类等） |
| `analyticsConfig` | GoatCounter / Umami 访问统计 |
| `licenseConfig` | 文章原创版权声明（默认 CC BY-NC-SA 4.0） |

---

## 📜 常用脚本

| 命令 | 描述 |
| :--- | :--- |
| `pnpm dev` | 启动本地开发服务 |
| `pnpm build` | 静态编译生成产物并构建 Pagefind 搜索索引 |
| `pnpm preview` | 本地预览构建产物（含搜索功能） |
| `pnpm new-post <name>` | 快速创建新文章模板 |
| `pnpm lint` / `pnpm format` | 使用 Biome 进行代码检查与格式化 |
| `pnpm type-check` | TypeScript 类型检查 |

---

## 📁 目录结构

```text
blogs/
├── .github/workflows/   # GitHub Actions 自动化部署工作流
├── public/              # 静态公共资源（favicon 等）
├── scripts/             # 工具脚本（如 new-post.js）
├── src/
│   ├── assets/          # 图片资源、头像、横幅
│   ├── components/      # Astro / Svelte 组件库（评论、统计等）
│   ├── config.ts        # ⭐️ 站点核心配置文件
│   ├── content/posts/   # ✍️ 博客文章 Markdown 文件
│   ├── layouts/         # 页面布局模板
│   ├── pages/           # 站点路由页面（首页、归档、关于等）
│   └── styles/          # Tailwind 与全局样式
├── astro.config.mjs     # Astro 配置文件
└── package.json         # 项目依赖与脚本
```
