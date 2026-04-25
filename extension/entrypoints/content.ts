export default defineContentScript({
  matches: ['https://github.com/*/*'],
  main() {
    const repo = parseGitHubRepo(window.location);

    if (!repo) {
      return;
    }

    console.info('StarScout extension detected repository page', repo);
  },
});

type GitHubRepo = {
  owner: string;
  repo: string;
};

function parseGitHubRepo(location: Location): GitHubRepo | null {
  if (location.hostname !== 'github.com') {
    return null;
  }

  const [owner, repo, ...rest] = location.pathname.split('/').filter(Boolean);

  if (!owner || !repo || rest.length > 0) {
    return null;
  }

  return { owner, repo };
}
