#!/usr/bin/env python3
"""
GitGhost v14.0 - Multi-Repo Organization Scanner
Scans entire GitHub organizations or multiple repositories
Generates comparative security scorecards
"""

import subprocess
import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import tempfile
import shutil

class OrgScanner:
    def __init__(self, github_token=None):
        self.github_token = github_token
        self.results = {}
        
    def get_org_repos(self, org_name):
        """Fetch all repositories for an organization using GitHub API"""
        if not self.github_token:
            print("[!] GitHub token required for org scanning")
            return []
        
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        repos = []
        page = 1
        
        while True:
            url = f'https://api.github.com/orgs/{org_name}/repos?page={page}&per_page=100'
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                print(f"[!] Error fetching repos: {response.status_code}")
                break
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend([{
                'name': r['name'],
                'clone_url': r['clone_url'],
                'private': r['private'],
                'size': r['size'],
                'updated_at': r['updated_at']
            } for r in page_repos])
            
            page += 1
        
        return repos
    
    def clone_repo(self, repo_url, dest_dir):
        """Clone a repository for scanning"""
        try:
            # Add token to URL if available
            if self.github_token and 'github.com' in repo_url:
                repo_url = repo_url.replace('https://', f'https://{self.github_token}@')
            
            result = subprocess.run(
                ['git', 'clone', '--quiet', repo_url, dest_dir],
                capture_output=True,
                timeout=300
            )
            return result.returncode == 0
        except Exception as e:
            print(f"[!] Clone failed: {e}")
            return False
    
    def scan_single_repo(self, repo_info, temp_base_dir):
        """Scan a single repository"""
        repo_name = repo_info['name']
        print(f"[*] Scanning: {repo_name}")
        
        # Create temp directory for this repo
        repo_dir = os.path.join(temp_base_dir, repo_name)
        os.makedirs(repo_dir, exist_ok=True)
        
        try:
            # Clone repository
            if not self.clone_repo(repo_info['clone_url'], repo_dir):
                return {
                    'repo': repo_name,
                    'status': 'clone_failed',
                    'findings': []
                }
            
            # Run GitGhost scan
            from gitghost_core_v14 import scan_repo
            
            findings = scan_repo(repo_dir, since_days=365, use_cache=False)
            
            # Calculate metrics
            critical = sum(1 for f in findings if f['risk'] == 'CRITICAL')
            high = sum(1 for f in findings if f['risk'] == 'HIGH')
            medium = sum(1 for f in findings if f['risk'] == 'MEDIUM')
            
            avg_cvss = sum(f['cvss_score'] for f in findings) / len(findings) if findings else 0
            
            # Security score (0-100)
            security_score = max(0, 100 - (critical * 15 + high * 5 + medium * 1))
            
            return {
                'repo': repo_name,
                'status': 'success',
                'findings': findings,
                'metrics': {
                    'total': len(findings),
                    'critical': critical,
                    'high': high,
                    'medium': medium,
                    'avg_cvss': round(avg_cvss, 2),
                    'security_score': security_score
                },
                'updated_at': repo_info['updated_at']
            }
            
        except Exception as e:
            print(f"[!] Error scanning {repo_name}: {e}")
            return {
                'repo': repo_name,
                'status': 'scan_failed',
                'error': str(e),
                'findings': []
            }
        finally:
            # Cleanup
            try:
                shutil.rmtree(repo_dir)
            except:
                pass
    
    def scan_organization(self, org_name, max_repos=None, max_workers=3):
        """Scan all repositories in an organization"""
        print(f"[*] GitGhost v14.0 - Organization Scanner")
        print(f"[*] Target: {org_name}")
        
        # Get all repos
        repos = self.get_org_repos(org_name)
        
        if not repos:
            print("[!] No repositories found")
            return
        
        print(f"[*] Found {len(repos)} repositories")
        
        if max_repos:
            repos = repos[:max_repos]
            print(f"[*] Limiting to {max_repos} repos")
        
        # Create temp base directory
        temp_base_dir = tempfile.mkdtemp(prefix='gitghost_org_')
        
        try:
            # Scan repos in parallel
            results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.scan_single_repo, repo, temp_base_dir): repo
                    for repo in repos
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
            
            # Generate scorecard
            self.generate_scorecard(org_name, results)
            
            # Save detailed results
            output_file = f'gitghost_org_{org_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n[*] Scan complete!")
            print(f"[*] Results saved to: {output_file}")
            
            return results
            
        finally:
            # Cleanup temp directory
            try:
                shutil.rmtree(temp_base_dir)
            except:
                pass
    
    def generate_scorecard(self, org_name, results):
        """Generate security scorecard for the organization"""
        print("\n" + "="*80)
        print(f"SECURITY SCORECARD: {org_name}")
        print("="*80)
        
        # Overall stats
        total_findings = sum(len(r.get('findings', [])) for r in results)
        total_critical = sum(r.get('metrics', {}).get('critical', 0) for r in results)
        total_high = sum(r.get('metrics', {}).get('high', 0) for r in results)
        
        print(f"\n📊 ORGANIZATION OVERVIEW")
        print(f"  Total Repositories Scanned: {len(results)}")
        print(f"  Total Security Findings: {total_findings}")
        print(f"  Critical: {total_critical}")
        print(f"  High: {total_high}")
        
        # Top 10 riskiest repos
        successful_scans = [r for r in results if r['status'] == 'success']
        sorted_repos = sorted(
            successful_scans,
            key=lambda x: x['metrics']['security_score']
        )
        
        print(f"\n🔴 TOP 10 RISKIEST REPOSITORIES")
        print(f"{'Rank':<6} {'Repository':<40} {'Score':<8} {'Critical':<10} {'High':<10}")
        print("-" * 80)
        
        for i, repo in enumerate(sorted_repos[:10], 1):
            metrics = repo['metrics']
            print(f"{i:<6} {repo['repo']:<40} {metrics['security_score']:<8} "
                  f"{metrics['critical']:<10} {metrics['high']:<10}")
        
        # Repos with no issues
        clean_repos = [r for r in successful_scans if r['metrics']['total'] == 0]
        if clean_repos:
            print(f"\n✅ CLEAN REPOSITORIES ({len(clean_repos)})")
            for repo in clean_repos[:5]:
                print(f"  - {repo['repo']}")
        
        # Failed scans
        failed = [r for r in results if r['status'] != 'success']
        if failed:
            print(f"\n⚠️  FAILED SCANS ({len(failed)})")
            for repo in failed:
                print(f"  - {repo['repo']}: {repo['status']}")
        
        print("\n" + "="*80)

