
import pysmartthings
import aiohttp
import asyncio

import pymyq
import venstar
from keys import *

OPEN_CLOSE = False
lights = ['Pineapple', 'Dining Room Table', 'Garage Light', 'Bedroom Light']
LINE_BREAK = '*********************************'
SYSTEM_CHOICES = f'{LINE_BREAK}\n' \
                 'Which would you like to control?\n' \
                 '1. Lights\n' \
                 '2. Garage\n' \
                 f'3. Thermostat\n' \
                 f'4. Solar\n{LINE_BREAK}\n' \
                 'Choice: '
VENSTAR_CHOICES = f'{LINE_BREAK}\n' \
                  'What would you like to do?\n' \
                  '1. Toggle Fan\n' \
                  '2. Toggle Heater\n' \
                  '3. Toggle AIRCON\n' \
                  f'4. Cancel\n{LINE_BREAK}\n' \
                  'Choice: '
MAIN_LOOP_CHOICE = 'Would you like to keep going?\n0 = NO 1 = YES\nChoice: '


async def change_garage(request):

    async with aiohttp.ClientSession() as websession:
        # Create an API object:
        api = await pymyq.login(myqemail, myqpassword, websession)

        # The first cover is the garage door, so set that to the device
        device = list(api.covers.values())[0]

        if request == 'close':
            # Make sure we do in fact have the garage door, make sure it is open, and online
            if device.name == 'Garage Door' and device.state == 'open' and device.online:
                await device.close()
                await asyncio.sleep(15)
            else:
                print('Garage is closed already')
        if request == 'open':
            # Make sure we do in fact have the garage door, make sure it is open, and online
            if device.name == 'Garage Door' and device.state == 'closed' and device.online:
                await device.open()
                await asyncio.sleep(15)
            else:
                print('Garage is open already')

                # _LOGGER.info("---------")
                # _LOGGER.info("Device %s: %s", idx + 1, device.name)
                # _LOGGER.info("Device Online: %s", device.online)
                # _LOGGER.info("Device ID: %s", device.device_id)
                # _LOGGER.info("Parent Device ID: %s", device.parent_device_id)
                # _LOGGER.info("Device Family: %s", device.device_family)
                # _LOGGER.info("Device Platform: %s", device.device_platform)
                # _LOGGER.info("Device Type: %s", device.device_type)
                # _LOGGER.info("Firmware Version: %s", device.firmware_version)
                # _LOGGER.info("Open Allowed: %s", device.open_allowed)
                # _LOGGER.info("Close Allowed: %s", device.close_allowed)
                # _LOGGER.info("Current State: %s", device.state)


async def change_devices(target, state):
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, SMARTTHINGS_TOKEN)
        devices = await api.devices()
        for device in devices:
            if device.label == target:
                result = await device.command("main", "switch", state)
                assert result == True


async def print_devices():
    async with aiohttp.ClientSession() as session:
        api = pysmartthings.SmartThings(session, SMARTTHINGS_TOKEN)
        devices = await api.devices()
        for device in devices:
            print("{}: {}".format(device.device_id, device.label))


def venstar_options():
    info, sensors, runtimes = venstar.get_info(venstar_ip)
    state = {'fan': info['fanstate'], 'hvac': info['mode'],
             'heattemp': info['heattemp'], 'cooltemp': info['cooltemp']}
    print(LINE_BREAK)
    if state['hvac'] == 0:
        print('HVAC is currently OFF')
    elif state['hvac'] == 1:
        print(f'HVAC in HEATING mode and set to {state["heattemp"]}')
    elif state['hvac'] == 2:
        print(f'HVAC in COOLING mode and set to {state["cooltemp"]}')
    if state['fan'] == 0:
        print('HVAC fan is currently OFF')
    else:
        print('HVAC fan is currently RUNNING')

    for sensor in sensors:
        print(sensor['name'] + ': ', sensor['temp'])

    # After displaying status - user makes choice for what to change
    venstar_choice = input(VENSTAR_CHOICES)
    print(LINE_BREAK)
    if venstar_choice == '1':  # toggle fan
        if state['fan'] == 0:
            venstar.change_state(venstar_ip, state['hvac'], 1, state['heattemp'], state['cooltemp'])
            print('FAN ON')
        else:
            venstar.change_state(venstar_ip, state['hvac'], 0, state['heattemp'], state['cooltemp'])
            print('FAN OFF')
    elif venstar_choice == '2':  # Toggle heater
        if state['hvac'] == 0:
            venstar.change_state(venstar_ip, 1, state['fan'], state['heattemp'], state['cooltemp'])
            print(f'HEATER ON: SET TO {state["heattemp"]}')
        else:
            venstar.change_state(venstar_ip, 0, state['fan'], state['heattemp'], state['cooltemp'])
            print('SYSTEM OFF')
    elif venstar_choice == '3':  # Toggle AC
        if state['hvac'] == 0:
            venstar.change_state(venstar_ip, 2, state['fan'], state['heattemp'], state['cooltemp'])
            print(f'AIRCON ON: SET TO {state["cooltemp"]}')
        else:
            venstar.change_state(venstar_ip, 0, state['fan'], state['heattemp'], state['cooltemp'])
            print('SYSTEM OFF')
    print(LINE_BREAK)

def solar_options():
    pass

def main():
    loop = asyncio.get_event_loop()
    while True:
        system = input(SYSTEM_CHOICES)
        if system == '1':
            print(LINE_BREAK)
            for light in lights:
                print(f'{lights.index(light)+1}. {light}')
            print(LINE_BREAK)
            request = int(input('Select a light from above. (0 for none)'))
            print(LINE_BREAK)
            switch = int(input('1 for on, 0 for off: '))
            print(LINE_BREAK)
            if request != 0:
                if switch == 1:
                    switch = 'on'
                    print('SWITCHED ON')
                elif switch == 0:
                    switch = 'off'
                    print('SWITCHED OFF')
                loop.run_until_complete(change_devices(lights[request-1], switch))
            print(LINE_BREAK)
        elif system == '2':
            open_close = input('1 = open 0 = close\nChoice: ')
            if open_close == '0':
                loop.run_until_complete(change_garage('close'))
            else:
                loop.run_until_complete(change_garage('open'))
        elif system == '3':
            venstar_options()
        elif system == '4':
            solar_options()

        still_going = input(MAIN_LOOP_CHOICE)
        if still_going != '1':
            break


if __name__ == '__main__':
    main()
