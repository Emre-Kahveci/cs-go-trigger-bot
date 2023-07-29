import pymem
from time import sleep
import win32api
import requests

def get_offset(url = "https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json"):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check if the request was successful
        json_data = response.json()
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching the JSON file: {e}")
        return None

def triggerBot(offsets = get_offset()) -> None:
    sleep(.01)
    pm = pymem.Pymem('csgo.exe') # find csgo.exe
    
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll # access client.dll

    while True:

        # if the "x" key is pressed do not run 
        if win32api.GetAsyncKeyState(0x58):
            continue

        localPlayer = pm.read_uint(client + offsets["signatures"]["dwLocalPlayer"])

        # if the local player is dead
        if not pm.read_int(localPlayer + offsets["netvars"]["m_iHealth"]):
            continue

        crosshairId = pm.read_int(localPlayer + offsets["netvars"]['m_iCrosshairId'])

        # competitors take values between 1 and 64
        if not crosshairId or crosshairId > 64:
            continue

        player = pm.read_uint(client + offsets["signatures"]['dwEntityList'] + (crosshairId - 1) * 0x10)

        # if the opponent is alive
        if not pm.read_int(player + offsets["netvars"]["m_iHealth"]):
            continue

        # If not from your team
        if pm.read_uint(player + offsets["netvars"]["m_iTeamNum"]) == pm.read_uint(localPlayer + offsets["netvars"]["m_iTeamNum"]):
            continue
        
        # shoot
        pm.write_uint(client + offsets["signatures"]['dwForceAttack'], 6)
        sleep(.05)
        pm.write_uint(client + offsets["signatures"]['dwForceAttack'], 4)


if __name__ == "__main__":
    triggerBot()