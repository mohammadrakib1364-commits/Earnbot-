import os
import telebot
from telebot import types
from telebot.types import BotCommand
import csv
import re
import json
import time
from operator import itemgetter
import threading # Used for basic locking simulation

# --- ⚙️ CONFIGURATION SECTION (START) ---
# All configurations are mandatory for the bot to run correctly.
API_TOKEN = '9267752662:AAFW4SlAjdK8lU7VOVJT8cC3jb_bD_pf56M'
ADMIN_IDS = [8758365020]
REQUIRED_CHANNELS = [-1004327839937]
OTP_MONITOR_GROUPS = [-5599126517]
DATA_FOLDER = 'data'
BOT_NAME = "@lakibsma_bot"

# --- NEW REFERRAL & WITHDRAWAL CONSTANTS ---
REFERRAL_COMMISSION = 0.03  # Amount to be added per successful referral (0.03)
MIN_WITHDRAWAL = 0.50       # Minimum amount for withdrawal (0.50)
# -------------------------------------------

# --- FILE PATHS ---
WARN_FILE = os.path.join(DATA_FOLDER, "warned_users.json")
NUMBER_USER_FILE = os.path.join(DATA_FOLDER, "number_user.json")
USERS_FILE = os.path.join(DATA_FOLDER, 'users.txt')
VERIFIED_FILE = os.path.join(DATA_FOLDER, "verified_users.json")
TRAFFIC_FILE = os.path.join(DATA_FOLDER, "traffic.json")
MONITOR_GROUPS_FILE = os.path.join(DATA_FOLDER, "monitor_groups.json")
SUCCESS_COUNT_FILE = os.path.join(DATA_FOLDER, "success_count.json")
LAST_NUMBER_TAKEN_FILE = os.path.join(DATA_FOLDER, "last_number_taken.json")
# --- NEW FILE PATH ---
USER_BALANCES_FILE = os.path.join(DATA_FOLDER, 'user_balances.json')
# ---------------------

# --- CONSTANTS ---
CANCEL_BUTTON = "🔙 Cancel"
COOLDOWN_SECONDS = 0 
DEFAULT_OTP_GROUP_LINK = "https://t.me/itachiotp"

# Country Name to Flag mapping
COUNTRY_FLAGS = {
    "AFGHANISTAN": "🇦🇫", "ALBANIA": "🇦🇱", "ALGERIA": "🇩🇿", "ANDORRA": "🇦🇩",
    "ANGOLA": "🇦🇴", "ANTIGUA_AND_BARBUDA": "🇦🇬", "ARGENTINA": "🇦🇷",
    "ARMENIA": "🇦🇲", "AUSTRALIA": "🇦🇺", "AUSTRIA": "🇦🇹", "AZERBAIJAN": "🇦🇿",
    "BAHAMAS": "🇧🇸", "BAHRAIN": "🇧🇭", "BANGLADESH": "🇧🇩", "BARBADOS": "🇧🇧",
    "BELARUS": "🇧🇾", "BELGIUM": "🇧🇪", "BELIZE": "🇧🇿", "BENIN": "🇧🇯",
    "BHUTAN": "🇧🇹", "BOLIVIA": "🇧🇴", "BOSNIA_AND_HERZEGOVINA": "🇧🇦",
    "BOTSWANA": "🇧🇼", "BRAZIL": "🇧🇷", "BRUNEI": "🇧🇳", "BULGARIA": "🇧🇬",
    "BURKINA_FASO": "🇧🇫", "BURUNDI": "🇧🇮", "CAMBODIA": "🇰🇭", "CAMEROON": "🇨🇲",
    "CANADA": "🇨🇦", "CAPE_VERDE": "🇨🇻", "CENTRAL_AFRICAN_REPUBLIC": "🇨🇫",
    "CHAD": "🇹🇩", "CHILE": "🇨🇱", "CHINA": "🇨🇳", "COLOMBIA": "🇨🇴",
    "COMOROS": "🇰🇲", "CONGO_BRAZZAVILLE": "🇨🇬", "CONGO_KINSHASA": "🇨🇩",
    "COSTA_RICA": "🇨🇷", "COTE_DIVOIRE": "🇨🇮", "CROATIA": "🇭🇷", "CUBA": "🇨🇺",
    "CYPRUS": "🇨🇾", "CZECHIA": "🇨🇿", "DENMARK": "🇩🇰", "DJIBOUTI": "🇩🇯",
    "DOMINICA": "🇩🇲", "DOMINICAN_REPUBLIC": "🇩🇴", "ECUADOR": "🇪🇨",
    "EGYPT": "🇪🇬", "EL_SALVADOR": "🇸🇻", "EQUATORIAL_GUINEA": "🇬🇶",
    "ERITREA": "🇪🇷", "ESTONIA": "🇪🇪", "ESWATINI": "🇸🇿", "ETHIOPIA": "🇪🇹",
    "FIJI": "🇫🇯", "FINLAND": "🇫🇮", "FRANCE": "🇫🇷", "GABON": "🇬🇦",
    "GAMBIA": "🇬🇲", "GEORGIA": "🇬🇪", "GERMANY": "🇩🇪", "GHANA": "🇬🇭",
    "GREECE": "🇬🇷", "GRENADA": "🇬🇩", "GUATEMALA": "🇬🇹", "GUINEA": "🇬🇳",
    "GUINEA_BISSAU": "🇬🇼", "GUYANA": "🇬🇾", "HAITI": "🇭🇹", "HONDURAS": "🇭🇳",
    "HUNGARY": "🇭🇺", "ICELAND": "🇮🇸", "INDIA": "🇮🇳", "INDONESIA": "🇮🇩",
    "IRAN": "🇮🇷", "IRAQ": "🇮🇶", "IRELAND": "🇮🇪", "ISRAEL": "🇮🇱",
    "ITALY": "🇮🇹", "JAMAICA": "🇯🇲", "JAPAN": "🇯🇵", "JORDAN": "🇯🇴",
    "KAZAKHSTAN": "🇰🇿", "KENYA": "🇰🇪", "KIRIBATI": "🇰🇮", "KUWAIT": "🇰🇼",
    "KYRGYZSTAN": "🇰🇬", "LAOS": "🇱🇦", "LATVIA": "🇱🇻", "LEBANON": "🇱🇧",
    "LESOTHO": "🇱🇸", "LIBERIA": "🇱🇷", "LIBYA": "🇱🇾", "LIECHTENSTEIN": "🇱🇮",
    "LITHUANIA": "🇱🇹", "LUXEMBOURG": "🇱🇺", "MADAGASCAR": "🇲🇬", "MALAWI": "🇲🇼",
    "MALAYSIA": "🇲🇾", "MALDIVES": "🇲🇻", "MALI": "🇲🇱", "MALTA": "🇲🇹",
    "MARSHALL_ISLANDS": "🇲🇭", "MAURITANIA": "🇲🇷", "MAURITIUS": "🇲🇺", "MEXICO": "🇲🇽",
    "MICRONESIA": "🇫🇲", "MOLDOVA": "🇲🇩", "MONACO": "🇲🇨", "MONGOLIA": "🇲🇳",
    "MONTENEGRO": "🇲🇪", "Morocco": "🇲🇦", "MOZAMBIQUE": "🇲🇿", "MYANMAR": "🇲🇲",
    "NAMIBIA": "🇳🇦", "NEPAL": "🇳🇵", "NETHERLANDS": "🇳🇱", "NEW_ZEALAND": "🇳🇿",
    "NICARAGUA": "🇳🇮", "NIGER": "🇳🇪", "NIGERIA": "🇳🇬", "NORTH_KOREA": "🇰🇵",
    "NORTH_MACEDONIA": "🇲🇰", "NORWAY": "🇳🇴", "OMAN": "🇴🇲", "PAKISTAN": "🇵🇰",
    "PANAMA": "🇵🇦", "PAPUA_NEW_GUINEA": "🇵🇬", "PARAGUAY": "🇵🇾", "PERU": "🇵🇪",
    "PHILIPPINES": "🇵🇭", "POLAND": "🇵🇱", "PORTUGAL": "🇵🇹", "QATAR": "🇶🇦",
    "ROMANIA": "🇷🇴", "RUSSIA": "🇷🇺", "RWANDA": "🇷🇼", "SAINT_KITTS_AND_NEVIS": "🇰🇳",
    "SAINT_LUCIA": "🇱🇨", "SAINT_VINCENT_AND_THE_GRENADINES": "🇻🇨",
    "SAMOA": "🇼🇸", "SAN_MARINO": "🇸🇲", "SAO_TOME_AND_PRINCIPE": "🇸🇹",
    "SAUDI_ARABIA": "🇸🇦", "SENEGAL": "🇸🇳", "SERBIA": "🇷🇸", "SEYCHELLES": "🇸🇨",
    "SIERRA_LEONE": "🇸🇱", "SINGAPORE": "🇸🇬", "SLOVAKIA": "🇸🇰", "SLOVENIA": "🇸🇮",
    "SOLOMON_ISLANDS": "🇸🇧", "SOMALIA": "🇸🇴", "SOUTH_AFRICA": "🇿🇦", "SOUTH_KOREA": "🇰🇷",
    "SPAIN": "🇪🇸", "SRI_LANKA": "🇱🇰", "SUDAN": "🇸🇩", "SURINAME": "🇸🇷",
    "SWEDEN": "🇸🇪", "SWITZERLAND": "🇨🇭", "SYRIA": "🇸🇾", "TAIWAN": "🇹🇼",
    "TAJIKISTAN": "🇹🇯", "TANZANIA": "🇹🇿", "THAILAND": "🇹🇭", "TIMOR_LESTE": "🇹🇱",
    "TOGO": "🇹🇬", "TONGA": "🇹🇴", "TRINIDAD_AND_TOBAGO": "🇹🇹", "TUNISIA": "🇹🇳",
    "TURKEY": "🇹🇷", "TURKMENISTAN": "🇹🇲", "TUVALU": "🇹🇻", "UGANDA": "🇺🇬",
    "UKRAINE": "🇺🇦", "UNITED_ARAB_EMIRATES": "🇦🇪", "UNITED_KINGDOM": "🇬🇧",
    "USA": "🇺🇸", "URUGUAY": "🇺🇾", "UZBEKISTAN": "🇺🇿", "VANUATU": "🇻🇺",
    "VATICAN_CITY": "🇻🇦", "VENEZUELA": "🇻🇪", "VIETNAM": "🇻🇳", "YEMEN": "🇾🇪",
    "ZAMBIA": "🇿🇲", "ZIMBABWE": "🇿🇼"
}
# --- ⚙️ CONFIGURATION SECTION (END) ---

