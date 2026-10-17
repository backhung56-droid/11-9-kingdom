# 패러다임의 변화와 킹덤처치의 비전 — 신청 랜딩페이지

## 실행 / 배포
`landing/index.html`을 브라우저로 열거나 `landing/` 폴더를 Netlify에 배포하세요.

## 온라인 세미나 신청
**구글 신청서:** https://forms.gle/MtNb68xxpQVmZByk9

모든 신청 버튼(헤더/히어로/행사 안내/마지막 섹션/모바일 고정 버튼)이 위 구글폼으로 연결됩니다. 문의 전화는 행사 정보 영역에만 남겨두었습니다.

신청 링크를 변경할 경우 `landing/index.html`의 등록 CTA href와 `landing/script.js`의 `REGISTRATION_URL`을 함께 수정하세요. `landing_standalone.html`은 `pipeline.py`로 다시 생성할 수 있습니다.

## 이미지
`landing/assets/speaker-lee-jongpil.webp`는 사용자 제공 이종필 목사 사진을 최적화한 파일입니다.

## 아직 필요한 확인
- 참가비 및 자세한 참석 안내
- 승인된 공식 브랜드 로고 PNG/SVG (현재 문자 표기)

## 재빌드
`python pipeline.py`로 소스 검사/브라우저 캡처/ZIP 생성. 브라우저 기능이 없으면 `python pipeline.py --no-capture`로 정적 검사 및 ZIP 생성만 가능합니다.
