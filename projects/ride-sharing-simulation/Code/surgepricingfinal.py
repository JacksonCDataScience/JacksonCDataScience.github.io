import math
import numpy as np
import numpy.random as npr
import scipy
from scipy import stats as scs



def trip_stats(loc1, loc2, coef, Time=False):
    """
    Determines distance and estimated time between two locations
    """
    dist = math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)
    if Time:
        time = npr.uniform(coef["trip_time_lb"], coef["trip_time_ub"]) * dist / 20
        return dist, time
    else:
        return dist

def new_trip_update(drivers, driver_id, riders, rider_id, TNOW, surge, coef):
    """
    Update driver and rider dictionaries after a match
    """
    riders[rider_id]["matched"] = 1
    drivers[driver_id]["matched"] = 1
    drivers[driver_id]["current_rider"] = rider_id

    if drivers[driver_id]["rest_start"] is not None:
        drivers[driver_id]["total_rest_time"] += TNOW - drivers[driver_id]["rest_start"]
        drivers[driver_id]["rest_start"] = None

    pickup_dist, pickup_time = trip_stats(drivers[driver_id]["destination"], riders[rider_id]["waiting_location"], coef, Time=True)
    dest_dist, dest_time = trip_stats(riders[rider_id]["waiting_location"], riders[rider_id]["destination"], coef, Time=True)
    dropoff_time = TNOW + pickup_time + dest_time

    drivers[driver_id]["destination"] = riders[rider_id]["destination"]
    drivers[driver_id]["dropoff_time"] = dropoff_time

    if surge:
        drivers[driver_id]["total_earnings"] += coef["surge_base"] + coef["surge_rate"] * dest_dist - 0.2 * pickup_dist
    else:
        drivers[driver_id]["total_earnings"] += 3 + 1.8 * dest_dist - 0.2 * pickup_dist

    riders[rider_id]["pickup_time"] = TNOW + pickup_time
    riders[rider_id]["arrival_time"] = dropoff_time
    riders[rider_id]["abandon_time"] = None

    return drivers, riders

def driver_awaiting_rider(drivers, driver_id, riders, TNOW, coef):
    """
    Attempts to match an available driver to the closest waiting rider
    they can actually reach before the rider abandons.
    """
    driver_loc = drivers[driver_id]["destination"]
    min_distance = float("inf")
    closest_rider = None

    unmatched_riders = [r_id for r_id, r in riders.items() if r["matched"] == 0]

    for rider_id in unmatched_riders:
        rider_loc = riders[rider_id]["waiting_location"]
        _, pickup_time = trip_stats(driver_loc, rider_loc, coef, Time=True)

        # Skip rider if driver cannot reach them before they abandon
        if riders[rider_id]["abandon_time"] is not None:
            if TNOW + pickup_time > riders[rider_id]["abandon_time"]:
                continue

        if pickup_time < min_distance:
            min_distance = pickup_time
            closest_rider = rider_id

    if closest_rider is not None:
        drivers, riders = new_trip_update(drivers, driver_id, riders, closest_rider, TNOW, surge=False, coef=coef)
    else:
        drivers[driver_id]["dropoff_time"] = None
        drivers[driver_id]["rest_start"] = TNOW

    return drivers, riders

def rider_awaiting_driver(drivers, rider_id, riders, TNOW, coef):
    """
    Attempts to match a waiting rider to the closest available (unmatched) driver.
    Surge is determined by whether any unmatched drivers are within proximity threshold.
    Abandon time is only set if no unmatched driver is available, matching original logic.
    """
    rider_loc = riders[rider_id]["waiting_location"]

    # Only consider unmatched drivers, exactly like the original
    unmatched_drivers = [(d_id, d) for d_id, d in drivers.items() if d["matched"] == 0]

    # Determine surge: no unmatched drivers within proximity threshold
    availableDrivers_forSurge = 0
    for d_id, driver in unmatched_drivers:
        driver_loc = driver["destination"]
        _, distance_time = trip_stats(driver_loc, rider_loc, coef, Time=True)
        if distance_time <= coef.get("surge_proximity_threshold", 0.5):
            availableDrivers_forSurge += 1

    surge = availableDrivers_forSurge == 0

    if len(unmatched_drivers) > 0:
        # Find closest unmatched driver
        min_distance = float("inf")
        closest_driver = None
        for d_id, driver in unmatched_drivers:
            driver_loc = driver["destination"]
            _, distance_time = trip_stats(driver_loc, rider_loc, coef, Time=True)
            if distance_time < min_distance:
                min_distance = distance_time
                closest_driver = d_id

        drivers, riders = new_trip_update(drivers, closest_driver, riders, rider_id, TNOW, surge=surge, coef=coef)

    else:
        # No unmatched drivers — set abandon time, exactly like original
        riders[rider_id]["abandon_time"] = TNOW + npr.exponential(1 / coef["abandon"])

    return drivers, riders, surge