def scan_repo_list(repo_file, output_dir='./gitghost_multi_scan'):
    """Scan multiple repositories from a file"""
    print("[*] GitGhost v14.0 - Multi-Repo Scanner")
    
    # Read repo list
    with open(repo_file, 'r') as f:
        repos = [line.strip() for line in f if line.strip()]
    
    print(f"[*] Found {len(repos)} repositories to scan")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    
    for repo_url in repos:
        repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        print(f"\n[*] Scanning: {repo_name}")
        
        # Clone to temp directory
        temp_dir = tempfile.mkdtemp(prefix='gitghost_')
        
        try:
            # Clone
            result = subprocess.run(
                ['git', 'clone', '--quiet', repo_url, temp_dir],
                capture_output=True,
                timeout=300
            )
            
            if result.returncode != 0:
                print(f"[!] Clone failed for {repo_name}")
                results.append({
                    'repo': repo_name,
                    'status': 'clone_failed'
                })
                continue
            
            # Scan
            from gitghost_core_v14 import scan_repo
            findings = scan_repo(temp_dir, since_days=365, use_cache=False)
            
            # Save individual report
            repo_output = os.path.join(output_dir, f'{repo_name}_report.json')
            with open(repo_output, 'w') as f:
                json.dump(findings, f, indent=2)
            
            results.append({
                'repo': repo_name,
                'status': 'success',
                'findings_count': len(findings),
                'report_file': repo_output
            })
            
        except Exception as e:
            print(f"[!] Error: {e}")
            results.append({
                'repo': repo_name,
                'status': 'error',
                'error': str(e)
            })
        finally:
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except:
                pass
    
    # Summary
    print("\n" + "="*80)
    print("SCAN SUMMARY")
    print("="*80)
    print(f"Total repositories: {len(repos)}")
    print(f"Successful scans: {sum(1 for r in results if r['status'] == 'success')}")
    print(f"Failed scans: {sum(1 for r in results if r['status'] != 'success')}")
    print(f"Results saved to: {output_dir}/")
    
    return results

def main():
    parser = argparse.ArgumentParser(
        description="GitGhost v14.0 - Multi-Repository Scanner"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Scan mode')
    
    # Organization scanner
    org_parser = subparsers.add_parser('org', help='Scan GitHub organization')
    org_parser.add_argument('org_name', help='Organization name')
    org_parser.add_argument('--token', required=True, help='GitHub API token')
    org_parser.add_argument('--max-repos', type=int, help='Limit number of repos')
    org_parser.add_argument('--workers', type=int, default=3, help='Parallel workers')
    
    # List scanner
    list_parser = subparsers.add_parser('list', help='Scan from repo list file')
    list_parser.add_argument('repo_file', help='File with repository URLs')
    list_parser.add_argument('--output', default='./gitghost_multi_scan', 
                           help='Output directory')
    
    args = parser.parse_args()
    
    if args.command == 'org':
        scanner = OrgScanner(github_token=args.token)
        scanner.scan_organization(
            args.org_name,
            max_repos=args.max_repos,
            max_workers=args.workers
        )
    
    elif args.command == 'list':
        scan_repo_list(args.repo_file, args.output)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
