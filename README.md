# 🍥 Hugo Yang's Blog

[![Astro](https://img.shields.io/badge/Astro-5.x-BC52EE?style=flat-square&logo=astro&logoColor=white)](https://astro.build/)
[![Svelte](https://img.shields.io/badge/Svelte-5.x-FF3E00?style=flat-square&logo=svelte&logoColor=white)](https://svelte.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=flat-square&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Pagefind](https://img.shields.io/badge/Search-Pagefind-blue?style=flat-square)](https://pagefind.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

> 基于 [Astro 5](https://astro.build/) 静态站点生成框架与 [Fuwari](https://github.com/saicaca/fuwari) 主题精心打造的高性能个人独立博客，托管于 GitHub Pages。

- **🌐 线上站点**：<https://hugoyg-dev.github.io/blogs/>
- **📰 RSS 订阅源**：<https://hugoyg-dev.github.io/blogs/rss.xml>

---

## 📑 目录

- [✨ 项目特性](#-项目特性)
- [🛠️ 开发环境管理](#️-开发环境管理)
- [🚀 快速开始](#-快速开始)
- [⚙️ 核心配置文件详解 (`src/config.ts`)](#️-核心配置文件详解-srcconfigts)
- [✍️ 文章编写与内容发布](#️-文章编写与内容发布)
- [💬 评论系统 (giscus)](#-评论系统-giscus)
- [📊 访问统计 (GoatCounter / Umami)](#-访问统计-goatcounter--umami)
- [🚢 自动化部署 (GitHub Actions)](#-自动化部署-github-actions)
- [📜 常用脚本命令](#-常用脚本命令)
- [📁 项目目录结构](#-项目目录结构)
- [📄 开源协议](#-开源协议)

---

## ✨ 项目特性

- ⚡ **极致性能与 Islands 架构**：基于现代化的 **Astro 5** 驱动，默认零 JS 静态直出；动态交互按需加载 **Svelte 5** 组件。
- 🎨 **精美设计与动态主题**：
  - 优雅的 Material / 卡片式响应式设计，完美适配移动端与桌面端。
  - 支持 **亮色 / 暗色模式** 自动跟随与手动平滑切换。
  - 支持 **自定义主题色色相 (Hue)** 与访客调色板，可随时调整全局主色调。
- 🔍 **纯静态全文检索 (Pagefind)**：内置轻量、极速的客户端全文搜索引擎，毫秒级索引与高亮搜索，无需任何后端服务器。
- 🌊 **流畅的单页切换体验 (Swup)**：集成 Swup 页面无刷新平滑过渡与进度条，并在路由切换时智能重载评论组件与访问统计。
- 💻 **专业的代码块体验 (Expressive Code)**：
  - 代码语法高亮（JetBrains Mono 等宽字体）、行号显示、差异高亮（diff）。
  - 支持代码块标题、折叠长代码、语言标识徽标与一键复制功能。
- 📝 **丰富的 Markdown / MDX 扩展**：
  - **KaTeX 数学公式**：支持行内与块级 LaTeX 数学公式渲染。
  - **GitHub 风格 Admonitions**：支持 `NOTE`、`TIP`、`IMPORTANT`、`WARNING`、`CAUTION` 等提示块。
  - **GitHub 仓库卡片**：使用 `::github{repo="owner/repo"}` 指令即可动态展示仓库 Star、Fork 及元数据。
  - **PhotoSwipe 画廊**：文章内图片支持点击灯箱放大、缩放与拖拽。
- 💬 **无服务器评论系统 (giscus)**：基于 GitHub Discussions 构建，透明公开、防垃圾、支持 Markdown 语法与表情表态。
- 📈 **隐私友好的访问统计**：无缝支持 **GoatCounter** 或 **Umami**，不依赖 Cookie、完全合规且兼顾访客隐私。
- 🤖 **全自动 CI/CD 流程**：基于 GitHub Actions 实现一键推送、自动静态编译与 GitHub Pages 部署。

---

## 🛠️ 开发环境管理

本项目开发遵循严谨的环境隔离与版本管理规范：

### 1. Node.js 环境管理 (`nvm` + `npm` / `pnpm`)
- **Node 版本管理**：使用 [nvm](https://github.com/nvm-sh/nvm) 管理 Node.js 版本（推荐 Node **20+** 或 **22+**）：
  ```bash
  nvm install 22
  nvm use 22
  ```
- **包依赖管理**：项目使用 **pnpm**（或通过 npm 全局安装 pnpm）管理依赖：
  ```bash
  npm install -g pnpm
  ```

### 2. Python 环境管理 (`uv`)
- 若在后续扩展中涉及 Python 自动化脚本、数据处理或 AI 辅助工具，统一使用现代 Python 包与工具管理器 [uv](https://github.com/astral-sh/uv)：
  ```bash
  # 安装 uv（若尚未安装）
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # 运行独立 Python 脚本或管理虚拟环境示例
  uv venv
  uv run script.py
  ```

---

## 🚀 快速开始

### 1. 克隆代码仓库

```bash
git clone https://github.com/HugoYg-dev/blogs.git
cd blogs
```

### 2. 安装依赖

```bash
pnpm install
```

### 3. 启动本地开发服务

```bash
pnpm dev
```
打开浏览器访问 [http://localhost:4321](http://localhost:4321) 即可实时预览。

> [!NOTE]
> **关于站内搜索**：Pagefind 全文搜索索引是在静态构建阶段生成的。在 `pnpm dev` 开发环境下搜索功能不可用属正常现象，完整搜索功能可在执行 `pnpm build` 后通过 `pnpm preview` 体验。

### 4. 构建静态产物与本地预览

```bash
# 构建静态文件到 dist/ 并自动生成 Pagefind 搜索索引
pnpm build

# 本地启动静态服务器预览构建产物
pnpm preview
```

---

## ⚙️ 核心配置文件详解 (`src/config.ts`)

站点所有个性化定制集中在 `src/config.ts` 中。以下是核心配置对象的详细说明：

### 1. `siteConfig` 站点基础配置

```ts
export const siteConfig: SiteConfig = {
  title: "Hugo Yang 的博客",        // 站点主标题（显示在首页、页面 Title 等）
  subtitle: "记录技术与生活",         // 站点副标题 / 个性签名
  lang: "zh_CN",                   // 站点默认语言：'zh_CN' | 'en' | 'ja' | 'ko' | 'zh_TW' 等
  themeColor: {
    hue: 250,                      // 默认主题色相 (0 ~ 360)：红色: 0, 青色: 200, 靛蓝: 250, 粉色: 345
    fixed: false,                  // 是否固定主题色（设为 true 则对访客隐藏右下角调色盘）
  },
  banner: {
    enable: false,                 // 是否启用文章页或首页顶部的大横幅图
    src: "assets/images/demo-banner.png", // 横幅图片路径（相对于 /src，若以 '/' 开头则相对于 /public）
    position: "center",            // 图片对齐位置：'top' | 'center' | 'bottom'
    credit: {
      enable: false,               // 是否展示横幅图片版权来源
      text: "",                    // 版权作者 / 来源名称
      url: "",                     // 来源链接
    },
  },
  toc: {
    enable: true,                  // 是否在文章详情页右侧展示文章目录 (Table of Contents)
    depth: 2,                      // 目录最大深度（支持 1 到 3 级标题）
  },
  favicon: [
    // 留空则使用默认 favicon；也可配置多套图标（支持 light/dark 模式及不同分辨率）
    // {
    //   src: '/favicon/icon.png',
    //   theme: 'light',
    //   sizes: '32x32',
    // }
  ],
};
```

### 2. `profileConfig` 个人资料配置

用于渲染左侧个人卡片、头像、个人简介与社交媒体链接：

```ts
export const profileConfig: ProfileConfig = {
  avatar: "assets/images/avatar.jpg",     // 头像路径（相对 /src 或以 / 开头相对 /public）
  name: "Hugo Yang",                      // 昵称
  bio: "AI Engineer",                     // 个人简述
  links: [
    {
      name: "GitHub",
      icon: "fa6-brands:github",          // Iconify 图标名称 (FontAwesome 6 品牌图标)
      url: "https://github.com/HugoYg-dev",
    },
    {
      name: "RSS",
      icon: "fa6-solid:rss",              // RSS 订阅图标
      url: "/rss.xml",
    },
  ],
};
```

### 3. `navBarConfig` 导航栏菜单配置

配置顶部导航栏的栏目与外部链接：

```ts
export const navBarConfig: NavBarConfig = {
  links: [
    LinkPreset.Home,     // 首页预设链接 (/)
    LinkPreset.Archive,  // 归档页预设链接 (/archive/)
    LinkPreset.About,    // 关于页预设链接 (/about/)
    {
      name: "GitHub",
      url: "https://github.com/HugoYg-dev",
      external: true,    // 外部链接，会显示外链图标并在新标签页中打开
    },
  ],
};
```

### 4. `licenseConfig` 版权协议配置

配置文章底部的原创版权声明与授权协议：

```ts
export const licenseConfig: LicenseConfig = {
  enable: true,                                       // 是否在文末展示版权卡片
  name: "CC BY-NC-SA 4.0",                           // 协议名称
  url: "https://creativecommons.org/licenses/by-nc-sa/4.0/", // 协议详情链接
};
```

### 5. `expressiveCodeConfig` 代码高亮配置

```ts
export const expressiveCodeConfig: ExpressiveCodeConfig = {
  theme: "github-dark", // 代码块主题，请选择深色主题
};
```

### 6. `commentConfig` 评论系统配置

```ts
export const commentConfig: CommentConfig = {
  enable: true,               // 是否全局开启 giscus 评论
  giscus: {
    repo: "HugoYg-dev/blogs",              // 绑定的 GitHub 仓库全名
    repoId: "R_kgDOUJUbVg",                // GitHub 仓库 ID
    category: "Announcements",             // 讨论区分类
    categoryId: "DIC_kwDOUJUbVs4DEjQt",    // 讨论区分类 ID
    mapping: "pathname",                   // 映射方式（推荐 pathname）
    reactionsEnabled: true,                // 开启表情表态
    inputPosition: "top",                  // 评论输入框位置 ('top' | 'bottom')
  },
};
```

### 7. `analyticsConfig` 访问统计配置

```ts
export const analyticsConfig: AnalyticsConfig = {
  enable: false,                           // 是否启用访问统计
  provider: "goatcounter",                 // 提供商：'goatcounter' 或 'umami'
  goatcounterSite: "https://<name>.goatcounter.com/count", // GoatCounter 站点端点
  // 若使用 Umami 则填写：
  umamiScriptSrc: "https://<umami-host>/script.js",
  umamiWebsiteId: "<your-website-id>",
};
```

---

## ✍️ 文章编写与内容发布

### 1. 创建新文章

推荐使用内置的 CLI 工具快速创建新文章：

```bash
pnpm new-post my-first-post
```
该命令会在 `src/content/posts/` 目录下自动生成 `my-first-post.md`，并预先填好合规的 Frontmatter 模版。

### 2. Frontmatter 元数据详解

每篇文章的顶部需要包含由 `---` 包裹的 YAML 元数据：

```yaml
---
title: "文章标题"                     # [必需] 文章显示标题
published: 2026-08-31                # [必需] 发布日期 (YYYY-MM-DD)
updated: 2026-09-01                  # [可选] 最后修改日期
description: "文章摘要，用于首页卡片及 SEO" # [可选] 留空时会自动从正文首段提取
image: "assets/images/cover.png"     # [可选] 文章封面特色图
tags: ["Astro", "前端开发"]           # [可选] 标签列表
category: "技术分享"                  # [可选] 文章分类
draft: false                         # [可选] 是否为草稿，true 则不会在正式构建中发布
lang: "zh_CN"                        # [可选] 文章特定语言代码（覆盖站点全局设置）
---
```

### 3. Markdown 扩展与排版语法

除了标准的 Markdown 语法外，博客内置了丰富的排版与组件扩展：

#### 📐 KaTeX 数学公式

- **行内公式**：使用 `$E = mc^2$` 渲染为行内公式。
- **块级公式**：
  ```latex
  $$
  \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
  $$
  ```

#### 💡 GitHub 风格提示块 (Admonitions)

使用与 GitHub 语法完全一致的 Callout 语法：

```markdown
> [!NOTE]
> 这是一个说明提示块，用于补充背景信息。

> [!TIP]
> 这是一个技巧提示块，提供最佳实践与高效方法。

> [!IMPORTANT]
> 这是一个重要信息提示块，强调核心关键点。

> [!WARNING]
> 这是一个警告提示块，提示潜在的兼容性或注意事项。

> [!CAUTION]
> 这是一个危险警告提示块，提示破坏性操作。
```

同时支持 Directives 指令语法：
```markdown
:::tip[自定义提示标题]
这里是提示块内容，支持多行文本与内部格式。
:::
```

#### 📦 GitHub 仓库动态卡片

只需插入一行指令，博客即可在前端实时获取 GitHub 仓库信息（Star 数、Fork 数、主语言、License、Avatar 及描述）：

```markdown
::github{repo="withastro/astro"}
```

#### 💻 代码块增强 (Expressive Code)

```ts title="src/demo.ts" ins={3} del={2}
function greet(name: string) {
  // console.log("Hello, " + name);
  console.log(`Hello, ${name}!`);
}
```
- **文件标题栏**：`title="文件名"`
- **行高亮 / 差异**：`ins={3}`（绿色新增）、`del={2}`（红色删除）、`{1, 4-6}`（高亮行）
- **折叠代码块**：`collapse={2-10}`

---

## 💬 评论系统 (giscus)

本项目集成了基于 [GitHub Discussions](https://github.com/features/discussions) 的 **[giscus](https://giscus.app/)** 评论组件。

### 启用与配置步骤

1. **开启 Discussions**：确保 GitHub 博客仓库为公开状态（Public），前往仓库 **Settings -> Features**，勾选 **Discussions**。
2. **安装 giscus App**：访问 [GitHub Apps - giscus](https://github.com/apps/giscus)，授权并安装到本仓库（`blogs`）。
3. **获取仓库及分类 ID**：
   - 打开 [giscus.app](https://giscus.app/) 官方网站。
   - 输入你的仓库名称（例如 `HugoYg-dev/blogs`）。
   - 在 **Discussion 分类** 中选择分类（通常选择 `Announcements`，仅允许仓库维护者创建讨论，避免用户在 Discussions 随意乱发帖）。
   - 在生成的脚本配置区中，复制 `data-repo-id` 和 `data-category-id`。
4. **填入配置文件**：将复制到的 ID 填入 `src/config.ts` 中的 `commentConfig` 并将 `enable` 设为 `true`。

### 架构亮点
- **Swup 路由协同**：`src/components/Comment.astro` 深度监听了 Swup 的 `page:view` 钩子，页面无刷新跳转时自动按当前 URL 路径挂载新的评论区。
- **暗黑模式即时同步**：内置 `MutationObserver` 监听全局主题状态，切换亮色/暗色时即时向 giscus iframe 发送 `postMessage` 切换主题。

---

## 📊 访问统计 (GoatCounter / Umami)

为了保护访客隐私并摆脱笨重的 Cookie 追踪，博客原生支持两款轻量、合规的现代统计服务。

### 1. GoatCounter 配置
1. 在 [GoatCounter](https://www.goatcounter.com/) 免费注册一个统计站点（或私有化部署）。
2. 在 `src/config.ts` 中配置：
   ```ts
   export const analyticsConfig: AnalyticsConfig = {
     enable: true,
     provider: "goatcounter",
     goatcounterSite: "https://your-domain.goatcounter.com/count",
   };
   ```

### 2. Umami 配置
1. 在 [Umami Cloud](https://umami.is/) 或自建 Umami 实例中添加你的站点。
2. 在 `src/config.ts` 中配置：
   ```ts
   export const analyticsConfig: AnalyticsConfig = {
     enable: true,
     provider: "umami",
     umamiScriptSrc: "https://your-umami-host.com/script.js",
     umamiWebsiteId: "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
   };
   ```

> [!NOTE]
> `src/components/Analytics.astro` 同样集成了 Swup 单页路由拦截，每次页面平滑切换时均会自动上报 PV，无需手动处理 SPA 路由统计。

---

## 🚢 自动化部署 (GitHub Actions)

项目已内置 GitHub Actions 工作流文件 [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)，实现推送即自动部署。

### 部署流程与机制
1. **触发条件**：当推送到 `main` 分支或手动在 Actions 控制台点击 `workflow_dispatch` 时触发。
2. **构建阶段**：
   - 检出仓库代码，初始化 Node.js 22 和 pnpm 缓存环境。
   - 执行 `pnpm install --frozen-lockfile` 安装依赖。
   - 执行 `pnpm build` 进行 Astro 静态编译并由 Pagefind 建立索引产出至 `dist/`。
   - 将 `dist/` 上传为 GitHub Pages 发布工件。
3. **发布阶段**：调用官方 `actions/deploy-pages@v4` 发布到 GitHub Pages。

### 首次使用设置指南
前往 GitHub 仓库主页：
1. 点击 **Settings** -> 找到左侧菜单 **Pages**。
2. 在 **Build and deployment** 下的 **Source** 下拉列表中选择 **GitHub Actions**。
3. 后续只要执行 `git push origin main`，工作流将在 1~2 分钟内自动完成发布。

---

## 📜 常用脚本命令

| 命令 | 描述 | 说明 |
| :--- | :--- | :--- |
| `pnpm dev` | 启动开发服务器 | 默认运行在 `http://localhost:4321`，支持热更新（HMR） |
| `pnpm build` | 静态编译与索引 | 编译生产产物到 `dist/` 并自动生成 Pagefind 搜索索引 |
| `pnpm preview` | 预览生产产物 | 本地启动静态服务器验证构建后的站点与搜索功能 |
| `pnpm new-post <name>` | 一键新建文章 | 在 `src/content/posts/` 下生成包含标准 Frontmatter 的 Markdown |
| `pnpm check` | 模板与类型体检 | 运行 Astro 内置的诊断工具检查组件和配置 |
| `pnpm type-check` | TypeScript 检查 | 执行严格的 TypeScript 类型断言与类型验证 |
| `pnpm format` | 代码风格格式化 | 使用现代化高速 Biome 工具格式化 `src/` 代码 |
| `pnpm lint` | 静态代码分析检查 | 使用 Biome 进行 Lint 规则检查与自动修正 |

---

## 📁 项目目录结构

```text
blogs/
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 自动化构建与部署工作流
├── docs/                       # 主题多语言文档说明
├── public/                     # 静态公共资源目录（favicon, robots 等）
├── scripts/
│   └── new-post.js             # 新建文章模板脚本 (pnpm new-post)
├── src/
│   ├── assets/                 # 静态图片资源、头像、横幅等
│   ├── components/             # 核心组件库（Header, Footer, Comment, Analytics 等）
│   │   ├── Analytics.astro     # GoatCounter / Umami 统计注入组件
│   │   ├── Comment.astro       # Giscus 评论系统组件
│   │   └── ...
│   ├── config.ts               # ⭐️ 站点核心配置文件（标题/头像/菜单/评论/统计等）
│   ├── constants/              # 常量定义（主题模式、链接预设等）
│   ├── content/                # 博客内容集合
│   │   ├── config.ts           # Content Collections 模式架构与类型校验定义
│   │   ├── posts/              # ✍️ 博客文章 Markdown 文件存放目录
│   │   └── spec/               # 关于页 (about.md) 等固定页面
│   ├── layouts/                # 页面通用布局模板 (MainGridLayout 等)
│   ├── pages/                  # Astro 路由体系（首页、归档、关于、RSS 等）
│   ├── plugins/                # Markdown / Rehype 插件（Admonition, GitHub卡片等）
│   ├── styles/                 # Tailwind 与全局 CSS 样式
│   └── types/                  # TypeScript 类型定义文件
├── astro.config.mjs            # Astro 整体工程与插件集成配置
├── biome.json                  # Biome 代码格式化与 Linter 规则配置
├── package.json                # 项目依赖包与脚本定义
├── pagefind.yml                # Pagefind 搜索索引配置
└── tailwind.config.cjs         # Tailwind CSS 样式配置
```

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 协议开源。博客内发布的原创文章内容默认遵循 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)（知识共享 署名-非商业性使用-相同方式共享 4.0 国际许可协议）。
