import slack
import os
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response

from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
client = slack.WebClient(token=os.environ['SLACK_TOKEN'])

app = Flask(__name__)

def fetch_lunch_menu():
    """Fetch the weekly lunch menu from Carotte Läppstiftet"""
    url = "https://carotte.se/restauranger/lappstiftet/dagens-lunch/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first menu section (current week)
        h2 = soup.find('h2', string=lambda text: text and 'Dagens lunch v.' in text)
        
        if not h2:
            return "Could not find menu on the page."
        
        # Get the week number
        current_week = h2.get_text(strip=True)
        menu_text = f"*🍽️ Carotte Läppstiftet - {current_week}*\n"
        menu_text += "=" * 40 + "\n\n"
        
        # Get all p tags after this h2 until we hit the next h2 or price section
        current_day = ""
        found_menu_items = False
        
        for p_tag in h2.find_all_next('p'):
            text = p_tag.get_text(strip=True)
            
            # Stop conditions
            if not text:
                continue
            if 'Pris:' in text or 'Registrera dig' in text:
                break
            # Check if we've hit the next week
            next_h2 = p_tag.find_previous('h2')
            if next_h2 and next_h2 != h2 and 'Dagens lunch v.' in next_h2.get_text():
                break
            
            # Skip opening hours
            if 'öppettider' in text.lower():
                continue
            # Skip welcome text
            if 'Välkommen till' in text:
                continue
                
            # Check for soup
            if text == 'Soppan':
                menu_text += f"*🥣 Soppan*\n"
                found_menu_items = True
            # Soup description
            elif 'soppa' in text.lower() and not text.startswith(('Kött:', 'Fisk:', 'Veg:')):
                menu_text += f"  {text}\n\n"
            # Days of the week
            elif text in ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']:
                if current_day:
                    menu_text += "\n"
                current_day = text
                menu_text += f"*{text}*\n"
                found_menu_items = True
            # Meal options
            elif text.startswith(('Kött:', 'Fisk:', 'Veg:')):
                menu_text += f"  • {text}\n"
            # Special items
            elif 'efterrätt' in text.lower() or 'dessert' in text.lower():
                menu_text += f"  🍰 {text}\n"
            elif 'Frukostbuffé' in text:
                menu_text += f"  ☕ {text}\n"
        
        if not found_menu_items:
            menu_text += "\n_Could not parse menu details. Please check the website._"
        
        return menu_text
    
    except Exception as e:
        return f"Error fetching menu: {str(e)}"

def fetch_monopolet_menu():
    """Fetch the weekly lunch menu from Monopolet"""
    url = "https://monopolet.nu/"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Get all paragraphs
        paragraphs = [p.get_text().strip() for p in soup.find_all('p') if p.get_text().strip()]
        
        # Find the week index
        week_idx = next((i for i, p in enumerate(paragraphs) if 'Vecka' in p and p.startswith('Vecka')), -1)
        
        if week_idx == -1:
            return "Could not find menu on the page."
        
        current_week = paragraphs[week_idx]
        menu_text = f"*🍽️ Monopolet - {current_week}*\n"
        menu_text += "=" * 40 + "\n\n"
        
        current_day = ""
        
        # Process paragraphs after the week indicator
        for i in range(week_idx + 1, len(paragraphs)):
            text = paragraphs[i]
            
            # Stop at booking/contact sections
            if any(stop in text.lower() for stop in ['välkomna att maila', 'kontakta oss', 'större sällskap']):
                break
            
            # Skip julbord announcements
            if 'julbord' in text.lower() or 'glöm inte' in text.lower():
                continue
            
            # Days of the week
            if text in ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']:
                if current_day:
                    menu_text += "\n"
                current_day = text
                menu_text += f"*{text}*\n"
            # Skip the separator line
            elif text.startswith('———'):
                break
            # Menu items (only when we have a current day)
            elif current_day:
                menu_text += f"  • {text}\n"
        
        if len(menu_text.split('\n')) <= 3:
            menu_text += "\n_Could not parse menu details. Please check the website._"
        
        return menu_text
    
    except Exception as e:
        return f"Error fetching menu: {str(e)}"

@app.route("/lunch", methods=["GET", "POST"])
def lunch_menu():
    # Fetch and post both menus
    carotte_menu = fetch_lunch_menu()
    monopolet_menu = fetch_monopolet_menu()
    
    # Combine both menus
    combined_menu = f"{carotte_menu}\n\n{'='*40}\n\n{monopolet_menu}"
    
    # Post to Slack
    client.chat_postMessage(channel='#mazzii', text=combined_menu)
    
    # Return the menu as response
    return Response(combined_menu, mimetype='text/plain'), 200

# load_dotenv()

# slack_app_token = os.getenv("SLACK_APP_TOKEN")
# slack_bot_token = os.getenv("SLACK_BOT_TOKEN")

# app = App(token=slack_bot_token)

# @app.event('message')
# def message(args, say):
#     data = args.__dict__
#     user_input = data.get('event').get('text')
#     event_ts = data.get('event').get('ts')
#     channel_id = data.get('event').get('channel')
    
#     if "hello world" in user_input:
#         say(channel = channel_id, text="Hello Python", thread_ts=event_ts)

# handler = SocketModeHandler(app, slack_app_token)
# handler.start()