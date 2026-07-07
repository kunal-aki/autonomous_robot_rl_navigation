# Autonomous Robot Navigation Utilizing Reinforcement Learning for Optimal Path Finding

[Watch This Video For A Demo Of My Project!](https://drive.google.com/file/d/1BKHXHWkry97uiGU3LDK30FOwW9zna_fL/view?usp=sharing)
## How It Works

The robot uses a two-phase workflow to achieve zero-error navigation:

1. The Learning Phase: The robot maps an unknown environment using its sensors and runs a lightweight Reinforcement Learning algorithm (like Q-learning) to discover the shortest path.
2. The Execution Phase: Once the best path is found, the robot saves the exact coordinates to a local file. On all future runs, it reads this file and drives the route deterministically, bypassing any further learning or exploration.

