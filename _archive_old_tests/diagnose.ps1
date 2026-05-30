Write-Host "ORACLE CLOUD SSH DIAGNOSTICS"
Write-Host "============================"
Write-Host ""
Write-Host "1. Network Routing Test (Ping)"
ping -n 4 138.3.245.254
Write-Host ""
Write-Host "2. SSH Port Test"
Test-NetConnection -ComputerName 138.3.245.254 -Port 22
Write-Host ""
Write-Host "3. Trace Route"
tracert -d -h 15 138.3.245.254
Write-Host ""
Write-Host "Hata Tespiti:"
Write-Host "Eğer Ping 'Request timed out' diyor ve Port Testi 'TcpTestSucceeded: False' dönüyorsa,"
Write-Host "Oracle Cloud panelinizde 'Security Lists' (Güvenlik Listeleri) veya 'Network Security Groups'"
Write-Host "kısmından mevcut bilgisayarınızın IP adresine 22 portu için izin vermeniz gerekmektedir."
