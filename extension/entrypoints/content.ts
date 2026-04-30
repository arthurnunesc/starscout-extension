const API_BASE_URL = import.meta.env.WXT_PUBLIC_STARSCOUT_API_BASE_URL ?? 'http://127.0.0.1:8000';
const BADGE_ID = 'starscout-integrity-badge';
const POPOVER_ID = 'starscout-integrity-popover';

export default defineContentScript({
  matches: ['https://github.com/*/*'],
  main() {
    console.info('[StarScout] content script loaded', window.location.href);
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

type BadgePlacement =
  | { mode: 'desktop-border-grid'; starStat: HTMLElement }
  | { mode: 'mobile-responsive-meta'; container: HTMLElement; repo: GitHubRepo };

function installBadgeUpdater() {
  let lastUrl = '';
  let retryTimer: number | undefined;

  const update = () => {
    const repo = parseGitHubRepo(window.location);
    if (lastUrl === window.location.href && (!repo || document.getElementById(BADGE_ID))) {
      return;
    }

    lastUrl = window.location.href;
    window.clearTimeout(retryTimer);
    retryTimer = window.setTimeout(() => void refreshBadge(), 150);
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
    console.debug('[StarScout] not a supported repository page', window.location.href);
    return;
  }

  const placement = findBadgePlacement(repo);
  if (!placement) {
    console.debug('[StarScout] badge anchor not found yet', repo);
    return;
  }

  const badge = insertBadge(placement, 'StarScout checking');

  try {
    const result = await fetchStarIntegrity(repo);
    console.info('[StarScout] API response received', result);
    setBadgeExpanded(badge, result, true);
    badge.title = 'Heuristic StarScout suspected non-legit star signal';
    badge.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
      const expanded = badge.dataset.expanded !== 'false';
      setBadgeExpanded(badge, result, !expanded);
      if (expanded) {
        removePopover();
        return;
      }
      togglePopover(badge, result);
    });
  } catch (error) {
    console.warn('[StarScout] API request failed', error);
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

function findBadgePlacement(repo: GitHubRepo): BadgePlacement | null {
  const responsiveMeta = findResponsiveMetaContainer();
  if (responsiveMeta && isVisible(responsiveMeta)) {
    return { mode: 'mobile-responsive-meta', container: responsiveMeta, repo };
  }

  const borderGridStarStat = findBorderGridStarStat(repo);
  if (borderGridStarStat) {
    return { mode: 'desktop-border-grid', starStat: borderGridStarStat };
  }

  const sidebarStarStat = findSidebarStarStat(repo);
  if (sidebarStarStat) {
    return { mode: 'desktop-border-grid', starStat: sidebarStarStat };
  }

  return null;
}

function findResponsiveMetaContainer(): HTMLElement | null {
  return (
    document.querySelector<HTMLElement>('ul[aria-label="Repository details"]') ??
    document.querySelector<HTMLElement>('.responsive-meta-container')
  );
}

function findBorderGridStarStat(repo: GitHubRepo): HTMLElement | null {
  const borderGridRows = document.querySelectorAll<HTMLElement>('.BorderGrid-row');
  for (const row of borderGridRows) {
    const starLink = row.querySelector<HTMLElement>(`a[href="/${repo.owner}/${repo.repo}/stargazers"]`);
    const stat = starLink?.closest<HTMLElement>('.mt-2, li, div');
    if (stat) {
      return stat;
    }
  }

  return null;
}

function findSidebarStarStat(repo: GitHubRepo): HTMLElement | null {
  const links = document.querySelectorAll<HTMLElement>(
    `a[href="/${repo.owner}/${repo.repo}/stargazers"]`,
  );

  for (const link of links) {
    const stat = link.closest<HTMLElement>('.mt-2');
    if (stat && !stat.closest('#repository-details-container')) {
      return stat;
    }
  }

  return null;
}

function isVisible(element: HTMLElement): boolean {
  return !!(element.offsetWidth || element.offsetHeight || element.getClientRects().length);
}

function insertBadge(placement: BadgePlacement, text: string): HTMLElement {
  if (placement.mode === 'desktop-border-grid') {
    const container = document.createElement('div');
    container.id = BADGE_ID;
    container.className = 'mt-2';
    const badge = createDesktopBadge(text);
    badge.dataset.mode = 'desktop';
    container.append(badge);
    placement.starStat.insertAdjacentElement('afterend', container);
    return badge;
  }

  // Mobile: create <a> matching GitHub stat link styling with icon + bold value + label
  const badge = document.createElement('a');
  badge.id = BADGE_ID;
  badge.className = 'Link--secondary no-underline d-block mr-2';
  badge.dataset.mode = 'mobile';
  badge.role = 'listitem';
  badge.href = '#';

  // Search icon SVG
  badge.innerHTML = `<svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-search mr-1 tmp-mr-1">
    <path d="M10.68 11.74a6 6 0 0 1-7.922-8.982 6 6 0 0 1 8.982 7.922l3.04 3.04a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215ZM11.5 7a4.499 4.499 0 1 0-8.997 0A4.499 4.499 0 0 0 11.5 7Z"></path>
  </svg>`;

  // Split text into bold part and rest
  const match = text.match(/^(.+?)\s+-\s+(.+)$/);
  if (match) {
    const boldPart = document.createElement('span');
    boldPart.className = 'text-bold color-fg-default';
    boldPart.textContent = match[1];
    badge.append(boldPart, ` - ${match[2]}`);
  } else {
    badge.append(text);
  }

  // Insert between Stars and Forks
  const starsLink = placement.container.querySelector<HTMLElement>(
    `a[href="/${placement.repo.owner}/${placement.repo.repo}/stargazers"]`,
  );
  if (starsLink) {
    starsLink.insertAdjacentElement('afterend', badge);
  } else {
    placement.container.append(badge);
  }

  return badge;
}

function createDesktopBadge(text: string): HTMLAnchorElement {
  const badge = document.createElement('a');
  badge.setAttribute('data-view-component', 'true');
  badge.className = 'Link Link--muted';
  badge.href = '#';

  // Search icon SVG
  badge.innerHTML = `<svg aria-hidden="true" height="16" viewBox="0 0 16 16" version="1.1" width="16" data-view-component="true" class="octicon octicon-search mr-2 tmp-mr-2">
    <path d="M10.68 11.74a6 6 0 0 1-7.922-8.982 6 6 0 0 1 8.982 7.922l3.04 3.04a.749.749 0 0 1-.326 1.275.749.749 0 0 1-.734-.215ZM11.5 7a4.499 4.499 0 1 0-8.997 0A4.499 4.499 0 0 0 11.5 7Z"></path>
  </svg>`;

  // Split text into bold part and rest
  const match = text.match(/^(.+?)\s+-\s+(.+)$/);
  if (match) {
    const boldPart = document.createElement('strong');
    boldPart.textContent = match[1];
    badge.append(boldPart, ` ${match[2]}`);
  } else {
    badge.append(text);
  }

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
    return 'Not analyzed - StarScout';
  }

  return `${result.suspectedNonLegitPercent}% suspected - StarScout`;
}

function formatCollapsedBadgeText(result: StarIntegrityResponse): string {
  if (!result.analyzed || result.suspectedNonLegitPercent === null) {
    return 'NA - SS';
  }

  return `${result.suspectedNonLegitPercent}% - SS`;
}

function setBadgeExpanded(
  badge: HTMLElement,
  result: StarIntegrityResponse,
  expanded: boolean,
) {
  badge.dataset.expanded = String(expanded);
  badge.setAttribute('aria-expanded', String(expanded));
  const text = expanded ? formatBadgeText(result) : formatCollapsedBadgeText(result);

  // Check layout mode from data attribute
  const mode = badge.dataset.mode;

  if (mode === 'desktop') {
    // Desktop: keep SVG, update strong and text
    const svg = badge.querySelector('svg');
    badge.innerHTML = '';
    if (svg) badge.append(svg);
    const match = text.match(/^(.+?)\s+-\s+(.+)$/);
    if (match) {
      const strong = document.createElement('strong');
      strong.textContent = match[1];
      badge.append(strong, ` ${match[2]}`);
    } else {
      badge.append(text);
    }
  } else if (mode === 'mobile') {
    // Mobile: preserve SVG, update with bold span
    const svg = badge.querySelector('svg');
    badge.innerHTML = '';
    if (svg) badge.append(svg);
    const match = text.match(/^(.+?)\s+-\s+(.+)$/);
    if (match) {
      const boldPart = document.createElement('span');
      boldPart.className = 'text-bold color-fg-default';
      boldPart.textContent = match[1];
badge.append(boldPart, ` - ${match[2]}`);
    } else {
      badge.append(text);
    }
  } else {
    // Fallback
    badge.textContent = text;
  }
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
