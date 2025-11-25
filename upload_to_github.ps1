# GitHub 快速上传脚本
# 使用方法: .\upload_to_github.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PyChatCat GitHub 上传助手" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Git 是否安装
try {
    $gitVersion = git --version
    Write-Host "✓ Git 已安装: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git 未安装！" -ForegroundColor Red
    Write-Host "请先安装 Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "按 Enter 键退出"
    exit 1
}

Write-Host ""

# 检查是否已初始化 Git 仓库
if (Test-Path .git) {
    Write-Host "✓ Git 仓库已初始化" -ForegroundColor Green
} else {
    Write-Host "正在初始化 Git 仓库..." -ForegroundColor Yellow
    git init
    Write-Host "✓ Git 仓库初始化完成" -ForegroundColor Green
}

Write-Host ""

# 检查远程仓库
$remoteUrl = git remote get-url origin 2>$null
if ($remoteUrl) {
    Write-Host "✓ 远程仓库已配置: $remoteUrl" -ForegroundColor Green
} else {
    Write-Host "⚠ 未配置远程仓库" -ForegroundColor Yellow
    Write-Host ""
    $repoUrl = Read-Host "请输入您的 GitHub 仓库地址 (例如: https://github.com/username/pychatcat.git)"
    if ($repoUrl) {
        git remote add origin $repoUrl
        Write-Host "✓ 远程仓库已添加" -ForegroundColor Green
    } else {
        Write-Host "✗ 未输入仓库地址，跳过远程配置" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  准备上传文件..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 显示将要添加的文件（排除 .gitignore 中的文件）
Write-Host "检查文件状态..." -ForegroundColor Yellow
git status --short

Write-Host ""
$confirm = Read-Host "是否继续添加所有文件并提交? (Y/N)"
if ($confirm -ne "Y" -and $confirm -ne "y") {
    Write-Host "已取消操作" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "正在添加文件..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "请输入提交信息 (直接回车使用默认信息):" -ForegroundColor Yellow
$commitMsg = Read-Host "提交信息"
if (-not $commitMsg) {
    $commitMsg = "Initial commit: PyChatCat - Python Learning Assistant with AI"
}

Write-Host ""
Write-Host "正在提交..." -ForegroundColor Yellow
git commit -m $commitMsg

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 提交成功" -ForegroundColor Green
} else {
    Write-Host "✗ 提交失败，可能没有需要提交的文件" -ForegroundColor Red
    Write-Host "使用 'git status' 查看详情" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  推送到 GitHub..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查当前分支
$currentBranch = git branch --show-current
if (-not $currentBranch) {
    Write-Host "设置默认分支为 main..." -ForegroundColor Yellow
    git branch -M main
    $currentBranch = "main"
}

Write-Host "当前分支: $currentBranch" -ForegroundColor Cyan
Write-Host ""
$pushConfirm = Read-Host "是否推送到 GitHub? (Y/N)"
if ($pushConfirm -ne "Y" -and $pushConfirm -ne "y") {
    Write-Host "已取消推送，您可以稍后使用 'git push -u origin $currentBranch' 手动推送" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "正在推送到 GitHub..." -ForegroundColor Yellow
Write-Host "提示: 如果要求输入用户名和密码，请使用 GitHub Personal Access Token 作为密码" -ForegroundColor Yellow
Write-Host ""

git push -u origin $currentBranch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✓ 上传成功！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    if ($remoteUrl) {
        $repoPage = $remoteUrl -replace '\.git$', ''
        Write-Host "访问您的仓库: $repoPage" -ForegroundColor Cyan
    }
} else {
    Write-Host ""
    Write-Host "✗ 推送失败" -ForegroundColor Red
    Write-Host "可能的原因:" -ForegroundColor Yellow
    Write-Host "  1. 网络连接问题" -ForegroundColor Yellow
    Write-Host "  2. 认证失败（请使用 Personal Access Token）" -ForegroundColor Yellow
    Write-Host "  3. 远程仓库不存在或没有权限" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "请检查错误信息并重试" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "按 Enter 键退出"

