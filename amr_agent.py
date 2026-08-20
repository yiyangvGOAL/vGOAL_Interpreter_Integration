from time import sleep

from ws4py.client.threadedclient import WebSocketClient
from json import dumps, loads

import logging


class AMR_Agent(WebSocketClient):
    def __init__(self, amr_id):
        conn_string = "ws://172.21.%i.90:9090/" % amr_id
        WebSocketClient.__init__(self, conn_string)
        self.received_status_dict = {"Position": "P0",
                                     "Docked": False,
                                     "Holding": True,
                                     "Battery": "L0",
                                     #"Charging": False,
                                     "Error": "None"}
        self.received_amcl_pose = ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0, 0.0])

    # ----- OVERRIDDEN WEBSOCKETCLIENT METHODS -----
    def opened(self):
        logging.info("client connection OPENED")
        self._subscribe_amragent_state()
        self._subscribe_amcl_pose()

    def closed(self, code, reason=None):
        logging.info("client connection CLOSED.")
        logging.debug("\tcode: {0}\n\treason={1}".format(code, reason))

    def received_message(self, message):
        # Read the JSON of the received message
        msg_json = loads(str(message))
        # Only react to messages published by the AMR
        if msg_json["op"] == "publish":
            # Now find out what topic we received information from
            if msg_json["topic"] == "/amragent/state":
                # update the status dictionary
                self.received_status_dict["Position"] = msg_json["msg"]["position"]
                self.received_status_dict["Docked"] = msg_json["msg"]["docked"]
                self.received_status_dict["Holding"] = msg_json["msg"]["holding"]
                self.received_status_dict["Battery"] = msg_json["msg"]["battery"]
                #self.received_status_dict["Charging"] = msg_json["msg"]["charging"]
                if msg_json["msg"]["error"] != "None":
                    self.received_status_dict["Error"] = msg_json["msg"]["error"][0:2]
                else:
                    self.received_status_dict["Error"] = "None"
                # currently output dict
                logging.info(self.received_status_dict)
            elif msg_json["topic"] == "/amcl_pose":
                # fill in the AMCL pose.position
                self.received_amcl_pose[0][0] = msg_json["msg"]["pose"]["pose"]["position"]["x"]
                self.received_amcl_pose[0][1] = msg_json["msg"]["pose"]["pose"]["position"]["y"]
                self.received_amcl_pose[0][2] = msg_json["msg"]["pose"]["pose"]["position"]["z"]
                # fill in the AMCL pose.orientation
                self.received_amcl_pose[1][0] = msg_json["msg"]["pose"]["pose"]["orientation"]["x"]
                self.received_amcl_pose[1][1] = msg_json["msg"]["pose"]["pose"]["orientation"]["y"]
                self.received_amcl_pose[1][2] = msg_json["msg"]["pose"]["pose"]["orientation"]["z"]
                self.received_amcl_pose[1][3] = msg_json["msg"]["pose"]["pose"]["orientation"]["w"]

    # ----- PUBLIC METHODS -----
    def send_action(self, action: str):
        """
            Method to publish to the /amragent/action topic the Agent_Node on the AMR subscribes to

        :param action: the action to send to the AMR.
                        Allowed values are "pickup", "dropoff", "charging" or "move(Px, Py)" with x,y in [1, 9]
        """
        msg = {"op": "publish",
               "topic": "/amragent/action",
               "msg": {
                   "data": action
               }}
        self.send(dumps(msg))

    def set_init_pose(self, init_position_array, init_orientation_array, place: str):
        """
            Method to set the initial pose of the AMR
        :param init_position_array: list holding the x, y and z coordinates of the initial pose.position
        :param init_orientation_array: list holding the x, y, z and w coordinates of the initial pose.orientation
        :param place: place (P1 through P9) of the initial pose
        """
        self._send_init_pose_msg(init_position_array, init_orientation_array)
        sleep(0.3)
        while not self._amcl_init_pose(init_position_array, init_orientation_array):
            self._send_init_pose_msg(init_position_array, init_orientation_array)
            sleep(0.3)
        while self.received_status_dict["Position"] != place:
            sleep(1)
    # ----- PRIVATE METHODS -----
    def _send_init_pose_msg(self, init_position_array, init_orientation_array):
        """
            Private method to send a PoseWithCovarianceStamped message to the
            /initialpose topic of the AMR to set its initial pose based on the
            provided pose.

        :param init_position_array: list holding the x, y and z coordinates of the initial pose.position
        :param init_orientation_array: list holding the x, y, z and w coordinates of the initial pose.orientation
        :return:
        """
        msg = {"op": "publish",
               "topic": "/initialpose",
               "msg": {"header": {"frame_id": "map"},
                       "pose": {"pose": {"position": {"x": init_position_array[0],
                                                      "y": init_position_array[1],
                                                      "z": init_position_array[2]},
                                         "orientation": {"x": init_orientation_array[0],
                                                         "y": init_orientation_array[1],
                                                         "z": init_orientation_array[2],
                                                         "w": init_orientation_array[3]},
                                         },
                                "covariance": [0.0] * 36
                                }
                       }
               }
        self.send(dumps(msg))

    def _amcl_init_pose(self, init_position_array, init_orientation_array):
        """
            Private method to determine if the received AMCL pose matches
            the required initial pose of the AMR

        :param init_position_array: list holding the x, y and z coordinates of the initial pose.position
        :param init_orientation_array: list holding the x, y, z and w coordinates of the initial pose.orientation
        :return: True/False based on the match beween the AMCL pose and provided initial pose
        """
        # First, compare the position [x,y,z]
        for i in range(0, len(init_position_array)):
            if abs(self.received_amcl_pose[0][i] - init_position_array[i]) > 0.001:
                return False
        # Second, compare the orientation [x,y,z,w]
        for j in range(0, len(init_orientation_array)):
            if abs(self.received_amcl_pose[1][j] - init_orientation_array[j] > 0.001):
                return False
        # Got here, so everything matches, can return True
        return True

    def _subscribe_amragent_state(self):
        """
            Private method to subscribe to the state updates produced by the Agent_Node on the AMR
        """
        msg = {"op": "subscribe",
               "topic": "/amragent/state",
               "throttle_rate": 1000}
        self.send(dumps(msg))

    def _subscribe_amcl_pose(self):
        """
            Private method to subscribe to the /amcl_pose topic of the AMR
        """
        msg = {"op": "subscribe",
               "topic": "/amcl_pose",
               "throttle_rate": 200}
        self.send(dumps(msg))
