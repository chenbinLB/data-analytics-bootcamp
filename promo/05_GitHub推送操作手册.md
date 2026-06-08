# 推送到 GitHub 操作手册

> 5 分钟完成推送,前提:你的电脑装了 git,并已登录 GitHub 账号(chenbinLB)。

## 步骤 1:在 GitHub 创建空仓库

1. 打开 https://github.com/new
2. 填:
   - **Repository name**:`data-analytics-bootcamp`
   - **Description**:大厂数据分析师 4 周突击课 | 49.9 元 | 15 个跑通的 notebook
   - **Public**(公开,这样才能用 GitHub Pages 部署 JupyterLite)
   - ❌ **不要勾** "Add a README file"(我们已经有了)
   - ❌ **不要勾** "Add .gitignore"(我们已经有了)
   - ❌ **不要勾** "Choose a license"(我们已经有了)
3. 点 "Create repository"

## 步骤 2:在本地初始化 git 并推送

打开 **PowerShell**(在项目根目录下),依次执行:

```bash
# 1. 进入项目目录(替换成你的实际路径)
cd C:\Users\23596\.mavis\sessions\mvs_2cb7c6ea190c461eb815fb861c22ed5d\workspace\data-analytics-bootcamp

# 2. 初始化 git
git init

# 3. 配置用户信息(首次使用 git 必做)
git config user.name "chenbinLB"
git config user.email "你的邮箱@example.com"

# 4. 添加所有文件
git add .

# 5. 检查状态(确认 .venv / _check_deps 等没被加进来)
git status

# 6. 第一次提交
git commit -m "feat: 大厂数分 4 周突击课 v1.0(15 个 notebook 全部跑通)"

# 7. 关联远程仓库
git remote add origin https://github.com/chenbinLB/data-analytics-bootcamp.git

# 8. 推送到 main 分支
git branch -M main
git push -u origin main
```

## 步骤 3:如果推送时被要求登录

### 方式 A:GitHub Desktop(推荐,小白友好)
1. 下载 https://desktop.github.com/
2. 登录你的 GitHub 账号
3. File -> Add Local Repository -> 选本项目
4. 点 "Push origin"

### 方式 B:Personal Access Token
1. GitHub -> 头像 -> Settings -> Developer settings -> Personal access tokens -> Tokens (classic)
2. Generate new token
3. 勾选 `repo` 权限
4. 生成后**复制保存**(只显示一次)
5. 推送时:
   - Username: `chenbinLB`
   - Password: 粘贴 token(不是密码)

### 方式 C:SSH Key(进阶,推荐长期用)
```bash
# 1. 生成 SSH key
ssh-keygen -t ed25519 -C "你的邮箱@example.com"

# 2. 复制公钥
Get-Content ~\.ssh\id_ed25519.pub | clip

# 3. GitHub -> Settings -> SSH and GPG keys -> New SSH key
#    粘贴进去

# 4. 测试
ssh -T git@github.com

# 5. 推送(用 SSH 地址)
git remote set-url origin git@github.com:chenbinLB:data-analytics-bootcamp.git
git push -u origin main
```

## 步骤 4:启用 GitHub Pages(部署 JupyterLite)

推送成功后:

1. 打开 https://github.com/chenbinLB/data-analytics-bootcamp/settings/pages
2. **Source**:选 `Deploy from a branch`
3. **Branch**:选 `gh-pages` / `(root)` ← **先跳过这步**,等我帮你生成 JupyterLite 站点后再配
4. (可选)点 Save

> **GitHub Pages 部署 JupyterLite 我可以单独帮你做**,需要你告诉我:
> - 你想用什么域名(默认 chenbinLB.github.io/data-analytics-bootcamp)
> - 你的 14 个 notebook 累计大小(我帮你算过大概 600KB-1MB,数据 26MB 可能需要单独处理)

## 常见问题

### Q1:推送时提示 "Updates were rejected"
**A**:远端已经有内容了。先拉再推:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Q2:文件太大推不上去
**A**:GitHub 单文件限 100MB,仓库建议 < 1GB。
- 数据 26MB OK
- 如果太大,把 `data/ecommerce.db` 加到 .gitignore,从网盘下载

### Q3:.venv / .idea 也被推上去了
**A**:检查 .gitignore 是否在根目录,然后:
```bash
git rm -r --cached .venv
git rm -r --cached .idea
git commit -m "chore: remove ignored files from tracking"
git push
```

### Q4:Action 跑失败了
**A**:我写的 GitHub Action 在 Windows 上验证过,但 GitHub Actions 的 Windows runner 可能跟本地有差异。
如果失败:
1. 看 https://github.com/chenbinLB/data-analytics-bootcamp/actions 的报错
2. 把错误日志发我,我帮你改

## 推送成功后

你可以做这些事:

1. **分享仓库链接**:https://github.com/chenbinLB/data-analytics-bootcamp
2. **加 Star** (在仓库页右上角)
3. **写仓库介绍**:https://github.com/chenbinLB/data-analytics-bootcamp/settings -> Social preview -> Upload an image
4. **配置 GitHub Pages**(我帮你)
5. **分享到小红书 / 朋友圈**:用 promo/02_小红书3篇笔记.md 里的文案

---

**最后更新**:2026-06-09
**适用版本**:课程 v1.0
