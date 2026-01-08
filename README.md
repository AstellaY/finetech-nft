# finetech-nft — Simple XRPL Streamlit Demo

This is a minimal Python-only web app demonstrating XRPL testnet interactions using `streamlit` and `xrpl-py`.

## Prerequisites
- macOS or Linux or Windows
- Python 3.10+ (or 3.8+)
- `git` installed

## Quick setup
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app locally with Streamlit:

```bash
streamlit run app.py
```

Open the URL Streamlit shows (usually http://localhost:8501).

## Git & GitHub (initial push)
If this folder is not yet a git repo:

```bash
git init
git add .
git commit -m "Initial commit: simple XRPL Streamlit app"
```

Create a GitHub repo via the website, or using GitHub CLI:

```bash
# using GitHub CLI (optional)
gh repo create your-username/finetech-nft --public --source=. --remote=origin
git push -u origin main
```

If you created the repo on GitHub.com, follow the remote setup instructions they provide, then:

```bash
git remote add origin <your-remote-url>
git push -u origin main
```

## Collaboration workflow (recommended)
- Create a feature branch: `git checkout -b feat/my-change`
- Make changes and commit frequently.
- Push the branch: `git push -u origin feat/my-change`
- Open a Pull Request on GitHub and request review from your teammate.

## What I implemented here
- `app.py`: Streamlit frontend to generate a testnet wallet and check balances.
- `xrpl_utils.py`: helpers to connect to XRPL, generate a faucet wallet, and read balances.

If you want, I can:
- Initialize or fix the local git history and push to GitHub for you.
- Add NFT minting flows and example transactions.
