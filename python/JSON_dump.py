import os
import re
import math
import numpy as np
import json
import shutil
from find_name import find_weapon_name

# def find_name(file_name):
#     try:
#         with open(units_path, 'r', encoding='utf-8', errors='ignore') as units:
#             data = units.read()
#             name_match = re.search(fr'{file_name}/short";"(.*?)"', data)
#             if name_match:
#                 name = name_match.group(1)
#             else:
#                 name = file_name
#             return name
#     except Exception as e:
#         print(f"Error reading units_weaponry.csv: {e}")
#         return file_name

def get_first_value(value):
    if isinstance(value, list):
        return value[0] if value else 0
    return value

def load_version(version_file_path):
    try:
        with open(version_file_path, 'r') as version_file:
            return version_file.read().strip()
    except Exception as e:
        print(f"Error reading version file {version_file_path}: {e}")
        return 'unknown_version'

def extract_info(file_path, version):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in file {file_path}: {e}")
        return None
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
    
    try:
        bullet_type_match = data.get('rocket', {}).get('bulletType')
        if not bullet_type_match or bullet_type_match != "aam":
            return None

        rocket = data.get('rocket', {})
        guidance = rocket.get('guidance', {}).get('guidanceAutopilot', {})
        
        bullet_name = rocket.get('bulletName')
        caliber = float(rocket.get('caliber', 0))
        cxk = float(rocket.get('CxK', 0))
        mass = float(rocket.get('mass', 0))
        mass_end_booster = float(rocket.get('massEnd', 0))
        mass_end_sustainer = float(rocket.get('massEnd1', 0))
        time_fire_booster = get_first_value(rocket.get('timeFire', 0))
        time_fire_sustainer = get_first_value(rocket.get('timeFire1', 0))
        force_booster = float(rocket.get('force', 0))
        force_sustainer = float(rocket.get('force1', 0))
        time_life = float(rocket.get('timeLife', 0))
        end_speed = float(rocket.get('endSpeed', 0))
        max_distance = float(rocket.get('maxDistance', 0))
        loft_elevation = float(guidance.get('loftElevation', 0))
        loft_target_elevation = float(guidance.get('loftTargetElevation', 0))
        loft_omega_max = float(guidance.get('loftTargetOmegaMax', 0))
        loft_acceleration = float(guidance.get('loftAngleToAccelMult', 0))
        lock_distance = float(rocket.get('guidance', {}).get('radarSeeker', {}).get('receiver', {}).get('range', 0))
        fin_aoa_hor = float(rocket.get('finsAoaHor', 0))
        fin_aoa_ver = float(rocket.get('finsAoaVer', 0))
        tvc = float(rocket.get('thrustVectoringAngle', 0))
        overload = float(guidance.get('reqAccelMax', 0))
        dist_cm_stab = float(rocket.get('distFromCmToStab', 0))
        wing_mult = float(rocket.get('wingAreaMult', 0))
        guidance_timeout = float(guidance.get('timeOut') if guidance.get('timeOut') else guidance.get('timeToGain1')[0] if guidance.get('timeToGain1') else 0)
        
        wing_area = math.ceil(wing_mult * caliber * 100) / 100
        aoa = math.ceil(max(fin_aoa_hor, fin_aoa_ver) * 900) / 10
        tvc_deg = tvc * 90

        mass_difference = mass - mass_end_booster
        mass_difference1 = mass_end_booster - mass_end_sustainer if mass_end_sustainer != 0 else 0

        G = 9.81

        booster_impulse = force_booster * time_fire_booster
        sustainer_impulse = force_sustainer * time_fire_sustainer

        booster_isp = booster_impulse / (G * mass_difference) if mass_difference != 0 else 0
        sustainer_isp = sustainer_impulse / (G * mass_difference1) if mass_difference1 != 0 else 0

        area = np.pi * (caliber / 2) ** 2
        relative_drag_coeff = cxk * area

        drag_weight_ratio = relative_drag_coeff / mass_end_sustainer if mass_end_sustainer != 0 else relative_drag_coeff / mass_end_booster

        deltav_booster = booster_isp * G * np.log(mass / mass_end_booster)
        deltav_sustainer = sustainer_isp * G * np.log(mass_end_booster / mass_end_sustainer) if force_sustainer else 0
        total_deltav = deltav_booster + deltav_sustainer if deltav_sustainer else deltav_booster

        return {
            "file_path": file_path,
            "bullet_name": bullet_name if bullet_name else None,
            "caliber": caliber,
            "cxk": cxk,
            "relative drag": round(relative_drag_coeff, 3),
            "Drag/weight": round(drag_weight_ratio * 1000, 3),
            "mass": mass,
            "mass_end_booster": mass_end_booster,
            "mass_end_sustainer": mass_end_sustainer if mass_end_sustainer !=0 else mass_end_booster,
            "time_fire_booster": time_fire_booster,
            "time_fire_sustainer": time_fire_sustainer,
            "Booster dV": round(deltav_booster),
            "Sustainer dV": round(deltav_sustainer) if deltav_sustainer else 0,
            "Total dV": round(total_deltav),
            "force_booster": round(force_booster, 2),
            "force_sustainer": round(force_sustainer, 2),
            "Booster Mass": round(mass_difference, 1),
            "Sustainer Mass": round(mass_difference1, 1),
            "Total Impulse": round(booster_impulse + sustainer_impulse),
            "booster ISP": round(booster_isp),
            "sustainer ISP": round(sustainer_isp),
            "time_life": time_life,
            "end_speed": end_speed,
            "max_distance": max_distance,
            "loft_elevation": loft_elevation,
            "loft_target_elevation": abs(loft_target_elevation),
            "loft_omega_max": loft_omega_max,
            "loft_angle_acceleration": loft_acceleration,
            "lock_distance": lock_distance,
            "aoa": aoa,
            "tvc": tvc_deg,
            "overload": overload,
            "dist_cm_stab": dist_cm_stab,
            "wing_area": wing_area,
            "guidance_timeout": guidance_timeout,
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None

def list_blk_files(directory, compiled_dir, version):
    print(f'Loading information from {directory}')
    if not os.path.isdir(directory):
        print(f"Error: Directory {directory} does not exist.")
        return {}

    compiled_file = os.path.join(compiled_dir, 'compiled_info.json')
    
    blk_files_info = {}
    for filename in os.listdir(directory):
        if filename.endswith(('.blkx', '.blk')):
            file_path = os.path.join(directory, filename)
            try:
                info = extract_info(file_path, version)
                file_name = filename.rsplit('.', 1)[0]
                name = find_weapon_name(file_name)
                if info:
                    blk_files_info[name] = info
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Save the extracted information to the compiled file along with the version
    try:
        os.makedirs(compiled_dir, exist_ok=True)
        output_data = {
            "version": version,
            "data": blk_files_info
        }
        with open(compiled_file, 'w') as file:
            json.dump(output_data, file, indent=4)
            print(f"Saved compiled information to {compiled_file}")

        # Copy the compiled file to the 'saves compiled info' directory with version in the filename
        save_dir = 'saves_compiled_info'
        os.makedirs(save_dir, exist_ok=True)
        versioned_file_name = f'compiled_info_{version}.json'
        shutil.copy(compiled_file, os.path.join(save_dir, versioned_file_name))
        print(f"Copied compiled file to {os.path.join(save_dir, versioned_file_name)}")
        
    except Exception as e:
        print(f"Error saving compiled info to {compiled_file}: {e}")

    return blk_files_info

# Example usage
directory = 'rocketguns_json/aces.vromfs.bin_u/gamedata/weapons/rocketguns'
units_path = 'rocketguns_json/lang/lang.vromfs.bin_u/lang/units_weaponry.csv'
compiled_dir = 'compiled_info_directory'
version_file_path = 'rocketguns_json/aces.vromfs.bin_u/version'
version = load_version(version_file_path)
blk_files_info = list_blk_files(directory, compiled_dir, version)

#print(blk_files_info)
