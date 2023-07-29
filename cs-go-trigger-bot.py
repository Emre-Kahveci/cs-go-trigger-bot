import pymem
from time import sleep
import win32api

# Offsets
offsets = {
    'localPlayer': 0xDEA98C,
    'entityList': 0x4DFFF7C,
    'forceAttack': 0x322DDE8,
    'health': 0x100,
    'teamNum': 0xF4,
    'crosshairId': 0x11838 
}

def triggerBot() -> None:
    sleep(.01)
    pm = pymem.Pymem('csgo.exe') # find csgo.exe
    
    client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll # access client.dll

    while True:

        # if the "x" key is pressed do not run 
        if win32api.GetAsyncKeyState(0x58):
            continue

        localPlayer = pm.read_uint(client + offsets["localPlayer"])
        localHealth = pm.read_int(localPlayer + offsets["health"])

        # if the local player is dead
        if not localHealth:
            continue

        crosshairId = pm.read_int(localPlayer + offsets['crosshairId'])

        # competitors take values between 1 and 64
        if not crosshairId or crosshairId > 64:
            continue

        player = pm.read_uint(client + offsets['entityList'] + (crosshairId - 1) * 0x10)

        # if the opponent is alive
        if not pm.read_int(player + offsets['health']):
            continue

        # If not from your team
        if pm.read_uint(player + offsets["teamNum"]) == pm.read_uint(localPlayer + offsets["teamNum"]):
            continue
        
        # shoot
        pm.write_uint(client + offsets['forceAttack'], 6)
        sleep(.05)
        pm.write_uint(client + offsets['forceAttack'], 4)


if __name__ == "__main__":
    triggerBot()