# Initialize data folder
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)


class DataManager:
    """
    Handles all file-based data operations with basic error handling
    and uses a threading Lock for critical operations to simulate safety.
    """
    def __init__(self):
        self._lock = threading.Lock()

    def _read_json(self, file_path, default_value={}):
        """Reads JSON data from a file, returning default_value on failure or non-existence."""
        if not os.path.exists(file_path):
            return default_value
        try:
            # Use lock for thread safety simulation during file read
            with self._lock:
                with open(file_path, "r") as f:
                    return json.load(f)
        except Exception as e:
            print(f"DataManager Error: Failed to read JSON from {file_path}. Error: {e}")
            return default_value

    def _write_json(self, file_path, data):
        """Writes data to a JSON file."""
        try:
            # Use lock for thread safety simulation during file write
            with self._lock:
                with open(file_path, "w") as f:
                    json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"DataManager Error: Failed to write JSON to {file_path}. Error: {e}")
            return False

    def get_last_number_taken(self, user_id):
        data = self._read_json(LAST_NUMBER_TAKEN_FILE, {})
        return data.get(str(user_id), "N/A")

    def save_last_number_taken(self, user_id, number):
        data = self._read_json(LAST_NUMBER_TAKEN_FILE, {})
        data[str(user_id)] = number
        return self._write_json(LAST_NUMBER_TAKEN_FILE, data)
        
    def load_number_user_map(self):
        return self._read_json(NUMBER_USER_FILE, {})

    def save_number_user_map(self, data):
        return self._write_json(NUMBER_USER_FILE, data)
        
    def load_success_count(self):
        return self._read_json(SUCCESS_COUNT_FILE, {})

    def update_success_count(self, user_id):
        data = self.load_success_count()
        data[str(user_id)] = data.get(str(user_id), 0) + 1
        return self._write_json(SUCCESS_COUNT_FILE, data)

    def load_monitor_groups(self):
        return self._read_json(MONITOR_GROUPS_FILE, [])

    def save_monitor_groups(self, group_list):
        return self._write_json(MONITOR_GROUPS_FILE, group_list)

    def load_traffic(self):
        return self._read_json(TRAFFIC_FILE, [])

    def save_traffic(self, traffic_list):
        return self._write_json(TRAFFIC_FILE, traffic_list)

    def read_all_users(self):
        """Reads the list of all saved user IDs."""
        if not os.path.exists(USERS_FILE):
            return []
        try:
            with self._lock:
                with open(USERS_FILE, "r") as f:
                    # Use set for uniqueness and list comprehension for type conversion
                    return list(set([int(x.strip()) for x in f if x.strip().isdigit()]))
        except Exception as e:
            print(f"DataManager Error: Failed to read users file. Error: {e}")
            return []

    def save_user(self, user_id):
        """Saves the user ID to the user list file if not already present."""
        user_id_str = str(user_id)
        users = self.read_all_users()
        if user_id in users:
            return

        try:
            with self._lock:
                with open(USERS_FILE, "a") as f:
                    f.write(user_id_str + "\n")
        except Exception as e:
            print(f"DataManager Error: Failed to save user {user_id}. Error: {e}")
            
    # --- NEW BALANCE MANAGEMENT METHODS ---
    def load_balances(self):
        """Loads all user balance and referral data."""
        return self._read_json(USER_BALANCES_FILE, {})

    def save_balances(self, data):
        """Writes all user balance and referral data."""
        return self._write_json(USER_BALANCES_FILE, data)

    def get_balance(self, user_id):
        """Returns the user's balance and referral info, initializes if not found."""
        data = self.load_balances()
        # Initialize default structure for a new user
        return data.get(str(user_id), {"balance": 0.0, "referred_by": None, "referrals": 0})

    def update_balance_and_referral(self, user_id, amount_change=0.0, referred_by=None, is_referral_success=False):
        """Updates user balance and optionally sets referrer/increments referral count."""
        data = self.load_balances()
        user_id_str = str(user_id)
        
        # Initialize if new user
        if user_id_str not in data:
            data[user_id_str] = self.get_balance(user_id)
        
        # Update balance (using round for currency arithmetic precision)
        data[user_id_str]["balance"] = round(data[user_id_str]["balance"] + amount_change, 2)
        
        # Set referrer if not already set (only on first start)
        if referred_by and data[user_id_str]["referred_by"] is None:
            data[user_id_str]["referred_by"] = referred_by
        
        # Increment referral count
        if is_referral_success:
            data[user_id_str]["referrals"] += 1

        return self.save_balances(data)
    # ------------------------------------------

    def count_country_numbers(self, country):
        """Counts the number of lines in a country CSV file."""
        file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
        try:
            with self._lock:
                with open(file_path, "r") as f:
                    return len(f.readlines())
        except FileNotFoundError:
            return 0
        except Exception as e:
            print(f"DataManager Error: Failed to count lines for {country}. Error: {e}")
            return 0


