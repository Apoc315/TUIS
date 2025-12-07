#!/usr/bin/env python3
"""
Enhanced TikTok User Info Scraper
With colorful terminal menu and improved features
"""

import requests
import re
import argparse
import urllib.parse
import json
import sys
import os
from bs4 import BeautifulSoup
from datetime import datetime
import time

# ============================================
# COLOR MANAGEMENT
# ============================================
class Colors:
    """ANSI color codes for terminal output"""
    # Styles
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'
    HIDDEN = '\033[8m'
    
    # Colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    DEFAULT = '\033[39m'
    
    # Backgrounds
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    BG_DEFAULT = '\033[49m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Bright backgrounds
    BG_BRIGHT_BLACK = '\033[100m'
    BG_BRIGHT_RED = '\033[101m'
    BG_BRIGHT_GREEN = '\033[102m'
    BG_BRIGHT_YELLOW = '\033[103m'
    BG_BRIGHT_BLUE = '\033[104m'
    BG_BRIGHT_MAGENTA = '\033[105m'
    BG_BRIGHT_CYAN = '\033[106m'
    BG_BRIGHT_WHITE = '\033[107m'

# Short aliases for convenience
C = Colors

# ============================================
# TERMINAL UTILITIES
# ============================================
def clear_screen():
    """Clear terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print application header"""
    clear_screen()
    print(f"{C.BRIGHT_CYAN}{'='*60}{C.RESET}")
    print(f"{C.BRIGHT_MAGENTA}{C.BOLD}TIKTOK USER INFO SCRAPER{C.RESET}")
    print(f"{C.BRIGHT_CYAN}{'='*60}{C.RESET}")
    print(f"{C.DIM}Version 2.0 | Enhanced with Terminal Menu | No API Required{C.RESET}\n")

def print_menu():
    """Print main menu"""
    print(f"{C.BRIGHT_YELLOW}{C.BOLD}MAIN MENU{C.RESET}")
    print(f"{C.CYAN}{'─'*40}{C.RESET}")
    print(f"{C.GREEN}[1]{C.RESET} {C.BOLD}Scrape by Username{C.RESET}")
    print(f"{C.GREEN}[2]{C.RESET} {C.BOLD}Scrape by User ID{C.RESET}")
    print(f"{C.GREEN}[3]{C.RESET} {C.BOLD}Scrape Multiple Users (from file){C.RESET}")
    print(f"{C.GREEN}[4]{C.RESET} {C.BOLD}Batch Download Profile Pictures{C.RESET}")
    print(f"{C.GREEN}[5]{C.RESET} {C.BOLD}Export Data to JSON{C.RESET}")
    print(f"{C.GREEN}[6]{C.RESET} {C.BOLD}Settings (Colors/Theme){C.RESET}")
    print(f"{C.RED}[0]{C.RESET} {C.BOLD}Exit{C.RESET}")
    print(f"{C.CYAN}{'─'*40}{C.RESET}")

def print_banner():
    """Print ASCII art banner"""
    banner = f"""
{C.BRIGHT_MAGENTA}╔══════════════════════════════════════════════════════════╗
║{C.BRIGHT_CYAN}      _____ _ _      _          _   _               {C.BRIGHT_MAGENTA}║
║{C.BRIGHT_CYAN}     |_   _(_) | ___| | _____  | | | | ___  _   _   {C.BRIGHT_MAGENTA}║
║{C.BRIGHT_CYAN}       | | | | |/ __| |/ / _ \ | |_| |/ _ \| | | |  {C.BRIGHT_MAGENTA}║
║{C.BRIGHT_CYAN}       | | | | | (__|   <  __/ |  _  | (_) | |_| |  {C.BRIGHT_MAGENTA}║
║{C.BRIGHT_CYAN}       |_| |_|_|\___|_|\_\___| |_| |_|\___/ \__,_|  {C.BRIGHT_MAGENTA}║
║                                                            {C.BRIGHT_MAGENTA}║
║{C.BRIGHT_GREEN}          Enhanced Terminal Version 2.0             {C.BRIGHT_MAGENTA}║
╚══════════════════════════════════════════════════════════╝{C.RESET}
    """
    print(banner)

def print_colored(text, color=C.WHITE, style=C.RESET):
    """Print colored text with optional style"""
    return f"{style}{color}{text}{C.RESET}"