def driver_enter_sys(drivers, next_driver_id, riders, TNOW, coef):
    """
    Adds a new driver to the system at TNOW
    """
    def fast_truncnorm(mean, std):
        while True:
            x = np.random.normal(mean, std)
            if 0 <= x <= 20:
                return x

    mean_x_driver = coef['rider_dest_x_mean']
    mean_y_driver = coef['rider_dest_y_mean']
    std_driver = coef['init_std']
    driver_loc = [fast_truncnorm(mean_x_driver, std_driver), fast_truncnorm(mean_y_driver, std_driver)]
    
    offline_time = TNOW + npr.uniform(coef["shift_time_lb"], coef["shift_time_ub"])

    drivers[next_driver_id] = {
        "matched": 0,
        "current_rider": None,
        "destination": driver_loc,
        "dropoff_time": None,
        "shift_start": TNOW,
        "shift_end": offline_time,
        "rest_start": None,
        "total_rest_time": 0.0,
        "total_earnings": 0.0
    }

    drivers, riders = driver_awaiting_rider(drivers, next_driver_id, riders, TNOW, coef)
    return drivers, riders

def rider_enter_sys(drivers, riders, next_rider_id, TNOW, coef):
    """
    Adds a new rider to the system at TNOW
    """
    def fast_truncnorm(mean, std):
        while True:
            x = np.random.normal(mean, std)
            if 0 <= x <= 20:
                return x

    mean_x_wait = coef['rider_init_x_mean']
    mean_y_wait = coef['rider_init_y_mean']
    std_wait = coef['init_std']
    rider_wait_loc = [fast_truncnorm(mean_x_wait, std_wait), fast_truncnorm(mean_y_wait, std_wait)]
    
    mean_x_dest = coef['rider_dest_x_mean']
    mean_y_dest = coef['rider_dest_y_mean']
    std_dest = coef['dropoff_std']
    rider_dest_loc = [fast_truncnorm(mean_x_dest, std_dest), fast_truncnorm(mean_y_dest, std_dest)]

    riders[next_rider_id] = {
        "matched": 0,
        "waiting_location": rider_wait_loc,
        "destination": rider_dest_loc,
        "pickup_time": None,
        "arrival_time": None,
        "abandon_time": None,
        "sys_enter_time": TNOW
    }

    drivers, riders, surge = rider_awaiting_driver(drivers, next_rider_id, riders, TNOW, coef)
    return drivers, riders, surge

def ride_completion(drivers, driver_id, riders, kpi, TNOW, coef):
    """
    Update driver/rider stats after ride completion and append new KPI
    """
    rider_id = drivers[driver_id]["current_rider"]

    kpi["waiting_times"].append(
        float(riders[rider_id]["pickup_time"] - riders[rider_id]["sys_enter_time"])
    )

    del riders[rider_id]

    if drivers[driver_id]["shift_end"] <= TNOW:
        drivers, kpi = driver_offline(drivers, driver_id, kpi, TNOW)
    else:
        drivers[driver_id]["matched"] = 0
        drivers[driver_id]["current_rider"] = None
        drivers, riders = driver_awaiting_rider(drivers, driver_id, riders, TNOW, coef)

    return drivers, riders, kpi

def driver_offline(drivers, driver_id, kpi, TNOW):
    """
    Update driver KPIs when going offline
    """
    kpi["avg_hourly_earnings"].append(
        float(drivers[driver_id]["total_earnings"] / (TNOW - drivers[driver_id]["shift_start"]))
    )
    kpi["prop_resting_times"].append(
        float(drivers[driver_id]["total_rest_time"] / (TNOW - drivers[driver_id]["shift_start"]))
    )
    del drivers[driver_id]
    return drivers, kpi

