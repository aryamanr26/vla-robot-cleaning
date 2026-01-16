from oem.robot_interface import RobotInterface

class GausiumOmnieDriver(RobotInterface):
    """
    Stub for Gausium Omnie driver.
    In production, this would use Gausium REST/WebSocket APIs.
    """

    def connect(self) -> bool:
        raise NotImplementedError("Gausium Omnie hardware not available in challenge")

    def navigate_to_node(self, node_id: str) -> bool:
        raise NotImplementedError

    def start_cleaning(self, mode: str, params=None) -> bool:
        raise NotImplementedError

    def stop_cleaning(self) -> bool:
        raise NotImplementedError

    def get_status(self):
        raise NotImplementedError
