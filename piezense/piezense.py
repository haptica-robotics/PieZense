#!/usr/bin/env python3

import asyncio
import bleak

"""
A class for controlling a collection of PieZense pneumatic systems.
"""
class PieZense:
    def __init__(self, scale_factor: float = 1.0):
        """
        Common scale_factor values:
        - 1.0       : millibar
        - 100.0     : Pa
        - 0.1       : kPa
        - 0.001     : bar (atmosphere)
        - 0.0145038 : PSI
        - 0.750062  : mmHg
        - 10.19716  : mmH2O
        @param scale_factor: scaling factor for pressure readings (default 1.0)
        """
        self._scale_factor = scale_factor
        self._systems = []
        self._reconnect_task = None
        self._pressures = []
    class _System:
        """
        A class representing a single PieZense system, used internally by the PieZense library
        """
        def __init__(self, system_name: str, channel_count: int):
            self.system_name = system_name
            self.channel_count = channel_count
            self.client = None
    def addSystem(self, system_name: str, channel_count: int) -> int:
        """ 
        register a PieZense system that you want to connect to

        @param system_name: Bluetooth name of the PieZense system
        @param channel_count: Number of channels in the system, in the future this second argument may become optional
        @return: index of the registered system
        """
        return self._addSystem(system_name, channel_count)
    def _addSystem(self, system_name, channel_count) -> int:
        self._systems.append(self._System(system_name, channel_count))
        self._pressures.append([0]*channel_count)
        return len(self._systems) - 1
    def connect(self):
        """
        start the process of connecting to all registered systems

        @note: call this function just once

        use isEverythingConnected() to tell when all registered systems have become connected
        """
        self._reconnect_task = asyncio.run(self._connect())
    async def _connect(self):
        while(True):
            for i, system in enumerate(self._systems):
                if not system.client or not system.client.is_connected: # never connected or disconnected
                    print(f"Need device: {system.system_name}")
                    device = await bleak.BleakScanner.find_device_by_name(system.system_name)
                    print(f"Scanned for device: {system.system_name}")
                    if device:
                        print(f"Found device: {device}")
                        system.client = bleak.BleakClient(device)
                        await system.client.connect()
                        if system.client.is_connected:
                            print(f"Connected to device: {system.system_name}")
                            services=system.client.services
                            print(f"Services: {services}")
                        else:
                            print(f"Failed to connect to device: {system.system_name}")
                            system.client = None
                await asyncio.sleep(10)

    def isEverythingConnected(self) -> bool:
        """
        check if all registered systems are currently connected
        @return: bool: True if all systems are connected, False otherwise
        """
        return all( (system.client and system.client.is_connected) for system in self._systems)
    
    def sendSetpoint(self, system_num: int, channel_num: int, setpoint: float):
        """
        send a pressure setpoint to a channel of a system

        @param system_num: index of the system to send the setpoint to (later this may support system names too)
        @param channel_num: index of the channel to send the setpoint to
        @param setpoint: pressure setpoint
        """
        pass
    def sendSetpointBatch(self, setpoint_batch: list):
        """
        send a batch of pressure setpoints to multiple systems and channels

        @param setpoint_batch: a list of tuples, each containing (system_num (int), channel_num (int), setpoint (float))

        example: [ (0, 0, 1013), (0, 1, 500), (1, 0, 750) ]
        """
        pass

    def getPressureReadings(self) -> list:
        """
        get the latest pressure readings from all connected systems
        @return: list: a list of lists, where each inner list contains the pressure readings for a system
        """
        return self._pressures
    
    def setCallback(self, callback_function):
        """
        set a callback function to be called when new pressure data is received
        @param callback_function: a function that takes three arguments: system_num (int) and pressure_data (list)
        """
        pass
    
    def addForwarding(self, source_system_num: int, source_channel_num: int, target_system_num: int, target_channel_num: int, forwarding_function):
        """
        configure pressure forwarding from one channel to another

        @param source_system_num: index of the source system
        @param source_channel_num: index of the source channel
        @param target_system_num: index of the target system
        @param target_channel_num: index of the target channel
        @param forwarding_function: a function that takes a pressure value and returns a modified pressure value (for example lambda x: 4*(x-1100)+1100)
        """
        pass

    def addForwardingBatch(self, forwarding_batch: list):
        """
        configure multiple pressure forwardings in a batch

        @param forwarding_batch: a list of tuples, each containing (source_system_num (int), source_channel_num (int), target_system_num (int), target_channel_num (int), forwarding_function (function))
        """
        pass

    def stopForwarding(self, source_system_num: int, source_channel_num: int, target_system_num: int, target_channel_num: int):
        """
        stop pressure forwarding from a channel to a channel

        @param source_system_num: index of the source system
        @param source_channel_num: index of the source channel
        @param target_system_num: index of the target system
        @param target_channel_num: index of the target channel
        """
        pass

    def clearAllForwarding(self):
        """
        clear all pressure forwarding configurations
        """
        pass

    def sendConfig(self, system_num: int, channel_num: int, config_data: dict):
        """
        configure a channel of a system
        @param system_num: index of the system to configure (later this may support system names too)
        @param channel_num: index of the channel to configure
        @param config_data: configuration data to send

        config_data example {"set_act_mode": 1, "set_pid_Pvalues_p": 0.5}
        """
        pass

    def sendConfigBatch(self, config_data_batch: list):
        """
        send a batch of configuration data to multiple systems and channels

        @param config_data_batch: a list of tuples, each containing (system_num (int), channel_num (int), config_data (dict))

        example: [ (0, 0, {"set_act_mode": 1}), (0, 1, {"set_act_mode": 0}), (1, 0, {"set_act_mode": 1}) ]
        """
        pass

    def setMode(self, mode: dict):
        """
        Set the operating mode of the PieZense systems.

        @param mode: dictionary describing mode actions

        The mode dict may contain keys:
          - "reset_config": config_data_batch
          - "setpoints": setpoint_batch
          - "wait_time": seconds
          - "forwarding": forwarding_batch
          - "final_config": config_data_batch

        setMode performs the following steps:
          1. Clears all forwarding.
          2. Sends the "reset_config" set of configuration changes (e.g. set actuator mode / default loop params).
          3. Waits for "wait_time" seconds.
          4. Adds the new set of channel forwardings.
          5. Sends the "final_config" set of configuration changes.
        """
        pass


