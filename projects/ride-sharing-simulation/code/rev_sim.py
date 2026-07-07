import math
import numpy as np
import numpy.random as npr
import scipy
from scipy import stats as scs


# function for storing driver data as they enter system
def driver_enter_sys(drivers, next_driver_id, riders, TNOW, coef):
    '''
    Deals with new driver in system, adds them to our dictionary
    
    :param drivers: dictionary of all drivers in system at TNOW
    :param riders: dictionary of all riders in system at TNOW
    :param TNOW: Current time
    '''
    def fast_truncnorm(mean, std):
        while True:
            x = np.random.normal(mean, std)
            if 0 <= x <= 20:
                return x

    # determine driver's start location
    mean_x_driver = coef['rider_dest_x_mean']
    mean_y_driver = coef['rider_dest_y_mean']
    std_driver = coef['init_std']
    driver_loc = [fast_truncnorm(mean_x_driver, std_driver), fast_truncnorm(mean_y_driver, std_driver)]
    
    # determine driver's shift end time
    offline_time = TNOW + npr.uniform(coef["shift_time_lb"],coef["shift_time_ub"])

    # set up new driver in drivers dictionary
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

    # Check if there are riders waiting, if so, match with a rider
    drivers, riders = driver_awaiting_rider(drivers, next_driver_id, riders, TNOW, coef)

    return drivers, riders


# function for storing rider data as they enter the system
def rider_enter_sys(drivers, riders, next_rider_id, TNOW, coef):
    '''
    Deals with new rider in system, adds them to our dictionary
    
    :param drivers: dictionary of all drivers in system at TNOW
    :param riders: dictionary of all riders in system at TNOW
    :param TNOW: Current time
    '''
    def fast_truncnorm(mean, std):
        while True:
            x = np.random.normal(mean, std)
            if 0 <= x <= 20:
                return x

    # determine rider's waiting location 
    mean_x_wait = coef['rider_init_x_mean']
    mean_y_wait = coef['rider_init_y_mean']
    std_wait = coef['init_std']
    rider_wait_loc = [fast_truncnorm(mean_x_wait, std_wait), fast_truncnorm(mean_y_wait, std_wait)]
    
    # determine rider's dropoff location
    mean_x_dest = coef['rider_dest_x_mean']
    mean_y_dest = coef['rider_dest_y_mean']
    std_dest = coef['dropoff_std']
    rider_dest_loc = [fast_truncnorm(mean_x_dest, std_dest), fast_truncnorm(mean_y_dest, std_dest)]

    # set up new rider in rider's dictionary
    riders[next_rider_id] = {
        "matched": 0,
        "waiting_location": rider_wait_loc,
        "destination": rider_dest_loc,
        "pickup_time": None,
        "arrival_time": None,
        "abandon_time": None,
        "sys_enter_time": TNOW
    }

    # When entering system, check if there are any available drivers
    drivers, riders = rider_awaiting_driver(drivers, next_rider_id, riders, TNOW, coef)
    
    return drivers, riders



def driver_awaiting_rider(drivers, id, riders, TNOW, coef):
    '''
    Attempts to match available driver (id) to closest waiting rider. If none available, deals with them as unmatched status
    
    :param drivers: dictionary of all drivers in system at TNOW
    :param id: id of available driver
    :param riders: dictionary of all riders in system at TNOW
    '''
    # driver destination
    driver_loc = drivers[id]["destination"]

    # define closest rider and minimum distance
    min_distance = float("inf")

    # find riders that are available
    unmatched_riders = [k for k, r in riders.items() if r["matched"]==0]

    # for all available riders
    if len(unmatched_riders) > 0:
        # for each rider in the system
        for i in unmatched_riders:
            # define rider waiting location
            rider_loc = riders[i]["waiting_location"]
            
            # determine distances
            distance = trip_stats(driver_loc, rider_loc, coef)
            
            # if distance is smallest thus far, save it
            if distance < min_distance:
                min_distance = distance
                # determine closest rider index
                c = i
        
        # update driver and rider values based on this new trip if a driver is actually available
        drivers, riders = new_trip_update(drivers, id, riders, c, TNOW, coef)

    # there are no available riders, deal with driver as unmatched and waiting
    else:
        drivers[id]["dropoff_time"] = None
        drivers[id]["rest_start"] = TNOW
    
    return drivers, riders


