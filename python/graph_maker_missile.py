import argparse
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider, Button
import tkinter
import math
from scipy.interpolate import interp1d

# Conversion table
conversion_table = {
    0: [1224, 1224, 1],
    1000: [1224, 1167, 1.01],
    2000: [1224, 1110, 1.02],
    3000: [1224, 1060, 1.04],
    4000: [1224, 1000, 1.05],
    5000: [1224, 950, 1.06],
    6000: [1224, 900, 1.07],
    7000: [1224, 850, 1.09],
    8000: [1224, 800, 1.1],
    9000: [1224, 750, 1.12],
    10000: [1224, 700, 1.13],
    11000: [1224, 670, 1.14],
    12000: [1224, 625, 1.16],
    13000: [1224, 580, 1.17],
    14000: [1224, 544, 1.17],
    15000: [1224, 500, 1.18],
    16000: [1224, 465, 1.18],
    17000: [1224, 425, 1.17],
    18000: [1224, 390, 1.15],
    19000: [1224, 370, 1.15],
    20000: [1224, 360, 1.15],
}

altitudes = list(conversion_table.keys())
tas_values = [conversion_table[alt][0] for alt in altitudes]
ias_values = [conversion_table[alt][1] for alt in altitudes]
mach_values = [conversion_table[alt][2] for alt in altitudes]
speed_of_sound_values = [1224 / mach for mach in mach_values]

# Interpolation functions
tas_to_ias_interp = interp1d(altitudes, ias_values)
ias_to_tas_interp = interp1d(altitudes, tas_values)
speed_of_sound_interp = interp1d(altitudes, speed_of_sound_values)

def tas_to_ias(tas, altitude):
    if altitude < altitudes[0] or altitude > altitudes[-1]:
        raise ValueError("Altitude out of bounds for interpolation")
    ias_at_altitude = tas_to_ias_interp(altitude)
    return tas * (ias_at_altitude / 1224)

def ias_to_tas(ias, altitude):
    if altitude < altitudes[0] or altitude > altitudes[-1]:
        raise ValueError("Altitude out of bounds for interpolation")
    tas_at_altitude = tas_to_ias_interp(altitude)
    return ias * (1224 / tas_at_altitude)

def get_mach_number(tas, altitude):
    if altitude < altitudes[0] or altitude > altitudes[-1]:
        raise ValueError("Altitude out of bounds for interpolation")
    speed_of_sound = speed_of_sound_interp(altitude)
    return tas / speed_of_sound


# Function to parse command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description="Run missile simulation with provided parameters")
    parser.add_argument("--bullet_name", type=str, required=True)
    parser.add_argument("--caliber", type=float, required=True)
    parser.add_argument("--cxk", type=float, required=True)
    parser.add_argument("--mass", type=float, required=True)
    parser.add_argument("--mass_end_booster", type=float, required=True)
    parser.add_argument("--mass_end_sustainer", type=float, required=False, default=0)
    parser.add_argument("--time_fire_booster", type=float, required=True)
    parser.add_argument("--time_fire_sustainer", type=float, required=False, default=0)
    parser.add_argument("--force_booster", type=float, required=True)
    parser.add_argument("--force_sustainer", type=float, required=False, default=0)
    parser.add_argument("--time_life", type=float, required=True)
    parser.add_argument("--end_speed", type=float, required=True)
    parser.add_argument("--max_distance", type=float, required=False, default=None)
    parser.add_argument("--pressure0", type=float, required=False, default=760)  # Default pressure in hPa
    parser.add_argument("--temperature0", type=float, required=False, default=18)  # Default temperature in °C
    parser.add_argument("--loft_elevation", type=float, required=False, default=None)
    parser.add_argument("--loft_target_elevation", type=float, required=False, default=None)
    parser.add_argument("--loft_omega_max", type=float, required=False, default=None)
    parser.add_argument("--loft_acceleration", type=float, required=False, default=None)
    parser.add_argument("--lock_distance", type=float, required=False, default=None)
    parser.add_argument("--aoa", type=float, required=False, default=None)
    parser.add_argument("--tvc", type=float, required=False, default=0)
    parser.add_argument("--overload", type=float, required=False, default=None)
    parser.add_argument("--dist_cm_stab", type=float, required=False, default=None)
    parser.add_argument("--wing_area", type=float, required=False, default=None)
    parser.add_argument("--timeout", type=float, required=False, default=None)

    return vars(parser.parse_args())


