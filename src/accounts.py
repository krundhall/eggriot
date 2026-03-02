import os
import json
from riot_api import get_puuid_by_riot_id

ACCOUNTS_FILE = "../accounts.json"

def load_accounts():
    """Load accounts from JSON"""
    if os.path.exists(ACCOUNTS_FILE):
        with open(ACCOUNTS_FILE, 'r') as file:
            content = file.read().strip()
            if content:
                return json.loads(content)
    return []

def save_accounts(accounts):
    """Save accounts to JSON"""
    with open(ACCOUNTS_FILE, 'w') as file:
        json.dump(accounts, file, indent=2)

def account_exists(name: str, tag: str):
    """Check if account is in JSON"""
    accounts = load_accounts()
    for account in accounts:
        if account['gameName'] == name and account['tagLine'] == tag:
            return account
    return None

def add_account(name: str, tag: str):
    """Add new account to JSON by fetching PUUID from Riot API"""
    existing_account = account_exists(name, tag)
    if existing_account:
        print(f"Account already exists: {name}#{tag}")
        return existing_account

    account_data = get_puuid_by_riot_id(name, tag)

    if not account_data:
        print(f"Failed to fetch account data for {name}#{tag}")
        return None

    # Add to accounts.json
    accounts = load_accounts()
    accounts.append(account_data)
    save_accounts(accounts)

    print(f"Added account: {name}#{tag}")
    return account_data

def list_accounts():
    """List of all stored accounts"""
    accounts = load_accounts()
    if not accounts:
        print("No account blyat")
        return

    print("\n=== Stored Accounts ===")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. {account['gameName']}#{account['tagLine']}")
    print()