def rider_awaiting_driver(drivers, id, riders, TNOW, coef):
    '''
    Attempts to match waiting rider (id) to closest available driver. If none available, deals with them as unmatched status
    
    :param drivers: dictionary of all drivers in system at TNOW
    :param id: id of waiting rider
    :param riders: dictionary of all riders in system at TNOW
    :param TNOW: Current time
    '''
    # rider location
    rider_loc = riders[id]["waiting_location"]

    # define closest rider and minimum distance
    min_distance = float("inf")

    # find drivers that are available
    unmatched_drivers = [k for k, d in drivers.items() if d["matched"]==0]

    # for all available drivers
    if len(unmatched_drivers) > 0:
        # for each rider in the system
        for i in unmatched_drivers:
            # define rider waiting location
            driver_loc = drivers[i]["destination"]
            
            # determine distances
            distance = trip_stats(driver_loc, rider_loc, coef)
            
            # if distance is smallest thus far, save it
            if distance < min_distance:
                min_distance = distance
                # determine closest driver
                c = i

        # update driver and rider values based on this new trip if a driver is actually available
        drivers, riders = new_trip_update(drivers, c, riders, id, TNOW, coef)

    # else there is no driver available, set a patience time
    else:
        riders[id]["abandon_time"] = TNOW + npr.exponential(1/coef["abandon"])

    return drivers, riders


def new_trip_update(drivers, id_d, riders, id_r, TNOW, coef):
    ## NOW: we work out the distance from driver -> pickup and pickup -> destination
    # update rider and driver status to matched
    riders[id_r]["matched"] = 1
    drivers[id_d]["matched"] = 1

    # update driver's current rider and add any rest time taken, update rest_start back to None
    drivers[id_d]["current_rider"] = id_r
    if drivers[id_d]["rest_start"] is not None:
        drivers[id_d]["total_rest_time"] += TNOW - drivers[id_d]["rest_start"]
        drivers[id_d]["rest_start"] = None

    # find distance and RV time from driver's location to pickup
    pickup_trip_dist, pickup_trip_time = trip_stats(drivers[id_d]["destination"], riders[id_r]["waiting_location"], coef, Time=True)
    # find distance and RV time from pickup to destination
    dest_trip_dist, dest_trip_time = trip_stats(riders[id_r]["waiting_location"], riders[id_r]["destination"], coef, Time=True)
    
    # so time at drop-off
    dropoff_time = TNOW + pickup_trip_time + dest_trip_time
    
    # update driver status
    drivers[id_d]["destination"] = riders[id_r]["destination"] # driver's next waiting location will be the rider's destination
    drivers[id_d]["dropoff_time"] = dropoff_time
    drivers[id_d]["total_earnings"] += 3 + 1.8*dest_trip_dist - 0.2*pickup_trip_dist # base pay of £3, plus £2 payment per mile of trip with rider, minus £0.2 petrol cost per mile travelled

    # update rider status
    riders[id_r]["pickup_time"] = TNOW + pickup_trip_time
    riders[id_r]["arrival_time"] = dropoff_time
    riders[id_r]["abandon_time"] = None

    return drivers, riders


def trip_stats(loc1, loc2, coef, Time=False):
    '''
    Determines distance and estimated time between two locations
    
    :param loc1: Starting location
    :param loc2: Finishing location
    '''
    dist = math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
    if Time:
        time = npr.uniform(coef["trip_time_lb"], coef["trip_time_ub"]) * dist/20
        return dist, time
    else:
        return dist


def ride_completion(drivers, id_d, riders, kpi, TNOW, coef):
    '''
    Update driver/rider stats after ride completion and append new performance metrics to kpi
    
    :param drivers: dictionary of all drivers in system at TNOW
    :param id_d: id of driver of completed trip
    :param riders: dictionary of all riders in system at TNOW
    :param id_r: id of rider of completed trip
    :param kpi: dictionary of performance metrics of drivers and riders
    :param TNOW: Current time
    '''
    # find rider of completed trip
    id_r = drivers[id_d]["current_rider"]

    # update riders kpi values - waiting time from system arrival to pickup time
    kpi["waiting_times"].append(
        float(riders[id_r]["pickup_time"] - riders[id_r]["sys_enter_time"])
        )
    # remove rider data from dictionary
    del riders[id_r]

    # check if driver's shift has ended
    if drivers[id_d]["shift_end"] <= TNOW:
        driver_offline(drivers, id_d, kpi, TNOW)
    # else update driver status 
    else:
        drivers[id_d]["matched"] = 0
        drivers[id_d]["current_rider"] = None
        drivers, riders = driver_awaiting_rider(drivers, id_d, riders, TNOW, coef) 
    
    return drivers, riders, kpi
    

def driver_offline(drivers, id_d, kpi, TNOW):
    '''
    Driver going offline
    
    :param drivers: Description
    :param id_d: Description
    :param kpi: Description
    :param TNOW: Description
    '''
    # correct actual shift end time for driver
    # update drivers kpi values (now that the driver's shift has ended)
    kpi["avg_hourly_earnings"].append(
        float(drivers[id_d]["total_earnings"] / (TNOW - drivers[id_d]["shift_start"]))
        )
    kpi["prop_resting_times"].append(
        float(drivers[id_d]["total_rest_time"] / (TNOW - drivers[id_d]["shift_start"]))
        )
    del drivers[id_d]
    return drivers, kpi

        
