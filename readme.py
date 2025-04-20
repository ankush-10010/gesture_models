""" RULES AND FEATURES OF THE GAME
These are solid gameplay features that add depth to your "Space Invader" game! Here's a quick summary of how these features shape the overall gameplay experience:
1.Switching Between Fire Modes:
The player can toggle between single fire and rapid fire modes for more strategic shooting.
Single Fire Mode: Press "S" to switch to single fire mode.
Rapid Fire Mode: Press "R" to switch to rapid fire mode.
2.Single Fire Mode:
Press "Space" to shoot lasers in single fire mode.
There's a cooldown of 400 milliseconds between consecutive laser shots, preventing spam but encouraging careful timing.
3.Rapid Fire Mode:
In rapid fire mode, players can shoot a laser every time they press "Space".
5 seconds of continuous firing is allowed, after which a 5-second cooldown kicks in before the player can shoot again.
4.Countdown Logic for Rapid Fire:
The 5-second countdown in rapid fire mode begins on the first laser shot, so players need to make those 5 seconds count. If they don't fire continuously during that time, the window for rapid fire will close, and they'll have to wait for the cooldown before firing again.
5.Game Over Condition:
If a meteor hits the player, the game ends instantly, making avoidance crucial to survival.
6.Laser Movement:
Press "a" for left movement of laser
Press "d" for right movement of laser
there is no movement in vertical direction for laser because it doesn't make sense
"""