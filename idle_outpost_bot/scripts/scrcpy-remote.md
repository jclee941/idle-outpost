# 에뮬레이터 원격 제어 (.220)

## 옵션 1 (권장 — 설치 불필요): 브라우저로 접속

로컬 PC에서 아무 브라우저나 열고:

```
http://192.168.50.220:6080/vnc.html?host=192.168.50.220&port=6080&autoconnect=true&resize=scale
```

> .220에서 noVNC + scrcpy 가 systemd service로 항상 떠있음.
> 별도 설치 / SSH 터널 / ADB 키 페어링 불필요.

마우스 클릭 = 탭, 키보드 = 텍스트 입력, 휠 = 스크롤.

## 옵션 2: 로컬 scrcpy 사용 (zip 다운로드, admin 불필요)

PowerShell:

```powershell
$url = "https://github.com/Genymobile/scrcpy/releases/download/v3.1/scrcpy-win64-v3.1.zip"
Invoke-WebRequest $url -OutFile $env:USERPROFILE\Downloads\scrcpy.zip
Expand-Archive $env:USERPROFILE\Downloads\scrcpy.zip -DestinationPath $env:USERPROFILE\scrcpy -Force
cd $env:USERPROFILE\scrcpy\scrcpy-win64-v3.1
$env:ADB_SERVER_SOCKET = "tcp:192.168.50.220:5037"
.\scrcpy.exe
```

## 작업 순서 (어느 옵션이든)

1. Settings → Passwords & accounts → Add account → Google
2. `qwer941a@gmail.com` / `bingogo1l7!` 입력 (.env에도 저장됨)
3. Play Store → "Idle Outpost" 검색 → Install
4. 설치 완료되면 한 번 실행해 튜토리얼 첫 화면까지 진행
5. 브라우저 탭 닫음 / scrcpy 종료

## 검증

```sh
ssh root@192.168.50.220 'adb shell pm list packages | grep rockbite'
# expect: package:com.rockbite.zombieoutpost
```

## 보안 (작업 끝나면 잠그기)

```sh
ssh root@192.168.50.220 'systemctl disable --now idle-outpost-vnc idle-outpost-xstack idle-outpost-adb-server'
```

## 운영 명령

```sh
# 재시작
ssh root@192.168.50.220 'systemctl restart idle-outpost-xstack idle-outpost-vnc'

# 상태
ssh root@192.168.50.220 'systemctl is-active idle-outpost-emu idle-outpost-appium idle-outpost-adb-server idle-outpost-xstack idle-outpost-vnc'
```
