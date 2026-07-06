class Robot:

    def __init__(self, start):

        self.x, self.y = start

        # tracking for future Phase 3 memory system
        self.history = []
        self.total_steps = 0

    # -----------------------------
    # MOVE ROBOT
    # -----------------------------
    def set_position(self, pos):

        self.x, self.y = pos

        self.history.append(pos)
        self.total_steps += 1

    # -----------------------------
    # GET CURRENT POSITION
    # -----------------------------
    def get_position(self):

        return (self.x, self.y)

    # -----------------------------
    # RESET ROBOT
    # -----------------------------
    def reset(self, start):

        self.x, self.y = start
        self.history = []
        self.total_steps = 0
