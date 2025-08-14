import cmd
import os
import requests
import json
from getpass import getpass
from dotenv import load_dotenv

BANNER = """
                    .
                   .
                  .
,-. . . . . . . .,'-.
`~-=#################=-~'
   `~-=###########=-~'
       `~-=#####=-~'
           `~-=-~'

    >> Leafman Employee CLI v1.0 <<
"""

def pretty_print_table(data_list, headers):
    """
    Prints a list of dictionaries in a neat, tabular format.
    Handles nested keys using dot notation (e.g., 'leave_type.name').
    """
    if not data_list:
        print("[*] No data to display.")
        return

    header_keys = list(headers.keys())
    
    def get_nested_value(row, key):
        """Helper to retrieve a value from a potentially nested dictionary."""
        if '.' not in key:
            return row.get(key, "")
        
        value = row
        for part in key.split('.'):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return ""
        return value if value is not None else ""

    col_widths = {key: len(str(header)) for key, header in headers.items()}
    for row in data_list:
        for key in header_keys:
            value = get_nested_value(row, key)
            col_widths[key] = max(col_widths[key], len(str(value)))

    header_line = " | ".join(headers[key].ljust(col_widths[key]) for key in header_keys)
    print("\n" + header_line)
    print("-" * len(header_line))

    for row in data_list:
        row_values = []
        for key in header_keys:
            value = get_nested_value(row, key)
            row_values.append(str(value).ljust(col_widths[key]))
        print(" | ".join(row_values))
    print()

class LeafmanCLI(cmd.Cmd):
    intro = BANNER + "\nWelcome! Type 'help' or '?' to list commands.\n"
    prompt = '(leafman) '
    
    def __init__(self, api_base_url):
        super().__init__()
        self.api_base_url = api_base_url
        self.token = None
        self.current_user = None

    def _make_request(self, method, endpoint, data=None, is_json=True):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        url = f"{self.api_base_url}{endpoint}"
        kwargs = {'headers': headers}
        if data: kwargs['json' if is_json else 'data'] = data
        try:
            response = requests.request(method.upper(), url, **kwargs)
            response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            print(f"\n[-] API Error ({e.response.status_code}):")
            try: print(f"[-] Details: {e.response.json().get('detail', 'N/A')}")
            except json.JSONDecodeError: print(f"[-] Raw Response: {e.response.text[:200]}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"\n[-] Connection Error: {e}"); return None

    def do_login(self, arg):
        """Log in to the API. Usage: login <email> [password]"""
        args = arg.split();
        if not 1 <= len(args) <= 2: print("[-] Usage: login <email> [password]"); return
        email = args[0]; password = args[1] if len(args) == 2 else getpass("Password: ")
        form_data = {'username': email, 'password': password}
        token_data = self._make_request('POST', '/auth/token', data=form_data, is_json=False)
        if token_data and 'access_token' in token_data:
            self.token = token_data['access_token']
            self.current_user = self._make_request('GET', '/users/me')
            if self.current_user:
                print("\n[+] Login successful.")
                self.prompt = f'({email}) '
            else:
                print("\n[-] Failed to verify token or fetch profile.")
                self.do_logout(None)
        else:
            print("\n[-] Login failed. Check credentials.")

    def do_logout(self, arg):
        """Logs out of the current session."""
        self.token = None; self.current_user = None; self.prompt = '(leafman) '
        print("[*] Logged out.")

    def do_whoami(self, arg):
        """Displays currently logged-in user information."""
        if not self.token: print("[-] Not logged in."); return
        pretty_print_table([self.current_user], {
            "user_id": "ID", "first_name": "First Name", "last_name": "Last Name",
            "email": "Email", "role": "Role", "join_date": "Joined"
        })

    def do_show(self, arg):
        """
        Display your leave information.
        Usage:
          show balance    - Shows your current leave balances.
          show requests   - Shows your past leave requests.
        """
        if not self.token:
            print("[-] You are not logged in. Use 'login'.")
            return

        headers_map = {
            "balance": {
                "leave_type.name": "Leave Type", "year": "Year",
                "balance_days": "Total Allowance", "used_days": "Days Used",
            },
            "requests": {
                "request_id": "ID", "leave_type.name": "Type", "start_date": "Start Date",
                "end_date": "End Date", "total_days": "Days", "status": "Status"
            }
        }
        
        endpoint_map = {
            "balance": "/users/me/balances",
            "requests": "/leave-requests/",
        }

        if arg not in endpoint_map:
            print(f"[-] Unknown 'show' command: {arg}. See 'help show'.")
            return

        response = self._make_request('GET', endpoint_map[arg])

        if response is not None:
            pretty_print_table(response, headers_map[arg])

    def help_show(self):
        print("\nDisplay your leave information.")
        print("  show balance    - Shows your current leave balances.")
        print("  show requests   - Shows your past leave requests.\n")

    def do_apply(self, arg):
        """Interactively apply for a new leave request."""
        if not self.token: print("[-] Not logged in."); return
        print("\n[*] Fetching available leave types..."); leave_types = self._make_request('GET', '/leave-requests/types')
        if not leave_types: print("[-] Could not fetch leave types."); return
        print("[*] Please choose a leave type:"); [print(f"  ID: {lt['leave_type_id']} -> {lt['name']}") for lt in leave_types]
        print("\n[*] Starting new leave application...")
        try:
            leave_type_id = int(input("Enter Leave Type ID: "))
            if leave_type_id not in [lt['leave_type_id'] for lt in leave_types]: print(f"[-] Invalid ID '{leave_type_id}'."); return
            start_date = input("Start Date (YYYY-MM-DD): "); end_date = input("End Date (YYYY-MM-DD): ")
            reason = input("Reason (optional): ")
            data = {"leave_type_id": leave_type_id, "start_date": start_date, "end_date": end_date, "reason": reason}
            response = self._make_request('POST', '/leave-requests/', data=data)
            if response:
                print("\n[+] Leave request submitted successfully!")
                pretty_print_table([response], {
                    "request_id": "ID", "leave_type.name": "Type", "start_date": "Start Date",
                    "end_date": "End Date", "total_days": "Days", "status": "Status"
                })
        except ValueError: print("\n[-] Invalid input. ID must be an integer.")
        except Exception as e: print(f"\n[-] An unexpected error occurred: {e}")

    def do_exit(self, arg):
        """Exit the Leafman CLI."""
        print("Thank you for using Leafman. Have a great day!"); return True
        
    def do_EOF(self, arg):
        """Handle Ctrl-D to exit."""
        print(); return self.do_exit(arg)

if __name__ == '__main__':
    load_dotenv()
    api_url = os.getenv('LEAFMAN_API_URL', 'http://127.0.0.1:8000')
    try:
        LeafmanCLI(api_url).cmdloop()
    except KeyboardInterrupt:
        print("\n[*] Aborted by user. Exiting.")