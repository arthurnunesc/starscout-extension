const API_BASE_URL = 'http://127.0.0.1:8000';
const BADGE_ID = 'starscout-integrity-badge';
const POPOVER_ID = 'starscout-integrity-popover';

export default defineContentScript({
  matches: ['https://github.com/*/*'],
  main() {
    installBadgeUpdater();
  },
});

type GitHubRepo = {
  owner: string;
  repo: string;
};

type StarIntegrityResponse = {
  repo: string;
  analyzed: boolean;
  currentStars: number | null;
  suspectedNonLegitStars: number | null;
  estimatedLegitStars: number | null;
  suspectedNonLegitPercent: number | null;
  breakdown: {
    lowActivity: number;
    lockstep: number;
    overlap: number;
  } | null;
  analyzedThrough: string | null;
  warnings: string[];
};

function installBadgeUpdater() {
  let lastUrl = '';

  const update = () => {
    if (lastUrl === window.location.href) {
      return;
    }
    lastUrl = window.location.href;
    void refreshBadge();
  };

  update();
  new MutationObserver(update).observe(document.documentElement, {
    childList: true,
    subtree: true,
  });
}

async function refreshBadge() {
  removeBadge();

  const repo = parseGitHubRepo(window.location);
  if (!repo) {
    return;
  }

  const anchor = findStarAnchor(repo);
  if (!anchor) {
    return;
  }

  const badge = createBadge('StarScout: checking');
  anchor.insertAdjacentElement('afterend', badge);

  try {
    const result = await fetchStarIntegrity(repo);
    badge.textContent = formatBadgeText(result);
    badge.title = 'Heuristic StarScout suspected non-legit star signal';
    badge.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      togglePopover(badge, result);
    });
  } catch {
    badge.textContent = 'StarScout: unavailable';
  }
}

function parseGitHubRepo(location: Location): GitHubRepo | null {
  if (location.hostname !== 'github.com') {
    return null;
  }

  const [owner, repo, ...rest] = location.pathname.split('/').filter(Boolean);
  if (!owner || !repo || rest.length > 0) {
    return null;
  }
  if (owner.startsWith('orgs') || owner === 'topics' || owner === 'marketplace') {
    return null;
  }

  return { owner, repo };
}

function findStarAnchor(repo: GitHubRepo): HTMLElement | null {
  const starLink = document.querySelector<HTMLElement>(
    `a[href="/${repo.owner}/${repo.repo}/stargazers"]`,
  );
  if (starLink) {
    return starLink;
  }

  const starCounter = document.querySelector<HTMLElement>('#repo-stars-counter-star');
  return starCounter?.closest<HTMLElement>('a, button, li') ?? null;
}

function createBadge(text: string): HTMLButtonElement {
  const badge = document.createElement('button');
  badge.id = BADGE_ID;
  badge.type = 'button';
  badge.textContent = text;
  badge.style.cssText = [
    'display:inline-flex',
    'align-items:center',
    'margin-left:8px',
    'padding:2px 7px',
    'border:1px solid var(--borderColor-default, #d0d7de)',
    'border-radius:999px',
    'background:var(--bgColor-muted, #f6f8fa)',
    'color:var(--fgColor-muted, #57606a)',
    'cursor:pointer',
    'font-size:12px',
    'font-weight:500',
    'line-height:18px',
    'white-space:nowrap',
  ].join(';');
  return badge;
}

function removeBadge() {
  document.getElementById(BADGE_ID)?.remove();
  removePopover();
}

async function fetchStarIntegrity(repo: GitHubRepo): Promise<StarIntegrityResponse> {
  const response = await fetch(
    `${API_BASE_URL}/repos/${encodeURIComponent(repo.owner)}/${encodeURIComponent(repo.repo)}/star-integrity`,
    { headers: { Accept: 'application/json' } },
  );
  if (!response.ok) {
    throw new Error(`StarScout API returned ${response.status}`);
  }
  return response.json();
}

function formatBadgeText(result: StarIntegrityResponse): string {
  if (!result.analyzed || result.suspectedNonLegitPercent === null) {
    return 'StarScout: not analyzed';
  }

  return `StarScout: ${result.suspectedNonLegitPercent}% suspected`;
}

function togglePopover(anchor: HTMLElement, result: StarIntegrityResponse) {
  const existing = document.getElementById(POPOVER_ID);
  if (existing) {
    existing.remove();
    return;
  }

  const popover = createPopover(result);
  document.body.append(popover);

  const rect = anchor.getBoundingClientRect();
  popover.style.top = `${Math.round(rect.bottom + window.scrollY + 8)}px`;
  popover.style.left = `${Math.round(rect.left + window.scrollX)}px`;
}

