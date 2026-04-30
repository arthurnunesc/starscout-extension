const API_BASE_URL = import.meta.env.WXT_PUBLIC_STARSCOUT_API_BASE_URL ?? 'http://127.0.0.1:8000';
const BADGE_ID = 'starscout-integrity-badge';

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
    updateBadgeText(badge, result);
    badge.title = 'Heuristic StarScout suspected non-legit star signal';
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

function updateBadgeText(badge: HTMLElement, result: StarIntegrityResponse) {
  const text = formatBadgeText(result);
  const mode = badge.dataset.mode;

  if (mode === 'desktop') {
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
    badge.textContent = text;
  }
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