# """This module provides the PieZense class for interfacing with PieZense pneumatic systems via Bluetooth Low Energy (BLE)."""
# class PieZense:
#     def __init__(self):
#         self.system_client_list=[] # list of BleakClient objects
    
#     """Connect to multiple PieZense systems by their names."""
#     def connect_to_systems(self, system_name_list_input):
#         self.system_name_list = system_name_list_input
#         self.num_systems = len(self.system_name_list)
#         for i, _ in enumerate(self.system_name_list):
#             self.system_client_list.append(None)

#         asyncio.run(self.reconnect_to_systems())

#     async def reconnect_to_systems(self):
#         while(True):
#             for i, system_name in enumerate(self.system_name_list):
#                 if self.system_client_list[i] is None: # connect
#                     print(f"Need device: {system_name}")
#                     device = await bleak.BleakScanner.find_device_by_name(system_name)
#                     print(f"Scanned for device: {system_name}")
#                     if device:
#                         print(f"Found device: {device}")
#                         self.system_client_list[i] = bleak.BleakClient(device)
#                         # self.system_client_list[i].set_disconnected_callback(self.generate_disconnect_callback(i, system_name))
#                         await self.system_client_list[i].connect()
#                         if self.system_client_list[i].is_connected:
#                             print(f"Connected to device: {system_name}")
#                             services=await self.system_client_list[i].services
#                             print(f"Services: {services}")

#                             for service in services:
#                                 for char in service.characteristics:
#                                     if "notify" in char.properties:
#                                         print(f"[{system_name}] Subscribing to {char.uuid}")
#                                         await self.system_client_list[i].start_notify(
#                                             char.uuid,
#                                             lambda sender, data, idx=i: self.notification_handler(idx, sender, data)
#                                         )
#                         else:
#                             print(f"Failed to connect to device: {system_name}")
#                             self.system_client_list[i] = None

#                 else:
#                     print(f"Device not found, will retry: {system_name}")
#                 await asyncio.sleep(11)

#     def notification_handler(self, device_index, sender, data):
#         expected_without_ts = FOLLOWER_COUNT * 2
#         pressure_data = data[:expected_without_ts]
#         num_followers = len(pressure_data) // 2 # // does integer division
#         for follower_id in range(num_followers):
#             low_byte = pressure_data[follower_id * 2]
#             high_byte = pressure_data[follower_id * 2 + 1]
#             pressure_value = (high_byte << 8) | low_byte
#             print(f"Device {device_index}, Follower {follower_id}, Pressure: {pressure_value} Pa")