def get_rho(altitude):
    # Given data
    altitudes = np.array([0, 1000, 2000, 3000, 5000, 8000, 10000, 12000, 15000, 20000])
    rho_values = np.array([0.56, 0.53, 0.49, 0.44, 0.365, 0.3, 0.27, 0.23, 0.19, 0.15])
    
    # Create an interpolation function with extrapolation enabled
    interp_func = interp1d(altitudes, rho_values, kind='linear', fill_value="extrapolate")
    
    # Calculate the rho value for the given altitude
    rho = interp_func(altitude)
    
    return rho

def compute_dependent_variables(args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude):
    start_speed_ias = tas_to_ias(start_speed, launch_altitude)

    # Constants
    g = 9.81  # gravitational acceleration (m/s^2)
    time_interval=0.01
    # Time array
    times = np.arange(0, args["time_life"] + time_interval, time_interval)
    n = len(times)

    # Initialize arrays
    true_mass = np.zeros(n)
    true_thrust = np.zeros(n)
    speeds = np.zeros(n)
    horizontal_speeds = np.zeros(n)
    vertical_speeds = np.zeros(n)
    drags = np.zeros(n)
    accelerations = np.zeros(n)
    horizontal_distances = np.zeros(n)
    vertical_distances = np.zeros(n)
    target_distances = np.zeros(n)
    true_acceleration = np.zeros(n)
    thrust_to_weights = np.zeros(n)
    angle = np.zeros(n)
    turn_rates = np.zeros(n)
    g_load = np.zeros(n)
    turn_radius = np.zeros(n)
    tas_speed = np.zeros(n)

    # Set initial values
    speeds[0] = start_speed_ias * (1000 / 3600)  # Convert km/h to m/s
    horizontal_speeds[0] = start_speed / 3.6
    vertical_speeds[0] = 0  # Initial vertical speed
    target_distances[0] = initial_target_distance * 1000  # Convert km to m
    horizontal_distances[0] = 0  # Initial horizontal distance
    vertical_distances[0] = launch_altitude  # Initial altitude
    angle[0] = 0
    tas_speed[0] = start_speed / 3.6
    aoa = np.radians(args.get("aoa"))
    tvc = np.radians(args.get("tvc"))
    max_load = args.get("overload")
    D = args.get("dist_cm_stab")

    # Get loft angles if there are any
    loft_climb_angle = args.get("loft_elevation")
    loft_dive_angle = args.get("loft_target_elevation")
    loft_omegamax = args.get("loft_omega_max")
    distance_check = args.get("lock_distance")
    loft_accel = args.get("loft_acceleration") 

    # Convert angles to radians if they are not zero and set the climbing mode
    if loft_climb_angle and loft_dive_angle and loft_omegamax != 0:
        loft_climb_angle = np.radians(loft_climb_angle)
        loft_dive_angle = np.radians(loft_dive_angle)
        loft_omega_max = np.radians(loft_omegamax*9) * time_interval
        lofting = True
        climbing = True
        diving = False
    else:
        lofting = False
        climbing = False
        diving = False

    # Segment 1: First phase burn
    timefire_steps = int(np.ceil((args["time_fire_booster"] + time_interval) / time_interval)) if args["time_fire_booster"] != 0 else 0
    mass_decrease_rate1 = (args["mass"] - args["mass_end_booster"]) / (timefire_steps - 1)
    for i in range(min(timefire_steps, n)):
        true_mass[i] = args["mass"] - i * mass_decrease_rate1
        true_thrust[i] = args["force_booster"]

    # Segment 2: Second phase burn (if applicable)
    if args["time_fire_sustainer"] > 0 and args["force_sustainer"] > 0 and args["mass_end_sustainer"] > 0:
        timefire1_steps = int(np.ceil((args["time_fire_sustainer"] + time_interval) / time_interval))
        mass_decrease_rate2 = (args["mass_end_booster"] - args["mass_end_sustainer"]) / (timefire1_steps - 1)
        for i in range(timefire_steps, min(timefire_steps + timefire1_steps, n)):
            true_mass[i] = args["mass_end_booster"] - (i - timefire_steps) * mass_decrease_rate2
            true_thrust[i] = args["force_sustainer"]
    else:
        timefire1_steps = 0

    # Segment 3: Coasting phase
    for i in range(timefire_steps + timefire1_steps, n):
        true_mass[i] = args["mass_end_booster"] if args["mass_end_sustainer"] == 0 else args["mass_end_sustainer"]
        true_thrust[i] = 0

    # Compute dynamics
    for i in range(1, n):
        rho = get_rho(vertical_distances[i-1])
        area = np.pi * (args["caliber"] / 2) ** 2  # Cross section area

        thrust_ias = tas_to_ias(true_thrust[i], vertical_distances[i-1])
        drags[i] = 0.5 * rho * speeds[i-1] ** 2 * args["cxk"] * area  # Drag computation
        accelerations[i] = (thrust_ias - drags[i]) / true_mass[i]  # Thrust acceleration

        intersection_time = (target_distances[i-1] - horizontal_distances[i-1]) / (horizontal_speeds[i-1] - target_speed * (1000 / 3600)) if target_speed != 0 else 0  # Predicted interception distance
        desired_altitude_change = target_altitude - vertical_distances[i-1]  # Climbing or diving distance
        angle1 = np.arctan(desired_altitude_change / (intersection_time * speeds[i-1])) if target_speed != 0 else 0
        dive_check = np.arctan(desired_altitude_change/(target_distances[i-1] - horizontal_distances [i-1])) if target_speed != 0 else 0
        desired_loft_angle = min(abs(true_acceleration[i-1]) * loft_accel * 0.005, loft_climb_angle)
        
        if distance_check > 0:
            if target_distances[i-1] - horizontal_distances[i-1] < distance_check/2:
                if lofting:
                    climbing = False
                    diving = True

        # Altitude functions
        if target_distances[i-1] - horizontal_distances[i-1] <= 0:
            angle[i] = 0
        elif target_altitude > vertical_distances[i-1]:
            angle[i]= angle1
        elif lofting:
            if climbing:
                angle[i] = min(desired_loft_angle, angle[i-1] + loft_omega_max) if desired_loft_angle > angle[i-1] + loft_omega_max else max(desired_loft_angle, angle[i-1] - loft_omega_max)

                if abs(dive_check) >= loft_dive_angle:
                    diving = True
                    climbing = False
            elif diving:
                if angle1 > 0:
                    angle[i] = min(angle[i-1]-loft_omega_max, angle1)
                elif angle1 < 0:
                    angle[i] = max(angle[i-1]-loft_omega_max, angle1)
                else:
                    angle[i] = angle1
        else:
            if desired_altitude_change == 0:
                angle[i] = 0
            else:
                angle[i] = angle1

        # Compute acceleration components based on the angle
        thrust_acceleration_x = accelerations[i] * np.cos(angle[i])
        thrust_acceleration_y = accelerations[i] * np.sin(angle[i])
        gravity_acceleration_y = -g * np.sin(angle[i])

        thrust_to_weights[i] = true_thrust[i] / true_mass[i]
        # True acceleration in the rocket's direction
        true_acceleration[i] = np.sign(accelerations[i]) * np.sqrt(thrust_acceleration_x ** 2 + thrust_acceleration_y ** 2) + gravity_acceleration_y

        # Update speeds and distances
        speeds[i] = speeds[i-1] + true_acceleration[i] * time_interval
        tas_speed[i] = ias_to_tas(speeds[i], vertical_distances[i-1])
        if args["end_speed"] != 0:
            tas_speed[i] = min(tas_speed[i], args["end_speed"])  # Cap the speed at max speed if provided
            speeds[i] = tas_to_ias(tas_speed[i], vertical_distances[i-1])
        # Separate x and y components from the true speed
        horizontal_speeds[i] = tas_speed[i] * np.cos(angle[i])
        vertical_speeds[i] = tas_speed[i] * np.sin(angle[i])


        horizontal_distances[i] = horizontal_distances[i-1] + horizontal_speeds[i] * time_interval  # Update horizontal distance
        vertical_distances[i] = vertical_distances[i-1] + vertical_speeds[i] * time_interval  # Update altitude
        target_distances[i] = target_distances[i-1] + target_speed * (1000 / 3600) * time_interval  # Update target distance

        if 0 < aoa < np.pi/8 or 7*np.pi/8 < aoa < np.pi:
            Cl = np.sin(6*aoa)
        elif np.pi/8 <= aoa <= 7*np.pi/8:
            Cl = np.sin(2*aoa)
        else:
            Cl = 0
        
        turn_rate = ((Cl * args["wing_area"] * 0.5 * rho * (speeds[i]**2) * D)/true_mass[i] + (tvc*D*true_thrust[i])/(true_mass[i])) * time_interval
        radius_check = tas_speed[i]/turn_rate
        load_check = (tas_speed[i]**2)/(radius_check*g)

        if args["timeout"] <= times[i]:
            if max_load == 0:
                turn_rates[i] = turn_rate
                turn_radius[i] = radius_check
                g_load[i] = load_check               
            elif load_check < max_load:
                turn_rates[i] = turn_rate
                turn_radius[i] = radius_check
                g_load[i] = load_check
            else:
                g_load[i] = max_load
                turn_radius[i] = (tas_speed[i] ** 2)/(max_load*g)
                turn_rates[i] = tas_speed[i]/turn_radius[i]
        else:
            turn_rates[i] = 0
            turn_radius[i] = 0
            g_load[i] = 0

        # Stop if max distance is reached and provided
        if args["max_distance"] is not None and horizontal_distances[i] > args["max_distance"]:
            trunc_index = i + 1
            times = times[:trunc_index]
            true_mass = true_mass[:trunc_index]
            true_thrust = true_thrust[:trunc_index]
            speeds = speeds[:trunc_index]
            horizontal_speeds = horizontal_speeds[:trunc_index]
            vertical_speeds = vertical_speeds[:trunc_index]
            drags = drags[:trunc_index]
            accelerations = accelerations[:trunc_index]
            horizontal_distances = horizontal_distances[:trunc_index]
            vertical_distances = vertical_distances[:trunc_index]
            target_distances = target_distances[:trunc_index]
            true_acceleration = true_acceleration[:trunc_index]
            thrust_to_weights = thrust_to_weights[:trunc_index]
            angle = angle[:trunc_index]
            g_load = g_load[:trunc_index]
            turn_rates = turn_rates[:trunc_index]  
            turn_radius = turn_radius[:trunc_index]
            tas_speed = tas_speed[:trunc_index]        
            break

    mach_numbers = [get_mach_number(tas * 3.6, vertical_distances[i]) for i, tas in enumerate(tas_speed)]
    accelerations_tas = [ias_to_tas(acceleration, vertical_distances[i]) for i, acceleration in enumerate(accelerations)]


    return times, true_mass, true_thrust, tas_speed, mach_numbers, drags, accelerations_tas, horizontal_distances, vertical_distances, target_distances, thrust_to_weights, g_load, turn_radius, turn_rates

