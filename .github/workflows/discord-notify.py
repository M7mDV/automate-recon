#!/usr/bin/env python3
import os
import requests
import glob

def send_to_discord(webhook, results_dir="recon_output"):
    if not webhook:
        print("[!] DISCORD_WEBHOOK not set")
        return False
    
    # Summary stats
    summary = {"total": 0, "alive": 0, "files": []}
    
    for file in glob.glob(f"{results_dir}/*.txt"):
        size = os.path.getsize(file)
        if size > 0:
            summary["files"].append(os.path.basename(file))
            if "AllSubs" in file:
                with open(file) as f:
                    summary["total"] = len(f.readlines())
            elif "httpx" in file:
                with open(file) as f:
                    summary["alive"] = len(f.readlines())
    
    # Send message
    message = {
        "username": "Recon Bot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        "embeds": [{
            "title": "🔍 Recon Pipeline Complete",
            "color": 3447003,
            "fields": [
                {"name": "📊 Total Subdomains", "value": str(summary["total"]), "inline": True},
                {"name": "🌐 Alive Hosts", "value": str(summary["alive"]), "inline": True},
                {"name": "📁 Files Generated", "value": "\n".join(summary["files"]) or "None", "inline": False}
            ]
        }]
    }
    
    resp = requests.post(webhook, json=message)
    print(f"[+] Discord notification sent: {resp.status_code}")
    
    # Upload files
    for file in glob.glob(f"{results_dir}/*.txt"):
        if os.path.getsize(file) > 0 and os.path.getsize(file) < 8 * 1024 * 1024:  # < 8MB
            with open(file, 'rb') as f:
                files = {'file': (os.path.basename(file), f)}
                resp = requests.post(webhook, files=files)
                print(f"[+] Uploaded {file}: {resp.status_code}")
    
    return True

if __name__ == "__main__":
    webhook = os.environ.get('DISCORD_WEBHOOK")
    send_to_discord(webhook)
