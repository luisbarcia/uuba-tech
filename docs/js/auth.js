/**
 * Uúba Tech — Portal Auth Gate
 * Client-side password protection (obfuscated, not encryption-grade).
 * Blocks casual access. Does not resist determined inspection.
 */
(function () {
  var KEY = 'uuba_auth';
  // SHA-256 hash of the password (not the password itself)
  // Password: uuba2026
  var HASH = 'b3e244d978dbe0665a1bb1270339b49236c9d88104b5313d1204434f021f2109';

  // Check if already authenticated this session
  if (sessionStorage.getItem(KEY) === HASH) return;

  // Simple SHA-256 via SubtleCrypto
  async function sha256(msg) {
    var data = new TextEncoder().encode(msg);
    var buf = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(buf)).map(function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  // Hide page content
  document.documentElement.style.visibility = 'hidden';
  document.documentElement.style.overflow = 'hidden';

  window.addEventListener('DOMContentLoaded', function () {
    document.body.style.visibility = 'hidden';

    // Create overlay
    var overlay = document.createElement('div');
    overlay.id = 'auth-overlay';
    overlay.innerHTML = [
      '<div style="position:fixed;inset:0;background:#0f172a;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:system-ui,sans-serif;">',
      '  <div style="text-align:center;max-width:360px;padding:2rem;">',
      '    <div style="font-size:2rem;font-weight:800;color:#38bdf8;margin-bottom:0.25rem;">UUBA <span style="color:#e2e8f0;">Tech</span></div>',
      '    <div style="color:#94a3b8;font-size:0.9rem;margin-bottom:2rem;">Portal interno — acesso restrito</div>',
      '    <form id="auth-form" autocomplete="off">',
      '      <input id="auth-input" type="password" placeholder="Senha" autocomplete="off" ',
      '        style="width:100%;padding:0.75rem 1rem;border-radius:8px;border:1px solid #334155;background:#1e293b;color:#e2e8f0;font-size:1rem;outline:none;text-align:center;" />',
      '      <div id="auth-error" style="color:#f87171;font-size:0.8rem;margin-top:0.75rem;display:none;">Senha incorreta</div>',
      '      <button type="submit" style="margin-top:1rem;padding:0.6rem 2rem;border-radius:8px;border:none;background:#38bdf8;color:#0f172a;font-weight:700;font-size:0.9rem;cursor:pointer;transition:opacity 0.2s;">Entrar</button>',
      '    </form>',
      '  </div>',
      '</div>',
    ].join('\n');
    document.body.appendChild(overlay);
    overlay.style.visibility = 'visible';

    var form = document.getElementById('auth-form');
    var input = document.getElementById('auth-input');
    var error = document.getElementById('auth-error');

    setTimeout(function () { input.focus(); }, 100);

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var hash = await sha256(input.value);
      if (hash === HASH) {
        sessionStorage.setItem(KEY, HASH);
        overlay.remove();
        document.documentElement.style.visibility = '';
        document.documentElement.style.overflow = '';
        document.body.style.visibility = '';
      } else {
        error.style.display = 'block';
        input.value = '';
        input.focus();
        input.style.borderColor = '#f87171';
        setTimeout(function () { input.style.borderColor = '#334155'; }, 1500);
      }
    });
  });
})();
