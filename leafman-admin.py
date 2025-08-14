# leafman-admin.py
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

    >> Leafman Admin Console v1.0 <<
"""

def pretty_print_table(data_list, headers):
    if not data_list: print("[*] No data to display."); return
    header_keys = list(headers.keys())
    def get_nested_value(row, key):
        if '.' not in key: return row.get(key, "")
        value = row
        for part in key.split('.'):
            if isinstance(value, dict): value = value.get(part)
            else: return ""
        return value if value is not None else ""
    col_widths = {key: len(str(header)) for key, header in headers.items()}
    for row in data_list:
        for key in header_keys:
            value = get_nested_value(row, key)
            col_widths[key] = max(col_widths[key], len(str(value)))
    header_line = " | ".join(headers[key].ljust(col_widths[key]) for key in header_keys)
    print("\n" + header_line); print("-" * len(header_line))
    for row in data_list:
        row_values = [str(get_nested_value(row, key)).ljust(col_widths[key]) for key in header_keys]
        print(" | ".join(row_values))
    print()

class LeafmanAdminCLI(cmd.Cmd):
    intro = BANNER + "\nWelcome, Admin! Type 'help' or '?' to list commands.\n"
    prompt = '(leafman-admin) '
    
    def __init__(self, api_base_url):
        super().__init__(); self.api_base_url = api_base_url; self.token = None; self.current_user = None

    def _make_request(self, method, endpoint, data=None, is_json=True):
        headers = {'Authorization': f'Bearer {self.token}'} if self.token else {}
        url = f"{self.api_base_url}{endpoint}"; kwargs = {'headers': headers}
        if data: kwargs['json' if is_json else 'data'] = data
        try:
            response = requests.request(method.upper(), url, **kwargs); response.raise_for_status()
            return response.json() if response.text else {}
        except requests.exceptions.HTTPError as e:
            print(f"\n[-] API Error ({e.response.status_code}):")
            try: print(f"[-] Details: {e.response.json().get('detail', 'N/A')}")
            except json.JSONDecodeError: print(f"[-] Raw Response: {e.response.text[:200]}")
            return None
        except requests.exceptions.RequestException as e: print(f"\n[-] Connection Error: {e}"); return None

    def _require_admin(self):
        is_admin = self.current_user and self.current_user.get('role') == 'Admin'
        if not is_admin: print("[-] Admin privileges required.")
        return is_admin

    def do_login(self, arg):
        args = arg.split();
        if not 1 <= len(args) <= 2: print("[-] Usage: login <email> [password]"); return
        email = args[0]; password = args[1] if len(args) == 2 else getpass("Password: ")
        form_data = {'username': email, 'password': password}
        token_data = self._make_request('POST', '/auth/token', data=form_data, is_json=False)
        if token_data and 'access_token' in token_data:
            self.token = token_data['access_token']; self.current_user = self._make_request('GET', '/users/me')
            if self.current_user and self.current_user.get('role') == 'Admin':
                print("\n[+] Admin login successful."); self.prompt = f'(admin:{email}) '
            else: print("\n[-] User is not an Admin or failed to fetch profile."); self.do_logout(None)
        else: print("\n[-] Login failed. Check credentials.")

    def do_logout(self, arg):
        self.token = None; self.current_user = None; self.prompt = '(leafman-admin) '; print("[*] Logged out.")

    def do_whoami(self, arg):
        if not self.token: print("[-] Not logged in."); return
        pretty_print_table([self.current_user], {"user_id": "ID", "first_name": "First Name", "last_name": "Last Name", "email": "Email", "role": "Role"})

    def do_show(self, arg):
        """Display info. Usage: show [pending|all_requests|balance|departments|leavetypes]"""
        if not self._require_admin(): return
        
        # THE FIX: Added 'reason' to the headers for pending and all_requests
        headers_map = {
            "pending": {
                "request_id": "ID", "user.first_name": "First Name", "start_date": "Start",
                "end_date": "End", "status": "Status", "reason": "Reason"
            },
            "all_requests": {
                "request_id": "ID", "user.first_name": "First Name", "leave_type.name": "Type",
                "start_date": "Start", "end_date": "End", "status": "Status", "reason": "Reason"
            },
            "leavetypes": {
                "leave_type_id": "ID", "name": "Leave Type", "annual_quota": "Quota", "carry_forward": "Carry Fwd"
            },
            "departments": {
                "department_id": "ID", "name": "Department Name"
            },
            "balance": {
                "leave_type.name": "Leave Type", "year": "Year",
                "balance_days": "Total", "used_days": "Used",
            },
        }
        
        endpoint_map = {
            "pending": "/admin/leave-requests?status=Pending",
            "all_requests": "/admin/leave-requests",
            "leavetypes": "/leave-requests/types",
            "departments": "/admin/departments/",
            "balance": "/users/me/balances",
        }
        
        # Adding a simple check for personal requests since it's not in the main admin list
        if arg == "requests":
            print("[!] Note: 'show requests' shows your personal request history.")
            personal_headers = {"request_id": "ID", "leave_type.name": "Type", "start_date": "Start", "end_date": "End", "status": "Status", "reason": "Reason"}
            response = self._make_request('GET', '/leave-requests/')
            if response is not None: pretty_print_table(response, personal_headers)
            return

        if arg not in endpoint_map:
            print(f"[-] Unknown 'show' command: {arg}. See 'help show'.")
            return
            
        response = self._make_request('GET', endpoint_map[arg])
        if response is not None:
            pretty_print_table(response, headers_map[arg])

            
    def help_show(self):
        print("\nDisplay information. Usage: show <option>")
        print("  pending      - All PENDING leave requests."); print("  all_requests - ALL leave requests in the system.")
        print("  leavetypes   - All configured leave types."); print("  departments  - All configured departments.")
        print("  balance      - Your personal leave balance.\n")

    def do_adduser(self, arg):
        """[Admin] Create a new employee user."""
        if not self._require_admin(): return
        try:
            email=input("Email: ");password=getpass("Password: ");first_name=input("First Name: ");last_name=input("Last Name: ")
            join_date=input("Join Date (YYYY-MM-DD): ");role=input("Role [Employee]: ") or "Employee";dept_id=int(input("Department ID [1]: ") or "1")
            data={"first_name":first_name,"last_name":last_name,"email":email,"password":password,"join_date":join_date,"role":role,"department_id":dept_id}
            response=self._make_request('POST','/admin/users',data=data)
            if response: print("\n[+] User created successfully!"); pretty_print_table([response], {"user_id":"ID","first_name":"First","last_name":"Last","email":"Email"})
        except Exception as e: print(f"\n[-] Error: {e}")

    def do_approve(self, arg):
        """[Admin] Approve a request. Usage: approve <id>"""
        if not self._require_admin(): return
        try: 
            request_id=int(arg); note=input("Note (optional): "); data={"status":"Approved","approval_note":note}
            response=self._make_request('PATCH',f'/admin/leave-requests/{request_id}',data=data);
            if response: print(f"\n[+] Request {request_id} approved.")
        except ValueError: print("[-] Invalid ID.")

    def do_reject(self, arg):
        """[Admin] Reject a request. Usage: reject <id>"""
        if not self._require_admin(): return
        try: 
            request_id=int(arg); note=input("Reason (required): ");
            if not note: print("[-] Reason required."); return
            data={"status":"Rejected","approval_note":note}; response=self._make_request('PATCH',f'/admin/leave-requests/{request_id}',data=data)
            if response: print(f"\n[+] Request {request_id} rejected.")
        except ValueError: print("[-] Invalid ID.")

    def do_add_leavetype(self, arg):
        """[Admin] Create a new leave type."""
        if not self._require_admin(): return
        try: 
            name=input("Name: "); quota=float(input("Annual Quota: ")); carry_fwd=(input("Carry forward? (y/n) [n]: ") or "n").lower()=='y'
            data={"name":name,"annual_quota":quota,"carry_forward":carry_fwd}; response=self._make_request('POST','/admin/leave-types',data=data)
            if response: print("\n[+] Leave Type created!"); pretty_print_table([response],{"leave_type_id":"ID","name":"Name","annual_quota":"Quota"})
        except Exception as e: print(f"\n[-] Error: {e}")

    def do_add_dept(self, arg):
        """[Admin] Create a new department."""
        if not self._require_admin(): return
        try: 
            name=input("Department Name: "); response=self._make_request('POST','/admin/departments',data={"name":name})
            if response: print("\n[+] Department created!"); pretty_print_table([response],{"department_id":"ID","name":"Name"})
        except Exception as e: print(f"\n[-] Error: {e}")

    def do_exit(self, arg):
        """Exit the Admin Console."""
        print("Exiting Admin Console."); return True
        
    def do_EOF(self, arg):
        """Handle Ctrl-D to exit."""
        print(); return self.do_exit(arg)

if __name__ == '__main__':
    load_dotenv(); api_url = os.getenv('LEAFMAN_API_URL', 'http://127.0.0.1:8000')
    try: LeafmanAdminCLI(api_url).cmdloop()
    except KeyboardInterrupt: print("\n[*] Aborted by user. Exiting.")