def generate_missile_graph(args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude):
    times, true_mass, true_thrust, speeds_tas, mach_numbers, drags, accelerations, horizontal_distances, vertical_distances, target_distances, thrust_to_weights, g_load, turn_radius, turn_rates = compute_dependent_variables(
        args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude
    )

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor="dimgrey")
    # Plot 1: Time vs Speed
    ax_speed = axs[0, 0]
    ax_mach = ax_speed.twinx()
    line_mach, = ax_mach.plot(times, mach_numbers, label='Mach', color='b')
    line_speed, = ax_speed.plot(times, speeds_tas, label='Speed', color='c')
    ax_speed.set_title(f'{args["name"]}')
    ax_mach.set_ylabel('Mach number')
    ax_mach.grid(False)
    ax_mach.patch.set_facecolor("grey")
    ax_speed.set_xlabel('Time (s)')
    ax_speed.set_ylabel('Speed TAS (m/s)')
    ax_speed.grid(True, color="black")
    ax_speed.patch.set_facecolor("grey")
    ax_mach.legend(loc='lower right')
    ax_speed.legend(loc='upper right')

    # Plot 2: Time vs Distance
    ax_distance = axs[0, 1]
    line_horizontal_distance, = ax_distance.plot(times, horizontal_distances, label='Horizontal Distance', color='b')
    ax_distance.set_xlabel('Time (s)')
    ax_distance.set_ylabel('Distance (m)')
    ax_distance.grid(True, color='black')
    ax_distance.patch.set_facecolor("grey")

    # Plot 3: Time vs Acceleration
    ax_acceleration = axs[1, 0]
    line_acceleration, = ax_acceleration.plot(times, accelerations, label='Acceleration', color='b')
    ax_acceleration.set_xlabel('Time (s)')
    ax_acceleration.set_ylabel('Acceleration (m/s²)')
    ax_acceleration.grid(True, color="black")
    ax_acceleration.patch.set_facecolor("grey")

    # Plot 4: Time vs Drag
    ax_drag = axs[1, 1]
    line_drag, = ax_drag.plot(times, drags, label='Drag', color='b')
    ax_drag.set_xlabel('Time (s)')
    ax_drag.set_ylabel('Drag (N)')
    ax_drag.grid(True, color="black")
    ax_drag.patch.set_facecolor("grey")

    plt.tight_layout(rect=[0, 0, 1, 1])

    fig1, axs1 = plt.subplots(1, 2, figsize=(20, 10), facecolor="dimgrey")


    # Plot 1-1: Hor and Vert distances
    ax_distance1 = axs1[0]
    line_vertical_distance = ax_distance1.plot(times, vertical_distances, label='Altitude', color='g')
    line_target_distance = ax_distance1.plot(times, target_distances, label='Target Distance', color='r')
    line_horizontal_distance, = ax_distance1.plot(times, horizontal_distances, label='Horizontal Distance', color='b')
    ax_distance1.set_title(f"{initial_target_distance}km, {launch_altitude}m, {start_speed}km/h, \ntarget going {target_speed}km/h at {launch_altitude}m")
    ax_distance1.set_xlabel('Time (s)')
    ax_distance1.set_ylabel('Distance (m)')
    ax_distance1.legend(loc='upper left')
    ax_distance1.grid(True, color='black')
    ax_distance1.patch.set_facecolor("grey")

    # Plot 1-2: T/W

    ax_twr = axs1[1]
    line_thrust_weight = ax_twr.plot(times, thrust_to_weights, label='T/W', color='g')
    ax_twr.set_xlabel('Time (s)')
    ax_twr.set_ylabel('T/W')
    ax_twr.grid(True, color="black")
    ax_twr.patch.set_facecolor("grey")

    fig2, axs2 = plt.subplots(1, 2, figsize=(10,20), facecolor="dimgrey")

    ax_g = axs2[0]
    line_g = ax_g.plot(times, g_load, label='G load', color='b')
    ax_g.set_xlabel('Time (s)')
    ax_g.set_ylabel('G load')
    ax_g.grid(True, color="black")
    ax_g.patch.set_facecolor("grey")

    ax_turn = axs2[1]
    line_turn_radius = ax_turn.plot(times, turn_radius, label='Turn radius', color='b')
    ax_turn.set_xlabel('Time (s)')
    ax_turn.set_ylabel('Turn radius (m)')
    ax_turn.grid(True, color="black")
    ax_turn.patch.set_facecolor("grey")

    return fig, fig1, fig2


