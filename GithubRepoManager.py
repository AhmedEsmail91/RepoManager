import requests
class GitHubRepoManager:
    def __init__(self, token, username):
        self.token = token
        self.username = username
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        self.repos = []

    def fetch_repos(self):
        print("Fetching repositories...")
        repos = []
        page = 1
        per_page = 100
        while True:
            url = f"https://api.github.com/user/repos?visibility=all&per_page={per_page}&page={page}"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Failed to fetch repos: {response.status_code} - {response.text}")
                break
            page_data = response.json()
            if not page_data:
                break
            repos.extend(page_data)
            page += 1
        self.repos = sorted(repos, key=lambda r: not r["private"])
        print(f"✅ Total repositories fetched: {len(self.repos)}")

    def show_repos(self, show_description=True, show_private=True, limit=None):
        if not self.repos:
            print("No repositories to show. Please fetch first.")
            return None
        import pandas as pd
        data = []
        for idx, repo in enumerate(self.repos):
            row = {
                'Index': idx,
                'Full Name': repo['full_name']
            }
            if show_private:
                row['Private'] = repo['private']
            if show_description:
                row['Description'] = repo['description'] if repo['description'] else ""
            data.append(row)
        df = pd.DataFrame(data)
        if limit is not None:
            df_show = df.head(limit)
        display(df_show)
        return df

    def delete_repos_by_index(self, indices, confirm=False):
        if not self.repos:
            print("No repositories loaded. Please fetch first.")
            return
        for idx in indices:
            if idx < 0 or idx >= len(self.repos):
                print(f"❌ Invalid index: {idx}")
                continue
            full_name = self.repos[idx]['full_name']
            if confirm:
                user_input = input(f"Are you sure you want to delete {full_name}? (y/N): ")
                if user_input.lower() != 'y':
                    print(f"Skipped: {full_name}")
                    continue
            url = f"https://api.github.com/repos/{full_name}"
            try:
                response = requests.delete(url, headers=self.headers)
                if response.status_code == 204:
                    print(f"✅ Deleted: {full_name}")
                else:
                    print(f"❌ Failed to delete {full_name} — {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Exception while deleting {full_name}: {e}")
