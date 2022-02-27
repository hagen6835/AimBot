# https://discourse.odriverobotics.com/t/nema-enclosures-for-d5065-and-d6374-motors/830
# https://docs.odriverobotics.com/v/latest/getting-started.html
# https://docs.odriverobotics.com/v/latest/fibre_types/com_odriverobotics_ODrive.html


import numpy as np
import odrive
import time

od = odrive.find_any()
axis = od.axis0
mo = axis.motor
enc = axis.encoder

# od.reboot()
# time.sleep(4)
axis.requested_state = 3  # 3 is the calibration sequence

# wait until calibration sequence is over
while axis.current_state != 1:
    time.sleep(.1)

axis.requested_state = 8  # 8 is the closed control loop

if __name__ == '__main__':
    while True:
        if axis.current_state != 8:
            print("NOT IN CLOSE LOOP MODE")
        print("current position: ", axis.controller.input_pos)
        command = input("input position: ").strip()
        input_value = int(command)

        axis.controller.input_pos = input_value


def set_motor_position(rear_coordinates):
    # takes in the rear coordinates and figures out what the motor position should be to match that coordinate
    # will take some tuning to figure out how many turns match to what position on the screw assembly
    return


# Takes in 3d target location and calculates where the rear of the gun should be located to aim at that point
def get_rear_coordinates(found_coordinates):
    x, y, z = found_coordinates

    x_0 = 0
    y_0 = 0
    z_0 = 0

    # equation of the plane that controls the rear of the gun
    rear_z = -1

    x_y_equality = (rear_z - z_0) / (z - z_0)

    rear_y = ((y - y_0) * x_y_equality) + y_0
    rear_x = ((x - x_0) * x_y_equality) + x_0

    return np.array([rear_x, rear_y, rear_z])


# returns true if it is within the bounds of the machine itself
def check_rear_coordinates(rear_coordinates):
    x, y, z = rear_coordinates

    # pre-defined range of motion for the rear mover [lower, upper]
    X_BOUNDS = np.array([-.5, .5])
    Y_BOUNDS = np.array([-.5, .5])
    Z_BOUNDS = np.array([-1, -1])

    in_bounds = True

    if x < X_BOUNDS[0] or x > X_BOUNDS[1]:
        in_bounds = False

    if y < Y_BOUNDS[0] or y > Y_BOUNDS[1]:
        in_bounds = False

    if z < Z_BOUNDS[0] or z > Z_BOUNDS[1]:
        in_bounds = False

    return in_bounds
