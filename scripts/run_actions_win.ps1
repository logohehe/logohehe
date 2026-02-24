param(
  [Parameter(Mandatory=$true)][string]$Plan
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Plan)) { throw "Plan not found: $Plan" }
$data = Get-Content -Raw -Path $Plan | ConvertFrom-Json

Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class WinInput {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
  public const uint LEFTDOWN = 0x0002;
  public const uint LEFTUP = 0x0004;
  public const uint RIGHTDOWN = 0x0008;
  public const uint RIGHTUP = 0x0010;
}
"@

$wshell = New-Object -ComObject WScript.Shell
$startDelay = [double]($data.start_delay)
if ($startDelay -gt 0) { Start-Sleep -Milliseconds ([int]($startDelay * 1000)) }

foreach ($a in $data.actions) {
  switch ($a.type) {
    'move' {
      [WinInput]::SetCursorPos([int]$a.x, [int]$a.y) | Out-Null
    }
    'click' {
      if ($null -ne $a.x -and $null -ne $a.y) {
        [WinInput]::SetCursorPos([int]$a.x, [int]$a.y) | Out-Null
        Start-Sleep -Milliseconds 80
      }
      $btn = [string]$a.button
      if ($btn -eq 'right') {
        [WinInput]::mouse_event([WinInput]::RIGHTDOWN,0,0,0,[UIntPtr]::Zero)
        Start-Sleep -Milliseconds 35
        [WinInput]::mouse_event([WinInput]::RIGHTUP,0,0,0,[UIntPtr]::Zero)
      } else {
        [WinInput]::mouse_event([WinInput]::LEFTDOWN,0,0,0,[UIntPtr]::Zero)
        Start-Sleep -Milliseconds 35
        [WinInput]::mouse_event([WinInput]::LEFTUP,0,0,0,[UIntPtr]::Zero)
      }
    }
    'wait' {
      Start-Sleep -Milliseconds ([int]([double]$a.seconds * 1000))
    }
    'type' {
      $wshell.SendKeys([string]$a.text)
    }
    'key' {
      switch ([string]$a.key) {
        'enter' { $wshell.SendKeys('{ENTER}') }
        'esc' { $wshell.SendKeys('{ESC}') }
        default { $wshell.SendKeys([string]$a.key) }
      }
    }
    'launch' {
      Start-Process -FilePath ([string]$a.path) | Out-Null
    }
    default {
      throw "Unsupported action type: $($a.type)"
    }
  }
}

Write-Output 'Execution complete'