def progress_bar(iteration, total, prefix='', suffix='', length=50, fill='█'):
    """Display progress bar"""
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '─' * (length - filled_length)
    print(f'\r{prefix} |{C.BRIGHT_CYAN}{bar}{C.RESET}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

# ============================================
# TIKTOK SCRAPER CLASS
# ============================================
class TikTokScraper:
    def __init__(self, use_colors=True):
        self.use_colors = use_colors
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
    def colorize(self, text, color_code):
        """Apply color if enabled"""
        if self.use_colors:
            return f"{color_code}{text}{C.RESET}"
        return text
    
    def fetch_user_info(self, identifier, by_id=False):
        """Fetch user information from TikTok"""
        start_time = time.time()
        
        # Clean identifier
        if not by_id and identifier.startswith('@'):
            identifier = identifier[1:]
        
        url = f"https://www.tiktok.com/@{identifier}" if not by_id else f"https://www.tiktok.com/@user{identifier}"
        
        try:
            print(f"\n{self.colorize('🌐', C.BRIGHT_CYAN)} {self.colorize('Fetching data from TikTok...', C.CYAN)}")
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                return {"error": f"Failed to fetch user (Status: {response.status_code})"}
            
            # Parse HTML
            try:
                soup = BeautifulSoup(response.text, 'lxml')
            except:
                soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract data
            user_data = self._extract_data(response.text)
            
            if "error" in user_data:
                return user_data
            
            # Calculate fetch time
            fetch_time = time.time() - start_time
            
            # Add metadata
            user_data['fetch_time'] = f"{fetch_time:.2f}s"
            user_data['timestamp'] = datetime.now().isoformat()
            user_data['url'] = url
            
            return user_data
            
        except requests.RequestException as e:
            return {"error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def _extract_data(self, html_content):
        """Extract user data from HTML"""
        patterns = {
            'user_id': r'"webapp\.user-detail"[^}]*"id":"(\d+)"',
            'unique_id': r'"uniqueId":"([^"]+)"',
            'nickname': r'"nickname":"([^"]+)"',
            'followers': r'"followerCount":(\d+)',
            'following': r'"followingCount":(\d+)',
            'likes': r'"heartCount":(\d+)',
            'videos': r'"videoCount":(\d+)',
            'signature': r'"signature":"([^"]*?)"',
            'verified': r'"verified":(true|false)',
            'secUid': r'"secUid":"([^"]+)"',
            'privateAccount': r'"privateAccount":(true|false)',
            'region': r'"region":"([^"]*)"',
            'diggCount': r'"diggCount":(\d+)',
            'friendCount': r'"friendCount":(\d+)',
            'avatarLarger': r'"avatarLarger":"([^"]+)"',
            'createTime': r'"createTime":(\d+)',
        }
        
        info = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, html_content)
            if match:
                info[key] = match.group(1)
            else:
                # Try alternative patterns
                alt_patterns = {
                    'user_id': r'"userId":"(\d+)"',
                    'unique_id': r'"uniqueId":"([^"]+)"',
                    'nickname': r'"nickName":"([^"]+)"',
                }
                if key in alt_patterns:
                    alt_match = re.search(alt_patterns[key], html_content)
                    info[key] = alt_match.group(1) if alt_match else "N/A"
                else:
                    info[key] = "N/A"
        
        # Clean up data
        info['signature'] = info.get('signature', '').replace('\\n', '\n').replace('\\"', '"')
        
        # Extract social links
        info['social_links'] = self._extract_social_links(html_content, info.get('signature', ''))
        
        # Format numbers
        info['followers'] = self._format_number(info.get('followers', '0'))
        info['following'] = self._format_number(info.get('following', '0'))
        info['likes'] = self._format_number(info.get('likes', '0'))
        info['videos'] = self._format_number(info.get('videos', '0'))
        
        # Boolean conversions
        info['verified'] = info.get('verified', 'false').lower() == 'true'
        info['privateAccount'] = info.get('privateAccount', 'false').lower() == 'true'
        
        # Format creation date
        if info.get('createTime', '0') != 'N/A' and info['createTime'] != '0':
            try:
                create_date = datetime.fromtimestamp(int(info['createTime']))
                info['createTime'] = create_date.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        return info
    
    def _extract_social_links(self, html_content, bio):
        """Extract social links from HTML and bio"""
        social_links = []
        
        # Method 1: TikTok bio links
        link_patterns = [
            r'href="https://www\.tiktok\.com/link/v2\?[^"]*?target=([^"&]+)"',
            r'scene=bio_url[^"]*?target=([^"&]+)',
            r'"bioLink":{"link":"([^"]+)"',
            r'"shareUrl":"([^"]+)"',
        ]
        
        for pattern in link_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                try:
                    decoded = urllib.parse.unquote(match)
                    if decoded.startswith(('http://', 'https://', 'www.')):
                        if decoded not in social_links:
                            social_links.append(decoded)
                except:
                    pass
        
        # Method 2: Social media mentions in bio
        social_patterns = {
            'instagram': [r'[iI][gG][\s:]*@?([a-zA-Z0-9._]+)', r'instagram\.com/([a-zA-Z0-9._]+)'],
            'twitter': [r'[tT]witter[\s:]*@?([a-zA-Z0-9._]+)', r'twitter\.com/([a-zA-Z0-9._]+)', r'x\.com/([a-zA-Z0-9._]+)'],
            'youtube': [r'[yY][tT][\s:]*@?([a-zA-Z0-9._]+)', r'youtube\.com/([a-zA-Z0-9._]+)'],
            'snapchat': [r'[sS]napchat[\s:]*@?([a-zA-Z0-9._]+)', r'snapchat\.com/add/([a-zA-Z0-9._]+)'],
            'facebook': [r'[fF][bB][\s:]*@?([a-zA-Z0-9._]+)', r'facebook\.com/([a-zA-Z0-9._]+)'],
            'telegram': [r'[tT]elegram[\s:]*@?([a-zA-Z0-9._]+)', r't\.me/([a-zA-Z0-9._]+)'],
        }
        
        for platform, patterns in social_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, bio)
                if match:
                    username = match.group(1)
                    social_links.append(f"{platform}:{username}")
                    break
        
        # Method 3: Email addresses
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', bio)
        if email_match:
            social_links.append(f"email:{email_match.group(0)}")
        
        return list(set(social_links))[:10]  # Remove duplicates, limit to 10
    
    def _format_number(self, num_str):
        """Format large numbers with K, M, B suffixes"""
        try:
            num = int(num_str)
            if num >= 1000000000:
                return f"{num/1000000000:.1f}B"
            elif num >= 1000000:
                return f"{num/1000000:.1f}M"
            elif num >= 1000:
                return f"{num/1000:.1f}K"
            return str(num)
        except:
            return num_str
    
    def display_user_info(self, user_data):
        """Display user information in a beautiful format"""
        if "error" in user_data:
            print(f"\n{self.colorize('❌ ERROR', C.BRIGHT_RED)}: {self.colorize(user_data['error'], C.RED)}")
            return
        
        print(f"\n{self.colorize('='*60, C.BRIGHT_CYAN)}")
        print(f"{self.colorize('👤 TIKTOK USER PROFILE', C.BRIGHT_MAGENTA)}")
        print(f"{self.colorize('='*60, C.BRIGHT_CYAN)}")
        
        # Basic Info
        print(f"\n{self.colorize('📋 BASIC INFORMATION', C.BRIGHT_YELLOW)}")
        print(f"{self.colorize('─'*40, C.CYAN)}")
        print(f"{self.colorize('Username:', C.GREEN)} {self.colorize('@' + user_data.get('unique_id', 'N/A'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('Nickname:', C.GREEN)} {self.colorize(user_data.get('nickname', 'N/A'), C.WHITE)}")
        print(f"{self.colorize('User ID:', C.GREEN)} {self.colorize(user_data.get('user_id', 'N/A'), C.WHITE)}")
        
        # Status indicators
        verified = "✅" if user_data.get('verified') else "❌"
        private = "🔒" if user_data.get('privateAccount') else "🔓"
        print(f"{self.colorize('Verified:', C.GREEN)} {self.colorize(verified, C.BRIGHT_YELLOW if user_data.get('verified') else C.RED)}")
        print(f"{self.colorize('Private:', C.GREEN)} {self.colorize(private, C.BRIGHT_YELLOW if user_data.get('privateAccount') else C.GREEN)}")
        
        # Stats with icons
        print(f"\n{self.colorize('📊 STATISTICS', C.BRIGHT_YELLOW)}")
        print(f"{self.colorize('─'*40, C.CYAN)}")
        print(f"{self.colorize('👥 Followers:', C.BLUE)} {self.colorize(user_data.get('followers', '0'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('🤝 Following:', C.BLUE)} {self.colorize(user_data.get('following', '0'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('❤️  Total Likes:', C.BLUE)} {self.colorize(user_data.get('likes', '0'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('🎬 Videos:', C.BLUE)} {self.colorize(user_data.get('videos', '0'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('👍 Digg Count:', C.BLUE)} {self.colorize(user_data.get('diggCount', '0'), C.BRIGHT_WHITE)}")
        print(f"{self.colorize('👯 Friends:', C.BLUE)} {self.colorize(user_data.get('friendCount', '0'), C.BRIGHT_WHITE)}")
        
        # Biography
        if user_data.get('signature') and user_data['signature'] != 'N/A':
            print(f"\n{self.colorize('📝 BIOGRAPHY', C.BRIGHT_YELLOW)}")
            print(f"{self.colorize('─'*40, C.CYAN)}")
            print(f"{self.colorize(user_data.get('signature'), C.WHITE)}")
        
        # Social Links
        if user_data.get('social_links'):
            print(f"\n{self.colorize('🔗 SOCIAL LINKS', C.BRIGHT_YELLOW)}")
            print(f"{self.colorize('─'*40, C.CYAN)}")
            for i, link in enumerate(user_data['social_links'], 1):
                print(f"{self.colorize(f'{i}.', C.GREEN)} {self.colorize(link, C.CYAN)}")
        
        # Additional Info
        print(f"\n{self.colorize('🔧 ADDITIONAL INFO', C.BRIGHT_YELLOW)}")
        print(f"{self.colorize('─'*40, C.CYAN)}")
        print(f"{self.colorize('SecUid:', C.GREEN)} {self.colorize(user_data.get('secUid', 'N/A')[:30] + '...', C.DIM)}")
        print(f"{self.colorize('Region:', C.GREEN)} {self.colorize(user_data.get('region', 'N/A'), C.WHITE)}")
        if user_data.get('createTime') and user_data['createTime'] != 'N/A':
            print(f"{self.colorize('Created:', C.GREEN)} {self.colorize(user_data['createTime'], C.WHITE)}")
        
        # Fetch time
        if 'fetch_time' in user_data:
            print(f"\n{self.colorize('⏱️  Fetch Time:', C.DIM)} {self.colorize(user_data['fetch_time'], C.DIM)}")
        
        print(f"\n{self.colorize('='*60, C.BRIGHT_CYAN)}")
    
    def download_profile_pic(self, user_data, directory="profile_pics"):
        """Download profile picture"""
        avatar_url = user_data.get('avatarLarger')
        if avatar_url and avatar_url != 'N/A':
            try:
                # Clean URL
                avatar_url = avatar_url.replace('\\u002F', '/')
                
                # Create directory if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)
                
                # Download
                print(f"\n{self.colorize('📥 Downloading profile picture...', C.CYAN)}")
                response = requests.get(avatar_url, stream=True, timeout=10)
                
                if response.status_code == 200:
                    filename = f"{directory}/{user_data.get('unique_id', 'user')}_profile.jpg"
                    with open(filename, 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)
                    
                    print(f"{self.colorize('✅ Downloaded:', C.BRIGHT_GREEN)} {self.colorize(filename, C.WHITE)}")
                    return filename
                else:
                    print(f"{self.colorize('❌ Failed to download', C.RED)}")
                    
            except Exception as e:
                print(f"{self.colorize('❌ Error downloading:', C.RED)} {str(e)}")
        
        return None
    
    def export_to_json(self, user_data, filename=None):
        """Export user data to JSON file"""
        if not filename:
            filename = f"{user_data.get('unique_id', 'tiktok_user')}_data.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(user_data, f, indent=2, ensure_ascii=False)
            print(f"\n{self.colorize('💾 Data exported to:', C.BRIGHT_GREEN)} {self.colorize(filename, C.WHITE)}")
            return True
        except Exception as e:
            print(f"{self.colorize('❌ Export failed:', C.RED)} {str(e)}")
            return False

