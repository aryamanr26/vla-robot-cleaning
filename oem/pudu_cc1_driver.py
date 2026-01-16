from oem.robot_interface import RobotInterface
class PuduCC1Driver(RobotInterface):
    """
    Stub for Pudu CC1 Pro driver.
    In production, this would use PUDU Link REST/WebSocket APIs.
    """

    def connect(self) -> bool:
        raise NotImplementedError("Pudu CC1 hardware not available in challenge")

    def navigate_to_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def start_cleaning(self, mode: str, params=None) -> bool:
        raise NotImplementedError

    def stop_cleaning(self) -> bool:
        raise NotImplementedError

    def get_status(self):
        raise NotImplementedError
