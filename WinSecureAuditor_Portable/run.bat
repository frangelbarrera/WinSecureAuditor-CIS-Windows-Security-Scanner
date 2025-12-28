@echo off
echo ========================================
echo   WinSecureAuditor - Version Portable
echo ========================================
echo.
echo Verificando privilegios de administrador...
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✓ Privilegios de administrador detectados
) else (
    echo ⚠ Advertencia: No se detectaron privilegios de administrador
    echo   Recomendado: Ejecutar como administrador para escaneos completos
    echo.
    pause
)

echo.
echo Iniciando WinSecureAuditor...
echo.
start "" "WinSecureAuditor_GUI.exe"
echo.
echo La aplicacion se ha iniciado. Puede cerrar esta ventana.
pause >nul