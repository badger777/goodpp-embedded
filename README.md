![gpp_log](readme_media/gpp_logo.png)

# Embedded Repo

SW Maestro 11기 팀 우릴봐

- 하경민 (팀장)
- 방승연
- 전형준

담당 멘토

- 강진범
- 김윤래
- 박정규
- 오은석
- 최광선

<!-- TABLE OF CONTENTS -->
## Table of Contents

- [Embedded Repo](#embedded-repo)
  - [Table of Contents](#table-of-contents)
  - [About The Project](#about-the-project)
    - [Built With](#built-with)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Contact](#contact)
    - [팀 우릴봐](#팀-우릴봐)

<!-- ABOUT THE PROJECT -->
## About The Project

![gpp_embedded](readme_media/gpp_embedded.jpeg)

푸피캠의 라즈베리파이에 들어갈 모듈,
그리고 푸피스낵바의 아두이노에 들어갈 모듈을 개발합니다.

### Built With

- H/W
  - Raspberry Pi 4 Model B Rev 1.4 8GB RAM + 32GB SD Card
  - Coral USB Accelerator
  - YR-029 - Camera kit
  - Arduino Uno Rev3
  - HC-06 - Bluetooth module
  - SG-90 - Servo motor
- S/W
  - Raspbian GNU/Linux 10 (buster)
  - Python 3.7.3
  
<!-- GETTING STARTED -->
## Getting Started

라즈베피 파이와 아두이노에서 어떻게 사용하는지를 설명합니다. 아래의 절차에 따라서 라즈베리 파이와 아두이노를 세팅하고 실행해보세요.

### Prerequisites

- Raspberry Pi Camera Setting



- USB Accelerator

1. Edge TPU runtime 설치

아래의 명령어를 실행한 뒤 Coral을 연결합니다. 이미 Coral이 연결되어 있는 상태라면 장치를 제거했다가 다시 연결합니다.

```bash
$ echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
$ curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
$ sudo apt-get update
$ sudo apt-get install libedgetpu1-std -y
```

2. Tensorflow Lite 라이브러리 설치

설치 후에 [링크1](https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi), [링크2](https://github.com/google-coral/tflite/tree/master/python/examples/detection) 등을 참고하여 Tensorflow Lite 라이브러리가 제대로 설치되었는지 확인해보세요.

```bash
$ pip3 install https://dl.google.com/coral/python/tflite_runtime-2.1.0.post1-cp37-cp37m-linux_armv7l.whl
```

3. Edge TPU API 설치

설치 후에 [링크](https://github.com/google-coral/edgetpu/tree/master/examples)를 참고하여 Tensorflow Lite 라이브러리가 제대로 설치되었는지 확인해보세요.

```bash
$ sudo apt-get install python3-edgetpu -y
```

-


 

### Installation

<!-- CONTACT -->
## Contact

### 팀 우릴봐

- 하경민 (팀장) gaonrudal@gmail.com
- 방승연 baaaang_53@yonsei.ac.kr
- 전형준 chariot0720@gmail.com
