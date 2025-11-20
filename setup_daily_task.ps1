# ===================================
# Windows 任务计划设置脚本（PowerShell）
# 自动执行每日实时策略检查
# ===================================

Write-Host ""
Write-Host "====================================" -ForegroundColor Cyan
Write-Host "🔧 设置 Windows 任务计划" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  警告: 未以管理员身份运行" -ForegroundColor Yellow
    Write-Host "建议: 右键点击PowerShell，选择'以管理员身份运行'" -ForegroundColor Yellow
    Write-Host ""
}

# 任务配置
$taskName = "QT_DailyStrategyCheck"
$taskDescription = "自动执行量化交易策略每日检查，检查TSLA/NVDA/INTC三支股票的交易信号"
$scriptPath = "K:\QT\daily_real_check.bat"
$workingDir = "K:\QT"

# 执行时间设置
$executeTime = "08:00"  # 每天早上8点（北京时间）
$executeDays = @("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")  # 工作日

Write-Host "📋 任务配置:" -ForegroundColor Green
Write-Host "  任务名称: $taskName"
Write-Host "  执行时间: 工作日（周一-周五）$executeTime"
Write-Host "  执行脚本: $scriptPath"
Write-Host "  工作目录: $workingDir"
Write-Host ""

# 删除已存在的任务
Write-Host "🗑️  检查并删除旧任务..." -ForegroundColor Yellow
try {
    $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
    if ($existingTask) {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
        Write-Host "  ✓ 已删除旧任务" -ForegroundColor Green
    } else {
        Write-Host "  ✓ 无旧任务需要删除" -ForegroundColor Green
    }
} catch {
    Write-Host "  ℹ️  未找到旧任务" -ForegroundColor Gray
}
Write-Host ""

# 创建任务动作
Write-Host "📝 创建任务计划..." -ForegroundColor Yellow
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$scriptPath`"" -WorkingDirectory $workingDir

# 创建触发器（每个工作日）
$triggers = @()
foreach ($day in $executeDays) {
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $day -At $executeTime
    $triggers += $trigger
}

# 创建任务设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 创建任务主体（以当前用户身份运行，最高权限）
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# 注册任务
try {
    Register-ScheduledTask `
        -TaskName $taskName `
        -Description $taskDescription `
        -Action $action `
        -Trigger $triggers `
        -Settings $settings `
        -Principal $principal `
        -Force | Out-Null
    
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "✅ 任务计划创建成功！" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📋 任务详情:" -ForegroundColor Cyan
    Write-Host "  • 任务名称: $taskName" -ForegroundColor White
    Write-Host "  • 执行时间: 工作日（周一-周五）$executeTime" -ForegroundColor White
    Write-Host "  • 执行脚本: $scriptPath" -ForegroundColor White
    Write-Host "  • 用户账户: $env:USERNAME" -ForegroundColor White
    Write-Host "  • 权限级别: 最高权限" -ForegroundColor White
    Write-Host ""
    
    Write-Host "💡 说明:" -ForegroundColor Cyan
    Write-Host "  • 系统将在每个工作日早上8点自动执行策略检查" -ForegroundColor White
    Write-Host "  • 检查完成后会自动发送邮件到 qsswgl@gmail.com" -ForegroundColor White
    Write-Host "  • 时间设置说明:" -ForegroundColor White
    Write-Host "    - 北京时间 08:00 = 美东时间 19:00（前一日）" -ForegroundColor Gray
    Write-Host "    - 适合在美股盘前查看策略信号" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🔍 常用命令:" -ForegroundColor Cyan
    Write-Host "  查看任务详情:" -ForegroundColor Yellow
    Write-Host "    Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  立即运行任务:" -ForegroundColor Yellow
    Write-Host "    Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  禁用任务:" -ForegroundColor Yellow
    Write-Host "    Disable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  启用任务:" -ForegroundColor Yellow
    Write-Host "    Enable-ScheduledTask -TaskName '$taskName'" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  删除任务:" -ForegroundColor Yellow
    Write-Host "    Unregister-ScheduledTask -TaskName '$taskName' -Confirm:`$false" -ForegroundColor Gray
    Write-Host ""
    
    # 显示下次运行时间
    $taskInfo = Get-ScheduledTask -TaskName $taskName | Get-ScheduledTaskInfo
    Write-Host "⏰ 下次运行时间: " -NoNewline -ForegroundColor Cyan
    Write-Host $taskInfo.NextRunTime -ForegroundColor Green
    Write-Host ""
    
    # 询问是否立即测试
    Write-Host "🧪 是否立即测试运行? (Y/N): " -NoNewline -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "Y" -or $response -eq "y") {
        Write-Host ""
        Write-Host "▶️  正在运行任务..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $taskName
        Start-Sleep -Seconds 2
        Write-Host "✓ 任务已启动，请查看邮箱接收结果" -ForegroundColor Green
        Write-Host ""
    }
    
} catch {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "❌ 任务计划创建失败！" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "错误信息: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "可能原因:" -ForegroundColor Yellow
    Write-Host "  • 权限不足（请以管理员身份运行PowerShell）" -ForegroundColor White
    Write-Host "  • 路径不正确" -ForegroundColor White
    Write-Host "  • 任务计划程序服务未运行" -ForegroundColor White
    Write-Host ""
}

Write-Host "按任意键退出..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