function createPopover(result: StarIntegrityResponse): HTMLDivElement {
  const popover = document.createElement('div');
  popover.id = POPOVER_ID;
  popover.style.cssText = [
    'position:absolute',
    'z-index:2147483647',
    'width:320px',
    'padding:12px',
    'border:1px solid var(--borderColor-default, #d0d7de)',
    'border-radius:8px',
    'background:var(--bgColor-default, #ffffff)',
    'box-shadow:0 8px 24px rgba(140,149,159,0.2)',
    'color:var(--fgColor-default, #24292f)',
    'font:13px/1.4 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif',
  ].join(';');
  popover.addEventListener('click', (event) => event.stopPropagation());
  popover.innerHTML = result.analyzed ? analyzedPopoverHtml(result) : notAnalyzedPopoverHtml(result);

  setTimeout(() => {
    document.addEventListener('click', removePopover, { once: true });
  }, 0);
  return popover;
}

function analyzedPopoverHtml(result: StarIntegrityResponse): string {
  const breakdown = result.breakdown;
  return `
    <strong style="display:block;margin-bottom:8px;">StarScout integrity signal</strong>
    <p style="margin:0 0 10px;color:var(--fgColor-muted, #57606a);">
      Heuristic signal only. Results may include false positives and are not proof that
      any star or account is fake.
    </p>
    ${metricRows([
      ['Current stars', formatNullableNumber(result.currentStars)],
      ['Suspected non-legit stars', formatNullableNumber(result.suspectedNonLegitStars)],
      ['Estimated legitimate stars', formatNullableNumber(result.estimatedLegitStars)],
      ['Suspected percentage', `${result.suspectedNonLegitPercent ?? 0}%`],
      ['Low-activity', formatNullableNumber(breakdown?.lowActivity ?? null)],
      ['Lockstep', formatNullableNumber(breakdown?.lockstep ?? null)],
      ['Overlap', formatNullableNumber(breakdown?.overlap ?? null)],
      ['Analyzed through', escapeHtml(result.analyzedThrough ?? 'unknown')],
    ])}
    ${warningsHtml(result.warnings)}
    ${attributionHtml()}
  `;
}

function notAnalyzedPopoverHtml(result: StarIntegrityResponse): string {
  return `
    <strong style="display:block;margin-bottom:8px;">StarScout integrity signal</strong>
    <p style="margin:0 0 10px;color:var(--fgColor-muted, #57606a);">
      This repository is not present in the current StarScout aggregate dataset. That is
      not a claim of zero suspected non-legit stars.
    </p>
    ${warningsHtml(result.warnings)}
    ${attributionHtml()}
  `;
}

function metricRows(rows: [string, string][]): string {
  return `
    <dl style="display:grid;grid-template-columns:1fr auto;gap:6px 12px;margin:0 0 10px;">
      ${rows
        .map(
          ([label, value]) => `
            <dt style="color:var(--fgColor-muted, #57606a);">${escapeHtml(label)}</dt>
            <dd style="margin:0;font-weight:600;">${value}</dd>
          `,
        )
        .join('')}
    </dl>
  `;
}

function warningsHtml(warnings: string[]): string {
  if (warnings.length === 0) {
    return '';
  }

  return `
    <div style="margin:10px 0;padding:8px;border-radius:6px;background:#fff8c5;color:#7d4e00;">
      ${warnings.map((warning) => `<div>${escapeHtml(warning)}</div>`).join('')}
    </div>
  `;
}

function attributionHtml(): string {
  return `
    <p style="margin:10px 0 0;color:var(--fgColor-muted, #57606a);font-size:12px;">
      Data and methodology attribution: StarScout, ICSE 2026 paper, and Zenodo DOI
      <a href="https://doi.org/10.5281/zenodo.17009694" target="_blank" rel="noreferrer">10.5281/zenodo.17009694</a>.
    </p>
  `;
}

function formatNullableNumber(value: number | null): string {
  return value === null ? 'unknown' : value.toLocaleString();
}

function escapeHtml(value: string): string {
  return value.replace(/[&<>"]/g, (char) => {
    const entities: Record<string, string> = {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
    };
    return entities[char];
  });
}

function removePopover() {
  document.getElementById(POPOVER_ID)?.remove();
}