def generate_comparison_graph(args1, args2,start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude):
    args = args1
    times, true_mass, true_thrust, speeds_tas, mach_numbers, drags, accelerations, horizontal_distances, vertical_distances, target_distances, thrust_to_weights, g_load, turn_radius, turn_rates = compute_dependent_variables(
        args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude
    )
    args = args2
    times2, true_mass2, true_thrust2, speeds_tas2, mach_numbers2, drags2, accelerations2, horizontal_distances2, vertical_distances2, target_distances2, thrust_to_weights2, g_load2, turn_radius2, turn_rates2 = compute_dependent_variables(
        args, start_speed, launch_altitude, target_speed, initial_target_distance, target_altitude
    )

    fig, axs = plt.subplots(2, 2, figsize=(16, 10), facecolor="dimgrey")
    # Plot 1: Time vs Speed
    ax_speed = axs[0, 0]
    ax_mach = ax_speed.twinx()
    line_mach, = ax_mach.plot(times, mach_numbers,label=f'Mach {args1["name"]}', color='b')
    line_mach1, = ax_mach.plot(times2, mach_numbers2, label=f'Mach {args2["name"]}', color='c')
    line_speed, = ax_speed.plot(times, speeds_tas, label=f'Speed {args1["name"]}', color='r')
    line_speed1, = ax_speed.plot(times2, speeds_tas2, label=f'Speed {args2["name"]}', color='g')
    ax_speed.set_title(f'{args1["name"]}, {args2["name"]}')
    ax_mach.set_ylabel('Mach number')
    ax_mach.grid(False)
    ax_mach.patch.set_facecolor("grey")   
    ax_speed.set_xlabel('Time (s)')
    ax_speed.set_ylabel('Speed TAS (m/s)')
    ax_speed.grid(True, color="black")
    ax_speed.patch.set_facecolor("grey")
    ax_mach.legend(loc='lower right')
    ax_speed.legend(loc='upper right')

    # Plot 2: Time vs Distance
    ax_distance = axs[0, 1]
    line_horizontal_distance, = ax_distance.plot(times, horizontal_distances, label=f'Hor Dist {args1["name"]}', color='b')
    line_horizontal_distance1, = ax_distance.plot(times2, horizontal_distances2, label=f'Hor Dist {args2["name"]}', color='c')
    ax_distance.set_xlabel('Time (s)')
    ax_distance.set_ylabel('Distance (m)')
    ax_distance.grid(True, color='black')
    ax_distance.patch.set_facecolor("grey")

    # Plot 3: Time vs Acceleration
    ax_acceleration = axs[1, 0]
    line_acceleration, = ax_acceleration.plot(times, accelerations, label=f'Acceleration {args1["name"]}', color='b')
    line_acceleration1, = ax_acceleration.plot(times2, accelerations2, label=f'Acceleration {args2["name"]}', color='c')
    ax_acceleration.set_xlabel('Time (s)')
    ax_acceleration.set_ylabel('Acceleration (m/s²)')
    ax_acceleration.grid(True, color="black")
    ax_acceleration.patch.set_facecolor("grey")

    # Plot 4: Time vs Drag
    ax_drag = axs[1, 1]
    line_drag, = ax_drag.plot(times, drags, label=f'Drag {args1["name"]}', color='b')
    line_drag1, = ax_drag.plot(times2, drags2, label=f'Drag {args2["name"]}', color='c')
    ax_drag.set_xlabel('Time (s)')
    ax_drag.set_ylabel('Drag (N)')
    ax_drag.grid(True, color="black")
    ax_drag.patch.set_facecolor("grey")

    plt.tight_layout(rect=[0, 0, 1, 1])

    fig1, axs1 = plt.subplots(1, 2, figsize=(20, 10), facecolor="dimgrey")

    # Plot 1-1: Hor and Vert distances
    ax_distance1 = axs1[0]
    ax_distance1.set_title(f"{initial_target_distance}km, {launch_altitude}m, {start_speed}km/h, \ntarget going {target_speed}km/h at {launch_altitude}m")
    line_horizontal_distance, = ax_distance1.plot(times, horizontal_distances, label=f'Hor Dist {args1["name"]}', color='b')
    line_horizontal_distance1, = ax_distance1.plot(times2, horizontal_distances2, label=f'Hor Dist {args2["name"]}', color='c')
    line_vertical_distance, = ax_distance1.plot(times, vertical_distances, label=f'Alt {args1["name"]}', color='g')
    line_vertical_distance1, = ax_distance1.plot(times2, vertical_distances2, label=f'Alt {args2["name"]}', color='y')
    line_target_distance, = ax_distance1.plot(times, target_distances, label='Target Dist', color='r')
    line_target_distance, = ax_distance1.plot(times2, target_distances2, color='r')

    ax_distance1.set_xlabel('Time (s)')
    ax_distance1.set_ylabel('Distance (m)')
    ax_distance1.legend(loc='upper left')
    ax_distance1.grid(True, color='black')
    ax_distance1.patch.set_facecolor("grey")

    # Plot 1-2: TWR
    ax_twr = axs1[1]
    line_thrust_weight1 = ax_twr.plot(times, thrust_to_weights, label=f'T/W {args1["name"]}', color='g')
    line_thrust_weight2 = ax_twr.plot(times2, thrust_to_weights2, label=f'T/W {args2["name"]}', color='y')
    ax_twr.set_xlabel('Time (s)')
    ax_twr.set_ylabel('TWR')
    ax_twr.grid(True, color="black")
    ax_twr.patch.set_facecolor("grey")
    ax_twr.legend(loc='upper right')

    fig2, axs2 = plt.subplots(1, 2, figsize=(10,20), facecolor="dimgrey")

    ax_g = axs2[0]
    line_g = ax_g.plot(times, g_load, label=f'G load {args1['name']}', color='b')
    line_g1 = ax_g.plot(times2, g_load2, label=f'G load {args2['name']}', color='c')
    ax_g.set_xlabel('Time (s)')
    ax_g.set_ylabel('G load')
    ax_g.grid(True, color="black")
    ax_g.patch.set_facecolor("grey")
    ax_g.legend(loc='upper right')

    ax_turn = axs2[1]
    line_turn_radius = ax_turn.plot(times, turn_radius, label=f'Turn radius {args1['name']}', color='b')
    line_turn_radius1 = ax_turn.plot(times2, turn_radius2, label=f'Turn radius {args2['name']}', color='c')
    ax_turn.set_xlabel('Time (s)')
    ax_turn.set_ylabel('Turn radius (m)')
    ax_turn.grid(True, color="black")
    ax_turn.patch.set_facecolor("grey")
    ax_turn.legend(loc='upper right')



    return fig, fig1, fig2
