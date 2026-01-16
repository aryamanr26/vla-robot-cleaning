from oem.robot_interface import RobotInterface

class KeenonC40Driver(RobotInterface):
    """
    Stub for Keenon C40 driver.
    In production, this would use Keenon REST/WebSocket APIs.
    """

    def connect(self) -> bool:
        raise NotImplementedError("Keenon C40 hardware not available in challenge")

    def navigate_to_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def start_cleaning(self, mode: str, params=None) -> bool:
        raise NotImplementedError

    def stop_cleaning(self) -> bool:
        raise NotImplementedError

    def get_status(self):
        raise NotImplementedError