# ============================================
# MENU FUNCTIONS
# ============================================
def menu_scrape_single(scraper):
    """Menu for scraping single user"""
    print_header()
    print(f"{C.BRIGHT_YELLOW}SCRAPE SINGLE USER{C.RESET}\n")
    
    print(f"{C.CYAN}Choose method:{C.RESET}")
    print(f"  {C.GREEN}1{C.RESET} - By Username (e.g., @username)")
    print(f"  {C.GREEN}2{C.RESET} - By User ID")
    print(f"  {C.GREEN}0{C.RESET} - Back to Main Menu\n")
    
    choice = input(f"{C.YELLOW}Choice [1/2/0]: {C.RESET}").strip()
    
    if choice == '0':
        return
    
    identifier = input(f"\n{C.YELLOW}Enter {'Username' if choice == '1' else 'User ID'}: {C.RESET}").strip()
    
    if not identifier:
        print(f"{C.RED}❌ No input provided!{C.RESET}")
        input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        return
    
    by_id = (choice == '2')
    
    # Fetch data
    user_data = scraper.fetch_user_info(identifier, by_id)
    
    # Display results
    scraper.display_user_info(user_data)
    
    # Ask for actions
    if "error" not in user_data:
        print(f"\n{C.YELLOW}Available Actions:{C.RESET}")
        print(f"  {C.GREEN}1{C.RESET} - Download Profile Picture")
        print(f"  {C.GREEN}2{C.RESET} - Export to JSON")
        print(f"  {C.GREEN}3{C.RESET} - Save to CSV")
        print(f"  {C.GREEN}0{C.RESET} - Continue")
        
        action = input(f"\n{C.YELLOW}Action [0-3]: {C.RESET}").strip()
        
        if action == '1':
            scraper.download_profile_pic(user_data)
        elif action == '2':
            scraper.export_to_json(user_data)
        elif action == '3':
            # CSV export could be added here
            print(f"{C.YELLOW}CSV export feature coming soon!{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

def menu_scrape_multiple(scraper):
    """Menu for scraping multiple users from file"""
    print_header()
    print(f"{C.BRIGHT_YELLOW}SCRAPE MULTIPLE USERS{C.RESET}\n")
    
    filename = input(f"{C.YELLOW}Enter filename with usernames/IDs (one per line): {C.RESET}").strip()
    
    if not os.path.exists(filename):
        print(f"{C.RED}❌ File not found!{C.RESET}")
        input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        return
    
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        print(f"\n{C.GREEN}Found {len(lines)} users in file{C.RESET}")
        
        use_ids = input(f"\n{C.YELLOW}Are these User IDs? (y/N): {C.RESET}").strip().lower() == 'y'
        
        all_data = []
        successful = 0
        
        for i, identifier in enumerate(lines, 1):
            print(f"\n{C.CYAN}[{i}/{len(lines)}]{C.RESET} Processing: {C.WHITE}{identifier}{C.RESET}")
            
            user_data = scraper.fetch_user_info(identifier, use_ids)
            
            if "error" not in user_data:
                successful += 1
                scraper.display_user_info(user_data)
                all_data.append(user_data)
                
                # Save individual JSON
                json_file = f"output/{user_data.get('unique_id', f'user_{i}')}.json"
                os.makedirs('output', exist_ok=True)
                with open(json_file, 'w') as f:
                    json.dump(user_data, f, indent=2)
            else:
                print(f"{C.RED}❌ Failed: {user_data.get('error', 'Unknown error')}{C.RESET}")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
        
        # Save combined data
        if all_data:
            combined_file = f"output/batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(combined_file, 'w') as f:
                json.dump(all_data, f, indent=2)
            
            print(f"\n{C.BRIGHT_GREEN}✅ Successfully scraped {successful}/{len(lines)} users{C.RESET}")
            print(f"{C.GREEN}📁 Combined data saved to: {combined_file}{C.RESET}")
    
    except Exception as e:
        print(f"{C.RED}❌ Error: {str(e)}{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

def menu_settings(scraper):
    """Settings menu"""
    print_header()
    print(f"{C.BRIGHT_YELLOW}SETTINGS{C.RESET}\n")
    
    print(f"{C.CYAN}Current Settings:{C.RESET}")
    print(f"  Colors: {C.GREEN if scraper.use_colors else C.RED}{'Enabled' if scraper.use_colors else 'Disabled'}{C.RESET}")
    print(f"  Timeout: 15 seconds")
    print(f"  User Agent: Chrome 120")
    print()
    
    print(f"{C.YELLOW}Options:{C.RESET}")
    print(f"  {C.GREEN}1{C.RESET} - Toggle Colors")
    print(f"  {C.GREEN}2{C.RESET} - Change Theme")
    print(f"  {C.GREEN}3{C.RESET} - Reset to Defaults")
    print(f"  {C.GREEN}0{C.RESET} - Back")
    
    choice = input(f"\n{C.YELLOW}Choice [0-3]: {C.RESET}").strip()
    
    if choice == '1':
        scraper.use_colors = not scraper.use_colors
        print(f"\n{C.GREEN}✅ Colors {'enabled' if scraper.use_colors else 'disabled'}{C.RESET}")
    elif choice == '2':
        print(f"\n{C.YELLOW}Theme selection coming soon!{C.RESET}")
    elif choice == '3':
        scraper.use_colors = True
        print(f"\n{C.GREEN}✅ Settings reset to defaults{C.RESET}")
    
    input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")

def main_menu():
    """Main interactive menu"""
    scraper = TikTokScraper(use_colors=True)
    
    while True:
        print_header()
        print_banner()
        print_menu()
        
        choice = input(f"\n{C.YELLOW}{C.BOLD}Select option [0-6]: {C.RESET}").strip()
        
        if choice == '1':
            menu_scrape_single(scraper)
        elif choice == '2':
            # Direct to scrape by ID
            print_header()
            identifier = input(f"\n{C.YELLOW}Enter User ID: {C.RESET}").strip()
            if identifier:
                user_data = scraper.fetch_user_info(identifier, by_id=True)
                scraper.display_user_info(user_data)
                if "error" not in user_data:
                    scraper.download_profile_pic(user_data)
                input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        elif choice == '3':
            menu_scrape_multiple(scraper)
        elif choice == '4':
            print_header()
            print(f"{C.YELLOW}Batch download coming soon!{C.RESET}")
            input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        elif choice == '5':
            print_header()
            print(f"{C.YELLOW}Export feature coming soon!{C.RESET}")
            input(f"\n{C.DIM}Press Enter to continue...{C.RESET}")
        elif choice == '6':
            menu_settings(scraper)
        elif choice == '0':
            print(f"\n{C.BRIGHT_GREEN}👋 Thank you for using TikTok Scraper!{C.RESET}\n")
            break
        else:
            print(f"\n{C.RED}❌ Invalid choice! Please try again.{C.RESET}")
            time.sleep(1)

# ============================================
# COMMAND LINE INTERFACE
# ============================================
def command_line_mode():
    """Original command-line interface"""
    parser = argparse.ArgumentParser(
        description="Enhanced TikTok User Information Scraper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s @username
  %(prog)s username
  %(prog)s --by-id 123456789
  %(prog)s @username --download
  %(prog)s @username --json
        """
    )
    parser.add_argument("identifier", help="TikTok username (with or without @) or user ID")
    parser.add_argument("--by-id", action="store_true", help="Indicates if the provided identifier is a user ID")
    parser.add_argument("--download", action="store_true", help="Download profile picture")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    args = parser.parse_args()
    
    scraper = TikTokScraper(use_colors=not args.no_color)
    
    user_data = scraper.fetch_user_info(args.identifier, args.by_id)
    
    if args.json:
        print(json.dumps(user_data, indent=2))
    else:
        scraper.display_user_info(user_data)
    
    if args.download and "error" not in user_data:
        scraper.download_profile_pic(user_data)
    
    return 0

# ============================================
# MAIN ENTRY POINT
# ============================================
if __name__ == "__main__":
    # Check if running in interactive mode or command-line mode
    if len(sys.argv) > 1:
        # Command-line mode
        sys.exit(command_line_mode())
    else:
        # Interactive menu mode
        try:
            main_menu()
        except KeyboardInterrupt:
            print(f"\n\n{C.BRIGHT_RED}⚠️  Interrupted by user{C.RESET}")
            sys.exit(0)
        except Exception as e:
            print(f"\n{C.BRIGHT_RED}❌ Fatal error: {str(e)}{C.RESET}")
            sys.exit(1)