def rider_abandonment(riders, id_r, kpi, TNOW):
    # update riders kpi values - abandonment count
    
    
    
    kpi["abandon_count"] += 1
    # remove rider data from dictionary
    kpi["abandon_times"].append(TNOW)

    del riders[id_r]

    return riders, kpi
# ---------------------------
# Main Simulation Function
# ---------------------------

def simulate_boxcar(Termination, coef):
    drivers = {}
    riders = {}
    next_driver_id = 1
    next_rider_id = 1
    surge = False

    kpi = { # Drivers: Count average earnings per hour for each driver and resting times for each driver between trips, Riders: count number of abandoned trips and waiting times for each trip
        "avg_hourly_earnings": [],
        "prop_resting_times": [],
        "waiting_times": [],
        "abandon_count": 0,
        "total_number_riders": 0,
        "abandon_times": [],      
        "driver_count_times": []
    }
    
    EventCalendar = np.zeros(6)
    EventCalendar[0] = npr.exponential(1 / coef["driver_arrival"])
    EventCalendar[1] = npr.exponential(1 / coef["rider_arrival"])
    EventCalendar[5] = Termination
    EventCalendar[[2,3,4]] = Termination + 1

    def next_ride_completion(drivers, Termination):
        event_time = Termination + 1
        driver_id = None
        for d_id, d in drivers.items():
            if d["matched"] == 1 and d["dropoff_time"] < event_time:
                event_time = d["dropoff_time"]
                driver_id = d_id
        return event_time, driver_id

    def next_driver_offline(drivers, Termination):
        event_time = Termination + 1
        driver_id = None
        for d_id, d in drivers.items():
            if d["matched"] == 0 and d["shift_end"] < event_time:
                event_time = d["shift_end"]
                driver_id = d_id
        return event_time, driver_id

    def next_abandon(riders, Termination):
        event_time = Termination + 1
        rider_id = None
        for r_id, r in riders.items():
            if r["abandon_time"] is not None and r["abandon_time"] < event_time:
                event_time = r["abandon_time"]
                rider_id = r_id
        return event_time, rider_id

    # Pre-populate initial drivers at TNOW=0
    TNOW = 0
    for _ in range(coef.get("initial_drivers", 10)):
        drivers, riders = driver_enter_sys(drivers, next_driver_id, riders, TNOW, coef)
        next_driver_id += 1
        
    

    while TNOW < Termination:
        EventCalendar[2], rc_driver_id = next_ride_completion(drivers, Termination)
        EventCalendar[3], off_driver_id = next_driver_offline(drivers, Termination)
        EventCalendar[4], abandon_rider_id = next_abandon(riders, Termination)

        TNEXT = np.min(EventCalendar)
        TypeNEXT = np.argmin(EventCalendar)
        TNOW = TNEXT
        kpi["driver_count_times"].append((TNOW, len(drivers))) 


        if TypeNEXT == 0:
            # Use slower arrival rate when driver count exceeds threshold
            threshold = coef.get("driver_count_threshold", float("inf"))
            if len(drivers) >= threshold:
                arrival_rate = coef.get("driver_arrival_high_count", coef["driver_arrival"])
            elif surge:
                arrival_rate = coef["driver_arrival_surge"]
            else:
                arrival_rate = coef["driver_arrival"]

            drivers, riders = driver_enter_sys(drivers, next_driver_id, riders, TNOW, coef)
            next_driver_id += 1
            EventCalendar[0] = TNOW + npr.exponential(1 / arrival_rate)

        elif TypeNEXT == 1:
            drivers, riders, surge = rider_enter_sys(drivers, riders, next_rider_id, TNOW, coef)
            next_rider_id += 1
            EventCalendar[1] = TNOW + npr.exponential(1 / coef["rider_arrival"])
            kpi["total_number_riders"] += 1

        elif TypeNEXT == 2:
            drivers, riders, kpi = ride_completion(drivers, rc_driver_id, riders, kpi, TNOW, coef)

        elif TypeNEXT == 3:
            drivers, kpi = driver_offline(drivers, off_driver_id, kpi, TNOW)

        elif TypeNEXT == 4:
            riders, kpi = rider_abandonment(riders, abandon_rider_id, kpi, TNOW)

        elif TypeNEXT == 5:
            break

    return kpi