from oem.robot_interface import RobotInterface

class MockRobot(RobotInterface):
    """
    Software-only mock robot used for simulation and testing.
    """

    def __init__(self):
        self.connected = False
        self.current_node = "dock"
        self.cleaning = False

    def connect(self) -> bool:
        print("[MOCK ROBOT] Connected")
        self.connected = True
        return True

    def navigate_to_node(self, node_id: str) -> bool:
        print(f"[MOCK ROBOT] Navigating to node: {node_id}")
        self.current_node = node_id
        return True

    def start_cleaning(self, mode: str, params=None) -> bool:
        print(f"[MOCK ROBOT] Starting cleaning mode: {mode}")
        self.cleaning = True
        return True

    def stop_cleaning(self) -> bool:
        print("[MOCK ROBOT] Stopping cleaning")
        self.cleaning = False
        return True

    def get_status(self):
        return {
            "connected": self.connected,
            "current_node": self.current_node,
            "cleaning": self.cleaning
        }
