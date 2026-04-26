const API_BASE_URL = 'http://127.0.0.1:8000';
const BADGE_ID = 'starscout-integrity-badge';

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
  analyzed: boolean;
  suspectedNonLegitPercent: number | null;
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

function createBadge(text: string): HTMLSpanElement {
  const badge = document.createElement('span');
  badge.id = BADGE_ID;
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
    'font-size:12px',
    'font-weight:500',
    'line-height:18px',
    'white-space:nowrap',
  ].join(';');
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
    return 'StarScout: not analyzed';
  }

  return `StarScout: ${result.suspectedNonLegitPercent}% suspected`;
}