class OTPBot:
    """
    Main class encapsulating the entire bot logic and handlers.
    """
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.dm = DataManager()
        self.user_last_request = {}
        self.setup_handlers()
        self.setup_commands()

    # --- BOT UTILITIES & CORE LOGIC ---

    def _get_flag(self, country_name):
        """Returns the flag emoji for a country name, defaults to 🌍."""
        return COUNTRY_FLAGS.get(country_name.upper(), "🌍")

    def _is_subscribed(self, user_id):
        """Checks if the user is subscribed to all required channels."""
        for channel in REQUIRED_CHANNELS:
            try:
                member = self.bot.get_chat_member(channel, user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    return False
            except Exception as e:
                # Log the error but treat as not subscribed to prevent bot failure
                print(f"Subscription check error for {user_id} in {channel}: {e}")
                return False
        return True

    def _extract_otp(self, text):
        """Robustly extracts OTP codes based on common patterns."""
        # Pattern 1: Search for codes preceded by keywords
        match_keyword = re.search(r'(?:OTP|Code|PIN|Cod|Verification|SMS|Passcode)[^\d\n]*([\d\-\s]{4,8})', text, re.IGNORECASE)
        if match_keyword:
            cleaned_otp = re.sub(r'[\s\-]', '', match_keyword.group(1))
            if 4 <= len(cleaned_otp) <= 8:
                return cleaned_otp

        # Pattern 2: Search for 4 to 8 digit numbers
        match_standalone = re.search(r'\b([\d\-\s]{4,8})\b', text)
        if match_standalone:
            cleaned_otp = re.sub(r'[\s\-]', '', match_standalone.group(1))
            if 4 <= len(cleaned_otp) <= 8:
                return cleaned_otp
            
        # Pattern 3: Legacy/Flexible search for short codes
        match_legacy = re.search(r"(\d{4,8})", text)
        if match_legacy:
            return match_legacy.group(1)
            
        return None

    def _send_otp_to_user(self, chat_id, number, otp, country):
        """
        Forwards the received OTP to the active user, updates success count, and 
        removes the number from the active list.
        """
        text = (
    "╔══════════════════╗\n"
    "        🔐 OTP RECEVED\n"
    "╠══════════════════╣\n"
    f"   📞 Number ➤ `{number}`\n"
    f"   💬 Otp ➤ `{otp}`\n"
    "╚══════════════════╝"
        )
        try:
            self.bot.send_message(chat_id, text, parse_mode="Markdown")
            self.dm.update_success_count(chat_id)

            # Remove the number from the active list
            data = self.dm.load_number_user_map()
            if number in data:
                del data[number]
                self.dm.save_number_user_map(data)
                
        except Exception as e:
            print(f"Error forwarding OTP or updating status for {chat_id}: {e}")

    def _assign_number_core(self, chat_id, message_id, country):
        """Core logic to assign a number from the CSV file."""
        current_time = time.time()
        
        # Cooldown Check
        if chat_id in self.user_last_request:
            elapsed = current_time - self.user_last_request[chat_id]
            if elapsed < COOLDOWN_SECONDS:
                return False 
        self.user_last_request[chat_id] = current_time
        
        file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
        lines = []

        try:
            # Read all lines and pop one
            with self.dm._lock:
                with open(file_path, "r") as f:
                    lines = f.readlines()
        except FileNotFoundError:
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ No numbers found for this country.", parse_mode="Markdown")
            return True
        except Exception as e:
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ Error reading number file: {e}", parse_mode="Markdown")
            return True

        if not lines:
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ No numbers available currently for this country.", parse_mode="Markdown")
            return True

        number = lines.pop(0).strip() 

        try:
            # Write remaining lines back
            with self.dm._lock:
                with open(file_path, "w") as f:
                    f.writelines(lines)
        except Exception as e:
            self.bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ Error saving numbers: {e}", parse_mode="Markdown")
            return True

        # Update active number map
        data = self.dm.load_number_user_map()
        data[number] = {
            "user_id": chat_id,
            "country": country,
            "time": current_time,
            "status": "Waiting"
        }
        self.dm.save_number_user_map(data)
        self.dm.save_last_number_taken(chat_id, number)

        # Send success message with updated inline keyboard
        text = (
            f"*✅ New Number For You 🔰*\n\n"
            f"*Number ⋮* `{number}`\n\n"
            f"*Country ⋮* {country} {self._get_flag(country)}\n"
            "*OTP Status ⋮* Waiting for OTP"
        )
        keyboard = types.InlineKeyboardMarkup()
        # Changed button for 'Change Number' to include the full number for status check in the callback
        keyboard.add(types.InlineKeyboardButton("🔄 Change Number", callback_data=f"change_{country}"))
        # Using the updated DEFAULT_OTP_GROUP_LINK
        keyboard.add(types.InlineKeyboardButton("💬 View OTP Group", url=DEFAULT_OTP_GROUP_LINK)) 
        keyboard.add(types.InlineKeyboardButton("🌍 Change Country", callback_data="change_country_menu")) 
        
        self.bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text,
                                parse_mode="Markdown",
                                reply_markup=keyboard)
        return True


    # --- KEYBOARDS ---

    def _get_main_menu_keyboard(self):
        """Generates the user's main menu reply keyboard."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📞 Get Number", "📦 Stock")
        # -------------------------
        markup.add("☎️ Support")
        return markup

    def _get_admin_panel_keyboard(self):
        """Generates the admin panel reply keyboard with all features."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("➕ Add New Country", "🗑️ Delete Country")
        markup.add("➕ Add Traffic", "🗑️ Delete Traffic")
        markup.add("🌍 Show Available Countries", "📊 Statistics")
        markup.add("📢 Broadcast Message", "👥 Total Users")
        markup.add("➕ Add Monitor Group", "🏆 Top Receivers")
        return markup

    def _get_admin_panel_keyboard_only_cancel(self):
        """Generates a temporary keyboard with only the Cancel button."""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(CANCEL_BUTTON)
        return markup

    # --- HANDLERS SETUP ---
    
    def setup_commands(self):
        try:
            self.bot.set_my_commands([
                BotCommand("start", "Restart Bot 🔄"),
                BotCommand("start", "Restart Bot 🔄")
            ])
        except Exception as e:
            print(f"Error setting bot commands: {e}")

    def setup_handlers(self):
        # Global Handlers
        self.bot.message_handler(commands=['start'])(self.start_handler)
        self.bot.message_handler(commands=['admin'])(self.admin_command_handler)
        self.bot.message_handler(func=lambda m: m.text == CANCEL_BUTTON)(self.cancel_handler)
        
        # User Menu Handlers
        self.bot.message_handler(func=lambda m: m.text == "📞 Get Number")(self.get_number_menu)
        self.bot.message_handler(func=lambda m: m.text == "📦 Stock")(self.handle_stock_display)
        self.bot.message_handler(func=lambda m: m.text == "☎️ Support")(self.handle_support)
        
       # Admin Panel Handlers
        self.bot.message_handler(func=lambda m: m.text == "👥 Total Users" and m.from_user.id in ADMIN_IDS)(self.show_total_users)
        self.bot.message_handler(func=lambda m: m.text == "📊 Statistics" and m.from_user.id in ADMIN_IDS)(self.show_stats)
        self.bot.message_handler(func=lambda m: m.text == "🏆 Top Receivers" and m.from_user.id in ADMIN_IDS)(self.show_top_receivers)
        self.bot.message_handler(func=lambda m: m.text == "📢 Broadcast Message" and m.from_user.id in ADMIN_IDS)(self.ask_broadcast_message)
        self.bot.message_handler(func=lambda m: m.text == "➕ Add New Country" and m.from_user.id in ADMIN_IDS)(self.ask_country_name)
        self.bot.message_handler(func=lambda m: m.text == "🗑️ Delete Country" and m.from_user.id in ADMIN_IDS)(self.delete_country_step)
        self.bot.message_handler(func=lambda m: m.text == "➕ Add Traffic" and m.from_user.id in ADMIN_IDS)(self.ask_traffic_name)
        self.bot.message_handler(func=lambda m: m.text == "🗑️ Delete Traffic" and m.from_user.id in ADMIN_IDS)(self.delete_traffic_step)
        self.bot.message_handler(func=lambda m: m.text == "➕ Add Monitor Group" and m.from_user.id in ADMIN_IDS)(self.ask_monitor_group_id)
        self.bot.message_handler(func=lambda m: m.text == "🌍 Show Available Countries" and m.from_user.id in ADMIN_IDS)(self.show_countries)

        # Inline Callback Handlers
        self.bot.callback_query_handler(func=lambda call: call.data == "verify_again")(self.handle_verify_again)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith(("country_", "change_")))(self.handle_get_or_change_number)
        self.bot.callback_query_handler(func=lambda call: call.data == "change_country_menu")(self.handle_change_country_menu)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith("status_"))(self.handle_status_check)
        # --- NEW CALLBACK HANDLER ---
        self.bot.callback_query_handler(func=lambda call: call.data.startswith("copy_link_"))(self.handle_copy_link_callback)
        # ----------------------------

        # Default/Monitoring Handler
        self.bot.message_handler(func=lambda m: True, content_types=["text"])(self.monitor_otp_messages)


    # --- HANDLER IMPLEMENTATION (Global) ---

    def start_handler(self, message):
        user_id = message.from_user.id
        self.dm.save_user(user_id)

        # --- NEW REFERRAL CHECK LOGIC (Start) ---
        referred_by_id = None
        if message.text.startswith('/start'):
            try:
                # Expecting: /start ref_USER_ID
                args = message.text.split()
                if len(args) == 2 and args[1].startswith('ref_'):
                    referred_by_id = int(args[1].replace('ref_', ''))
            except ValueError:
                referred_by_id = None # Invalid ref ID

        user_data = self.dm.get_balance(user_id)
        
        # Check if this user is NEW and was referred by someone else
        if referred_by_id and referred_by_id != user_id and user_data.get('referred_by') is None:
            # 1. Update the new user's referred_by field
            # 2. Credit the referrer (referred_by_id) with the commission
            self.dm.update_balance_and_referral(user_id, referred_by=referred_by_id)
            self.dm.update_balance_and_referral(referred_by_id, amount_change=REFERRAL_COMMISSION, is_referral_success=True)
            
            # Notify the referrer
            try:
                referrer_text = f"💰 **Congratulations!**\n\nYour friend has successfully joined the bot using your link! You have received *{REFERRAL_COMMISSION:.2f}* in your balance."
                self.bot.send_message(referred_by_id, referrer_text, parse_mode="Markdown")
            except Exception as e:
                print(f"Error notifying referrer {referred_by_id}: {e}")
        # --- NEW REFERRAL CHECK LOGIC (End) ---


        if not self._is_subscribed(user_id):
            # Subscription logic (same as before)
            welcome_text = (
                "<b>💬 Welcome ITACHI UCHIHA OTP ✅</b>\n"
                "<b>🔐 We help to receve otp</b>\n\n"
                "<b>Please Join Our Channel For Use!</b>"
            )
            markup = types.InlineKeyboardMarkup(row_width=2) 
            
            if len(REQUIRED_CHANNELS) >= 2:
                markup.add(
                    types.InlineKeyboardButton("ITACHI-UCHIA34", url=f"https://t.me/itachialive321"),
                    types.InlineKeyboardButton("ITACHI OTP GROUP", url=f"https://t.me/itachiotp"))
            else:
                for channel in REQUIRED_CHANNELS:
                    markup.add(types.InlineKeyboardButton(channel.replace('@', ''), url=f"https://t.me/{channel.replace('@','')}"))

            markup.add(types.InlineKeyboardButton("✅ Verify Again", callback_data="verify_again")) 
            
            try:
                self.bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="HTML")
            except Exception as e:
                print(f"Error sending subscription message: {e}")
            return

        # Send the main menu
        self.bot.send_message(user_id, 
                            "💬 *Welcome ITACHI UCHIHA OTP* ✅\n🔐 *We help to receve otp*", 
                            parse_mode="Markdown",
                            reply_markup=self._get_main_menu_keyboard())

    def admin_command_handler(self, message):
        if message.from_user.id not in ADMIN_IDS:
            self.bot.send_message(message.chat.id, "❌ You don't have permission to access this tool.")
            return
        self.admin_panel(message)

    def admin_panel(self, message):
        self.bot.send_message(message.chat.id, "👨‍💻 Control Panel", reply_markup=self._get_admin_panel_keyboard())

    def cancel_handler(self, message):
        if message.from_user.id in ADMIN_IDS:
            self.admin_panel(message)
        else:
            self.start_handler(message)


    # --- HANDLER IMPLEMENTATION (User Menu) ---

    def get_number_menu(self, message):
        if not self._is_subscribed(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Please subscribe to our channels first to use this feature.")
            return

        welcome_text = ("🌍 *Choose Your Country* 👇")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        countries_found = False
        
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".csv"):
                country = filename.replace(".csv", "")
                # Show stock count in button
                stock_count = self.dm.count_country_numbers(country)
                button_text = f"{self._get_flag(country)} {country} ({stock_count})"
                keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=f"country_{country}"))
                countries_found = True
                
        if not countries_found:
            self.bot.send_message(message.chat.id, "❌ No countries available yet. Please try again later.")
            return

        self.bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=keyboard)

    def handle_stock_display(self, message):
        if not self._is_subscribed(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Please subscribe to our channels first to use this feature.")
            return

        stock_list = []
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".csv"):
                country = filename.replace(".csv", "")
                stock_count = self.dm.count_country_numbers(country)
                stock_list.append((country, stock_count))
                
        if not stock_list:
            self.bot.send_message(message.chat.id, "📊 *Current Stock:*\n\nNo numbers available in stock.", parse_mode="Markdown")
            return

        stock_list.sort(key=lambda x: x[0])
        
        text = "📊 *Current Stock:*\n\n"
        for country, count in stock_list:
            text += f"🌍 {country} {self._get_flag(country)}: *{count}* numbers available\n"
            
        self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

    def handle_user_status(self, message):
        if not self._is_subscribed(message.from_user.id):
            self.bot.send_message(message.chat.id, "❌ Please subscribe to our channels first to use this feature.")
            return

        user_id = message.from_user.id
        last_number = self.dm.get_last_number_taken(user_id)
        
        # --- ADD BALANCE TO STATUS ---
        user_data = self.dm.get_balance(user_id)
        balance = user_data.get('balance', 0.0)
        
        text = (
            "📊 *Your Status*\n\n"
            f"🔹 Last Number Taken: `{last_number}`\n"
            f"🔹 Current Balance: *{balance:.2f}*\n" # New balance display
            f"🔹 Bot Status: 🟢 *ON*\n"
            f"🔹 {BOT_NAME}"
        )
        # -----------------------------
        self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

    def handle_support(self, message):
        self.bot.send_message(message.chat.id, "For support contact: **@TechSmsSupportbot**", parse_mode="Markdown")

    def handle_available_traffic(self, message):
        traffic = self.dm.load_traffic()
        
        if not traffic:
            self.bot.send_message(message.chat.id, "No traffic currently available.")
        else:
            text = "🌍 **Available Traffic:**\n"
            text += "\n".join(f"• {item}" for item in traffic)
            self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

    # --- HANDLER IMPLEMENTATION (New Features: Refer & Withdraw) ---

    def friend_invite_handler(self, message):
        """Handles the 'Friend invite' button. Displays referral link and stats."""
        user_id = message.from_user.id
        
        # Get bot username for the referral link
        try:
            # Fetches bot username dynamically
            bot_username = self.bot.get_me().username
        except Exception:
            bot_username = "YourBotName" # Fallback
            
        # Construct the referral link (t.me/BOT_USERNAME?start=ref_USER_ID)
        referral_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
        
        # Get user's current balance and referral count
        user_data = self.dm.get_balance(user_id)
        balance = user_data.get('balance', 0.0)
        referrals = user_data.get('referrals', 0)
        
        invite_message = (
            "🎉 **Refer & Earn!** 🎉\n\n"
            "Hey there! Want to earn some cash? Invite your friends to use our bot and get rewarded for every successful referral.\n\n"
            f"**Your Referral Link:**\n"
            f"`{referral_link}`\n\n"
            "Share this link with your friends. When they join and start the bot, you will receive a commission!\n\n"
            f"**Commission per referral:** *{REFERRAL_COMMISSION:.2f}*\n\n"
            f"**Your Stats:**\n"
            f"• Current Balance: *{balance:.2f}*\n"
            f"• Total Referrals: *{referrals}*\n\n"
            "Thank you for helping us grow!"
        )
        
        markup = types.InlineKeyboardMarkup()
        # Add a button to copy the link (for better UX)
        markup.add(types.InlineKeyboardButton("🔗 Copy Link", callback_data=f"copy_link_{user_id}"))
        
        self.bot.send_message(user_id, invite_message, parse_mode="Markdown", reply_markup=markup)


    def withdraw_step_1(self, message):
        """Handles the 'withdraw' button. Checks balance and asks for Bikash number."""
        user_id = message.from_user.id
        
        # Ensure user is subscribed before allowing withdrawal
        if not self._is_subscribed(user_id):
            self.bot.send_message(user_id, "❌ Please join our required channels to use this feature.", reply_markup=self._get_main_menu_keyboard())
            return
        
        user_data = self.dm.get_balance(user_id)
        balance = user_data.get('balance', 0.0)
        
        if balance < MIN_WITHDRAWAL:
            # Insufficient Balance Message (English as requested)
            text = (
                "❌ **Insufficient Balance!** ❌\n\n"
                "We apologize, but your current balance is too low to process a withdrawal.\n"
                f"• **Your Balance:** *{balance:.2f}*\n"
                f"• **Minimum Withdrawal:** *{MIN_WITHDRAWAL:.2f}*\n\n"
                "Please invite more friends using your referral link to increase your earnings."
            )
            self.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=self._get_main_menu_keyboard())
            return

        # Sufficient Balance: Ask for Bikash number
        text = (
            "✅ **Withdrawal Request**\n\n"
            f"Your current balance is *{balance:.2f}*.\n"
            "Please enter your **Bikash Personal Number** where you wish to receive the payment. \n"
            "**Note:** The total available balance will be withdrawn."
        )
        # Use admin panel's cancel button for consistency
        msg = self.bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        
        # Use next step handler to get the Bikash number. Pass the full balance amount.
        self.bot.register_next_step_handler(msg, self.withdraw_step_2, balance)
        

    def withdraw_step_2(self, message, amount):
        """Processes the Bikash number, forwards request to admin, and updates balance."""
        user_id = message.from_user.id
        
        if message.text == CANCEL_BUTTON:
            self.bot.send_message(user_id, "❌ Withdrawal cancelled.", reply_markup=self._get_main_menu_keyboard())
            return

        bikash_number = message.text.strip()
        
        # Basic validation for the number format (Bikash is typically 11 digits, starting with 01)
        if not re.match(r'^(01[3-9]\d{8})$', bikash_number):
            # Reprompt the user if validation fails
            msg = self.bot.send_message(user_id, "❌ Invalid Bikash number format. Please ensure it is an 11-digit number (e.g., 01xxxxxxxxx). Please try again or type '🔙 Cancel'.", parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard_only_cancel())
            self.bot.register_next_step_handler(msg, self.withdraw_step_2, amount)
            return

        # 1. Forward to Admin (First Admin ID as requested)
        admin_id = ADMIN_IDS[0] 
        
        admin_forward_message = (
            "🚨 **NEW WITHDRAWAL REQUEST** 🚨\n\n"
            f"• **User ID:** `{user_id}`\n"
            f"• **User Link:** [View User](tg://user?id={user_id})\n"
            f"• **Amount:** *{amount:.2f}*\n"
            f"• **Bikash Number:** `{bikash_number}`\n\n"
            "Please process the payment."
        )
        
        try:
            self.bot.send_message(admin_id, admin_forward_message, parse_mode="Markdown")
            
            # 2. Update user balance (Deduct the amount)
            self.dm.update_balance_and_referral(user_id, amount_change=-amount)
            
            # 3. Confirmation to User (English as requested)
            user_confirmation_text = (
                "✅ **Request Sent Successfully!** ✅\n\n"
                f"Your withdrawal request of *{amount:.2f}* has been successfully sent to the admin.\n"
                f"The payment will be processed to your Bikash number: `{bikash_number}` as soon as possible.\n\n"
                "Thank you for your patience!"
            )
            self.bot.send_message(user_id, user_confirmation_text, parse_mode="Markdown", reply_markup=self._get_main_menu_keyboard())
            
        except Exception as e:
            print(f"Error forwarding withdrawal request to admin {admin_id}: {e}")
            self.bot.send_message(user_id, "❌ **An error occurred.** We could not send your request to the admin. Please try again later.", reply_markup=self._get_main_menu_keyboard())


    # --- HANDLER IMPLEMENTATION (Admin Panel) ---

    def show_total_users(self, message):
        num_users = len(self.dm.read_all_users())
        self.bot.send_message(message.chat.id, f"👥 **Total Users:** *{num_users}* users have started the bot.", parse_mode="Markdown")

    def show_stats(self, message):
        num_users = len(self.dm.read_all_users())
        
        # Calculate Country/Number Stats
        num_countries = 0
        total_available_numbers = 0
        for f in os.listdir(DATA_FOLDER):
            if f.endswith(".csv"):
                num_countries += 1
                total_available_numbers += self.dm.count_country_numbers(f.replace(".csv", ""))

        # Calculate Waiting/Received Stats
        active_numbers_map = self.dm.load_number_user_map()
        numbers_waiting = len(active_numbers_map)
            
        codes_received = sum(self.dm.load_success_count().values())
        
        # --- Add Referral Stats to Admin Panel ---
        all_balances = self.dm.load_balances()
        total_referrals = sum(data.get('referrals', 0) for data in all_balances.values())
        
        text = (
            "📈 *Bot Statistics:*\n\n"
            f"👥 Total Users: *{num_users}*\n"
            f"🏆 Total Referrals: *{total_referrals}*\n" # New Stat
            f"🌍 Number of Countries: *{num_countries}*\n"
            f"📱 Total Available Numbers: *{total_available_numbers}*\n"
            f"-------------------------------\n"
            f"✅ Codes Received (Total): *{codes_received}*\n"
            f"⏳ Numbers Waiting: *{numbers_waiting}*"
        )
        self.bot.send_message(message.chat.id, text, parse_mode="Markdown")

    def show_top_receivers(self, message):
        data = self.dm.load_success_count()
        if not data:
            self.bot.send_message(message.chat.id, "❌ No successful OTPs recorded yet.", reply_markup=self._get_admin_panel_keyboard())
            return

        sorted_users = sorted(data.items(), key=lambda item: item[1], reverse=True)
        
        top_receivers = "*🏆 Top 5 OTP Receivers:*\n"
        top_receivers += "---------------------------------\n"
        
        for i, (user_id, count) in enumerate(sorted_users[:5]):
            try:
                user = self.bot.get_chat(user_id)
                username = f"@{user.username}" if user.username else f"User {user_id}"
            except Exception:
                username = f"User {user_id}"
                
            top_receivers += f"{i+1}. {username} - *{count}* successful OTPs\n"
            
        top_receivers += "---------------------------------\n"
        self.bot.send_message(message.chat.id, top_receivers, parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard())

    # --- ADMIN NEXT STEP HANDLERS ---
    
    def ask_broadcast_message(self, message):
        msg = self.bot.send_message(message.chat.id, "📝 Send the message you want to broadcast to users:", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        self.bot.register_next_step_handler(msg, self.broadcast_message)

    def broadcast_message(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
        
        if not message.text:
            self.bot.send_message(message.chat.id, "❌ Please send **only a text message** for broadcast.", reply_markup=self._get_admin_panel_keyboard())
            return
            
        users = self.dm.read_all_users()
        success, failed = 0, 0
        
        for uid in users:
            try:
                self.bot.send_message(uid, message.text)
                success += 1
            except:
                failed += 1
                
        self.bot.send_message(message.chat.id, f"✅ Successfully sent to: {success} users\n❌ Failed to send to: {failed} users", reply_markup=self._get_admin_panel_keyboard())

    def ask_country_name(self, message):
        msg = self.bot.send_message(message.chat.id, "Send the name of the country you want to add:", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        self.bot.register_next_step_handler(msg, self.get_country_name)

    def get_country_name(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
        
        country = message.text.strip()
        if not country or len(country) < 2:
            self.bot.send_message(message.chat.id, "❌ Invalid country name. Please send a valid country name.", reply_markup=self._get_admin_panel_keyboard())
            return
            
        msg = self.bot.send_message(message.chat.id, f"Send a CSV file containing numbers for {country}:", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        self.bot.register_next_step_handler(msg, self.save_country_file, country)

    def save_country_file(self, message, country):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return

        if not message.document:
            self.bot.send_message(message.chat.id, "❌ No file was sent. Please send a CSV file.", reply_markup=self._get_admin_panel_keyboard())
            return
            
        try:
            file_info = self.bot.get_file(message.document.file_id)
            downloaded = self.bot.download_file(file_info.file_path)
            file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
            
            # Save file
            with self.dm._lock:
                with open(file_path, "wb") as f:
                    f.write(downloaded)
                
            # Count numbers
            total_added = self.dm.count_country_numbers(country)
                
            self.bot.send_message(message.chat.id, f"✅ Country {country} added with {total_added} numbers.", reply_markup=self._get_admin_panel_keyboard())
            
            # Send Broadcast Message
            flag = self._get_flag(country)
            broadcast_text = (
                "🚨 *New Number Added!!*\n\n"
                f"**Country:** {country} - {flag}\n"
                f"**Capacity:** `{total_added}`\n\n"
                "All Numbers are *New and Fresh*."
            )
            
            for uid in self.dm.read_all_users():
                try:
                    self.bot.send_message(uid, broadcast_text, parse_mode="Markdown")
                except:
                    pass
                    
        except Exception as e:
            self.bot.send_message(message.chat.id, f"❌ Error saving file: {str(e)}", reply_markup=self._get_admin_panel_keyboard())
            print(f"File save error: {e}")

    def delete_country_step(self, message):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        countries = [f.replace(".csv", "") for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
        
        if not countries:
            self.bot.send_message(message.chat.id, "❌ No countries to delete.", reply_markup=self._get_admin_panel_keyboard())
            return
            
        for country in countries:
            markup.add(country)
        markup.add(CANCEL_BUTTON)
            
        self.bot.send_message(message.chat.id, "Choose the country you want to delete:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.delete_country_file)

    def delete_country_file(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
            
        country = message.text.strip()
        file_path = os.path.join(DATA_FOLDER, f"{country}.csv")
        
        if os.path.exists(file_path):
            try:
                with self.dm._lock:
                    os.remove(file_path)
                self.bot.send_message(message.chat.id, f"✅ Country {country} deleted.", reply_markup=self._get_admin_panel_keyboard())
            except Exception as e:
                self.bot.send_message(message.chat.id, f"❌ Error deleting country {country}. Error: {e}", reply_markup=self._get_admin_panel_keyboard())
        else:
            self.bot.send_message(message.chat.id, "❌ File not found.", reply_markup=self._get_admin_panel_keyboard())

    def ask_traffic_name(self, message):
        msg = self.bot.send_message(message.chat.id, "Send the name of the traffic (e.g., Bangladesh, India):", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        self.bot.register_next_step_handler(msg, self.add_traffic)

    def add_traffic(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
            
        traffic_name = message.text.strip()
        traffic = self.dm.load_traffic()
        
        if traffic_name in traffic:
            self.bot.send_message(message.chat.id, f"❌ Traffic '{traffic_name}' already exists.", reply_markup=self._get_admin_panel_keyboard())
            return
            
        traffic.append(traffic_name)
        self.dm.save_traffic(traffic)
        self.bot.send_message(message.chat.id, f"✅ Traffic '{traffic_name}' added successfully.", reply_markup=self._get_admin_panel_keyboard())

    def delete_traffic_step(self, message):
        traffic = self.dm.load_traffic()
        if not traffic:
            self.bot.send_message(message.chat.id, "❌ No traffic to delete.", reply_markup=self._get_admin_panel_keyboard())
            return
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for t_name in traffic:
            markup.add(t_name)
        markup.add(CANCEL_BUTTON)
            
        self.bot.send_message(message.chat.id, "Choose the traffic you want to delete:", reply_markup=markup)
        self.bot.register_next_step_handler(message, self.delete_traffic_item)

    def delete_traffic_item(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
        
        traffic_name = message.text.strip()
        traffic = self.dm.load_traffic()
        
        if traffic_name in traffic:
            traffic.remove(traffic_name)
            self.dm.save_traffic(traffic)
            self.bot.send_message(message.chat.id, f"✅ Traffic '{traffic_name}' deleted.", reply_markup=self._get_admin_panel_keyboard())
        else:
            self.bot.send_message(message.chat.id, "❌ Traffic not found.", reply_markup=self._get_admin_panel_keyboard())

    def ask_monitor_group_id(self, message):
        msg = self.bot.send_message(message.chat.id, "Send the *Group ID* (e.g., -100xxxxxxxxxx) or *Group Username* (@username) to add for OTP monitoring:", parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard_only_cancel())
        self.bot.register_next_step_handler(msg, self.add_monitor_group)

    def add_monitor_group(self, message):
        if message.from_user.id not in ADMIN_IDS: return 
        
        if message.text == CANCEL_BUTTON:
            self.admin_panel(message)
            return
        
        input_id = message.text.strip()
        groups = self.dm.load_monitor_groups()
        group_identifier = input_id
        
        try:
            if input_id.startswith('-100') or input_id.startswith('-'):
                group_identifier = int(input_id)
            elif not input_id.startswith('@'):
                group_identifier = '@' + input_id
        
        except ValueError:
            if not input_id.startswith('@'):
                group_identifier = '@' + input_id
        
        all_groups = OTP_MONITOR_GROUPS + groups
        is_duplicate = False
        for existing_group in all_groups:
            if str(existing_group).strip() == str(group_identifier).strip():
                is_duplicate = True
                break
                
        if not is_duplicate:
            groups.append(group_identifier)
            self.dm.save_monitor_groups(groups)
            self.bot.send_message(message.chat.id, f"✅ Monitor Group `{group_identifier}` added successfully.", parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard())
        else:
            self.bot.send_message(message.chat.id, f"❌ Monitor Group `{group_identifier}` already exists.", parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard())

    def show_countries(self, message):
        countries = [f.replace(".csv", "") for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
        if countries:
            country_list = "\n".join(f"• {c} {self._get_flag(c)}" for c in countries)
            self.bot.send_message(message.chat.id, "🌍 Available Countries:\n" + country_list, parse_mode="Markdown", reply_markup=self._get_admin_panel_keyboard())
        else:
            self.bot.send_message(message.chat.id, "❌ No countries available.", reply_markup=self._get_admin_panel_keyboard())

    # --- HANDLER IMPLEMENTATION (Inline Callbacks) ---

    def handle_verify_again(self, call):
        user_id = call.from_user.id
        if self._is_subscribed(user_id):
            self.bot.answer_callback_query(call.id, "✅ Verification successful!")
            self.bot.send_message(call.message.chat.id,
                                 "💬 *Welcome ITACHI UCHIHA OTP* ✅\n🔐 *We help to receve otp*", 
                                 parse_mode="Markdown", 
                                 reply_markup=self._get_main_menu_keyboard())
        else:
            self.bot.answer_callback_query(call.id, "❌ You need to join all channels first!")
            
    def handle_copy_link_callback(self, call):
        """Handles inline button callbacks for copying the referral link."""
        if call.data.startswith("copy_link_"):
            # Acknowledges the copy link click (Telegram handles actual copying on long press of the link in the message)
            self.bot.answer_callback_query(call.id, text="Link Copied! (Please click and hold the link in the message above to copy it manually)", show_alert=False)


    def handle_get_or_change_number(self, call):
        if not self._is_subscribed(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ You need to join our channels first!")
            return
            
        country = call.data.split("_", 1)[1]
        success = self._assign_number_core(chat_id=call.message.chat.id, message_id=call.message.message_id, country=country)
        
        if not success:
            self.bot.answer_callback_query(
                callback_query_id=call.id,
                text="⌛ Wait a moment before requesting again.", 
                show_alert=True
            )

    def handle_change_country_menu(self, call):
        if not self._is_subscribed(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ You need to join our channels first!")
            return

        welcome_text = ("🌍 *Choose Your Country* 👇")
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        
        for filename in os.listdir(DATA_FOLDER):
            if filename.endswith(".csv"):
                country = filename.replace(".csv", "")
                stock_count = self.dm.count_country_numbers(country)
                button_text = f"{self._get_flag(country)} {country} ({stock_count})"
                keyboard.add(types.InlineKeyboardButton(text=button_text, callback_data=f"country_{country}"))

        self.bot.edit_message_text(chat_id=call.message.chat.id, 
                                message_id=call.message.message_id,
                                text=welcome_text, 
                                parse_mode="Markdown",
                                reply_markup=keyboard)


    def handle_status_check(self, call):
        if not self._is_subscribed(call.from_user.id):
            self.bot.answer_callback_query(call.id, "❌ You need to join our channels first!")
            return

        # The number passed in the callback data (e.g., status_38651640579)
        number = call.data.split("_", 1)[1]
        number_user = self.dm.load_number_user_map()
        
        # CORE FIX: Check if the number is NOT in the active map (meaning it was fulfilled)
        if number not in number_user:
            self.bot.answer_callback_query(call.id, "✅ OTP Received! The number is no longer active. Check your private messages.")
        else:
            self.bot.answer_callback_query(call.id, "🔍 Still Waiting for OTP. Nothing received yet.")
        


    # --- HANDLER IMPLEMENTATION (Monitoring Logic) ---

    def monitor_otp_messages(self, message):
        """
        Monitors incoming messages from the specified groups for OTPs and matches 
        them using the visible part of the phone number.
        """
        if message.chat.type not in ["supergroup", "group"]:
            return

        # 1. Check if the message is from a monitored group ID
        all_monitor_groups = list(OTP_MONITOR_GROUPS)
        all_monitor_groups.extend(self.dm.load_monitor_groups()) 

        is_monitor_group = False
        for group_identifier in all_monitor_groups:
            if str(group_identifier).strip() == str(message.chat.id).strip():
                is_monitor_group = True
                break
            elif isinstance(group_identifier, str) and message.chat.username and message.chat.username.lower() == group_identifier.replace('@', '').lower():
                is_monitor_group = True
                break
            
        if not is_monitor_group:
            return

        text = message.text
        number_user = self.dm.load_number_user_map()
            
        # 2. Extract OTP
        otp = self._extract_otp(text)
        if not otp:
            return

        # 3. Extract visible number parts from the message (Masking Logic)
        # Regex to find sequences of 2 to 15 characters, including digits and asterisks
        # This covers formats like '****55' or '2267****74257'
        numbers_in_message = re.findall(r'\b[\d\*#\-+]{2,15}\b', text)
        
        
        for message_number_raw in numbers_in_message:
            
            # Clean the number: Remove spaces, hyphens, and plus signs
            message_number_clean = re.sub(r'[\s\-+]', '', message_number_raw)

            # CRITICAL FIX: Get only 2 to 9 trailing digits from the received number string.
            # This is the visible, unmasked part needed for matching.
            visible_part_match = re.search(r'(\d{2,9})$', message_number_clean)
            
            if not visible_part_match:
                continue
                
            visible_digits = visible_part_match.group(1)
            match_len = len(visible_digits)
            
            
            for stored_number, user_info in number_user.items():
        
                # 4. CRITICAL MATCHING: Check if the active (stored) full number ends with the visible part
                if len(stored_number) >= match_len:
                    if stored_number.endswith(visible_digits):
                        
                        # 5. Forward OTP
                        user_id = user_info["user_id"]
                        country = user_info["country"]

                        self._send_otp_to_user(user_id, stored_number, otp, country)

                        # Stop checking once a match is found and handled.
                        return 

# --- BOT START ---
if __name__ == "__main__":
    print(" ITACHI UCHIHA OTP Number Bot Run...")
    bot_instance = OTPBot(API_TOKEN)
    # NOTE: You MUST fully stop and restart your bot's running process 
    # after updating this code to see the changes applied.
    bot_instance.bot.infinity_polling(timeout=60, long_polling_timeout=60)
