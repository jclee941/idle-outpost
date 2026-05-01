# 실제 Android 폰을 봇 디바이스로 사용

emulator는 Idle Outpost의 Play Integrity 검사에 막힘. 실제 폰이 100% 확실한 경로.

## 사전 요건
- Android 11+ 폰 (Idle Outpost 요구사항)
- Idle Outpost 설치 + 한 번 실행 + Universal account 로그인 완료
- 폰과 jclee-dev / .220 가 같은 WiFi 네트워크
- USB 케이블 (최초 페어링용 — Android 11+는 USB 1회 필수)

## 1. 폰 측 설정

```
Settings → About phone → Build number를 7번 탭 (개발자모드 활성)
Settings → System → Developer options →
  USB debugging: ON
  Wireless debugging: ON         (Android 11+)
```

## 2. ADB pairing (USB로 1회만)

폰을 USB로 PC 연결, 폰에 "Allow USB debugging?" 다이얼로그 뜨면 Allow + Always.

작업 위치: jclee-dev (또는 .220 둘 다 OK, 같은 LAN이면)

```sh
# pair 모드 진입을 위해 폰에서:
# Settings → Developer options → Wireless debugging → Pair device with pairing code
# 6자리 코드 + IP:포트 표시됨

# jclee-dev에서:
adb pair <PHONE_IP>:<PAIR_PORT>
# 코드 입력 메시지 나오면 폰 화면의 6자리 코드 입력

# 그 다음 페어링 완료된 device를 일반 ADB로 연결
# 폰 화면 Wireless debugging 화면에 "IP:실제포트" 별도 표시됨 (위와 다른 포트)
adb connect <PHONE_IP>:<DEVICE_PORT>
adb devices
# expect: <PHONE_IP>:<DEVICE_PORT>    device
```

## 3. 봇 .env 갱신

```sh
# 폰 IP가 192.168.50.42 라고 가정
# .env 파일 수정:
ANDROID_DEVICE_NAME=192.168.50.42:5555
APPIUM_SERVER_URL=http://localhost:4723
# (Appium 서버는 jclee-dev에 새로 띄움 - 폰과 같은 LAN이라 OK)
```

## 4. Appium 서버를 jclee-dev에 (또는 .220에 그대로 사용)

```sh
# jclee-dev에 npm/appium 없으면 .220의 것 그대로 사용 가능
# .env에서 APPIUM_SERVER_URL=http://192.168.50.220:4723 유지

# 단, .220의 Appium은 ADB_SERVER_SOCKET=tcp:127.0.0.1:5037 라
# .220에서 폰 connect 해야 봇이 폰을 찾음
ssh root@192.168.50.220 'adb connect <PHONE_IP>:<DEVICE_PORT>; adb devices'
```

## 5. 봇 실행

```sh
cd /home/jclee/dev/idle
python -m idle_outpost_bot discover    # com.rockbite.zombieoutpost 보여야 함
python -m idle_outpost_bot calibrate --label main_screen
# screens.yaml 자동 갱신 후
IDLE_OUTPOST_DRY_RUN=1 python -m idle_outpost_bot once
python -m idle_outpost_bot run
```

## 폰 24/7 운용 팁
- 전원 어댑터 항시 연결 (배터리 0% 보호)
- Settings → Display → Screen timeout: Never (또는 30분)
- Settings → Battery → Adaptive Battery: OFF (백그라운드 게임 죽이지 마)
- WiFi 안정화: 정적 IP 할당 (라우터에서 MAC 바인딩)

## 잠금 (작업 후 emulator 인프라 정리)
```sh
ssh root@192.168.50.220 'systemctl disable --now idle-outpost-emu idle-outpost-appium idle-outpost-xstack idle-outpost-vnc'
# ADB는 살려둠 (폰 control용으로 계속 사용)
```