def rider_abandonment(riders, id_r, kpi):
    # update riders kpi values - abandonment count
    kpi["abandon_count"] += 1
    # remove rider data from dictionary
    del riders[id_r]

    return riders, kpi



def simulate_boxcar(Termination, coef):
    '''
    Simulation of the boxcar simulation
    
    :param Termination: Termination time of simulation
    '''
    # initialise drivers and riders
    drivers = {}
    riders = {}

    # initialise driver and rider IDs
    next_driver_id = 1
    next_rider_id = 1

    # initialise empty driver and rider performance metrics
    kpi = { # Drivers: Count average earnings per hour for each driver and resting times for each driver between trips, Riders: count number of abandoned trips and waiting times for each trip
        "avg_hourly_earnings": [],
        "prop_resting_times": [],
        "waiting_times": [],
        "abandon_count": 0,
        "total_number_riders": 0
    }

    # initialise an Event Calendar
    EventCalendar = np.zeros(6)
    # initialise next driver and rider arrival
    EventCalendar[0] = npr.exponential(1/coef["driver_arrival"])  # driver
    EventCalendar[1] = npr.exponential(1/coef["rider_arrival"]) # rider
    # initialise termination event
    EventCalendar[5] = Termination
    # MULTIVARIABLE EVENTS:
    # initialise ride completion, driver going offline and rider abandoning trip as infinity (Termination+1)
    EventCalendar[[2,3,4]] = Termination+1

    # define functions used to update these times in EventCalendar
    def next_ride_completion(drivers, Termination):
        # initialise event time and id setup
        event_time = Termination + 1
        id_d = None

        # find the driver with soonest dropoff time
        for driver_id, d in drivers.items():
            if d["matched"] == 1:
                if d["dropoff_time"] < event_time:
                    event_time = d["dropoff_time"]
                    id_d = driver_id

        # returns the time of this event, and the ids of the driver and rider involved
        return event_time, id_d
    
    def next_driver_offline(drivers, Termination):
        '''
        Determines next event for EventCalendar[2]: the next driver to go offline (assessing those that are not currently mid-job)
        
        :param drivers: dictionary of all online drivers in simulation
        :param Termination: termination time, end of simulation
        '''
        # initialise event time and id setup
        event_time = Termination + 1
        id_d = None
        # find the driver with soonest offline time
        for driver_id, d in drivers.items():
            if d["matched"] == 0:
                if d["shift_end"] < event_time:
                    event_time = d["shift_end"]
                    id_d = driver_id
        # returns the time of this event, and the id of the driver involved
        return event_time, id_d
    
    def next_abandon(riders, Termination):
        # initialise event type and id setup
        event_time = Termination + 1
        id_r = None

        # find next rider's abandon time 
        for rider_id, r in riders.items():
            if r["abandon_time"] is not None:
                if r["abandon_time"] < event_time:
                    event_time = r["abandon_time"]
                    id_r = rider_id
        # returns the time of this event, and the id of the rider involved
        return event_time, id_r

        

    # initialise time and event statuses
    TNOW = 0

    while TNOW < Termination:
        # update event statuses 
        # next ride completion
        EventCalendar[2], rc_id_d = next_ride_completion(drivers, Termination) 
        # next non-matched driver going offline
        EventCalendar[3], o_id_d = next_driver_offline(drivers, Termination)
        # next rider abandoning trip
        EventCalendar[4], a_id_r = next_abandon(riders, Termination)

        # find next event in Event Calendar
        TNEXT = min(EventCalendar) 
        TypeNEXT = np.argmin(EventCalendar) 
        # update time
        TNOW = TNEXT
        # if next event is a driver system arrival
        if TypeNEXT == 0:
            drivers, riders = driver_enter_sys(drivers, next_driver_id, riders, TNOW, coef)
            # update for next driver system arrival
            EventCalendar[0] = TNOW + npr.exponential(1/coef["driver_arrival"])
            next_driver_id += 1 

        # else if next event is a rider system arrival
        elif TypeNEXT == 1:
            drivers, riders = rider_enter_sys(drivers, riders, next_rider_id, TNOW, coef)
            # update for next rider system arrival
            EventCalendar[1] = TNOW + npr.exponential(1/coef["rider_arrival"]) 
            # add to kpi for total number of riders
            kpi["total_number_riders"] += 1
            next_rider_id += 1

        # else if next event is a ride completion
        elif TypeNEXT == 2:
            drivers, riders, kpi = ride_completion(drivers, rc_id_d, riders, kpi, TNOW, coef)

        # if next event is a non-matched driver leaving the system (going offline)
        elif TypeNEXT == 3:
            drivers, kpi = driver_offline(drivers, o_id_d, kpi, TNOW)

        # else if next event is a rider abandonment
        elif TypeNEXT == 4:
            riders, kpi = rider_abandonment(riders, a_id_r, kpi)

        # Else TypeNEXT = 5, Termination
            
    return kpi

