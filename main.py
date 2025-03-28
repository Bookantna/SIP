from client import call_ini
from server import server_ini

def serverIniOrClientIni():
    print("Options for SIP\n"
    "1) Setup server\n"
    "2) Setup client and call\n")
    selected_option = str(input("Select option: "))
    return selected_option

try:
    selected_option = serverIniOrClientIni()

    if selected_option == "1":
        server_ip = str(input("Server IP: "))
        server_ini(server_ip)
    elif selected_option == "2":
        server_ip = str(input("Server IP: "))
        ip = str(input("Your IP: "))
        end_ip = str(input("Callee IP: "))
        call_ini(SIP_SERVER=server_ip, CLIENT_IP=ip, end_client=end_ip)
    
except Exception as e:
    print(f"❌ Error: {e}")