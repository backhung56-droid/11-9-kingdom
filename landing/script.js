/* 세미나 온라인 신청 주소: 변경 시 이 값과 landing/index.html의 href도 함께 수정하세요. */
const REGISTRATION_URL = 'https://forms.gle/MtNb68xxpQVmZByk9';

function applyRegistration() {
  let parsed;
  try { parsed = new URL(REGISTRATION_URL); } catch { return; }
  if (parsed.protocol !== 'https:') return;
  document.querySelectorAll('.register-link').forEach(link => {
    link.href = parsed.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    link.setAttribute('aria-label', '세미나 온라인 신청 페이지 열기');
  });
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', applyRegistration, { once: true });
} else {
  applyRegistration();
}
