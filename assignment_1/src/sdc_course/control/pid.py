from collections import deque
import math
import numpy as np
from sdc_course.utils.utility import *



class PIDLongitudinalController:
    """
    PIDLongitudinalController implements longitudinal control using a PID.
    """

    def __init__(self, vehicle, dt, K_P, K_D, K_I):
        """
        Constructor method.

        :param vehicle: actor to apply to local planner logic onto
        :param dt: time differential in seconds
        :param K_P: Proportional term
        :param K_D: Differential term
        :param K_I: Integral term
        """

        self._vehicle = vehicle
        self._dt = dt
        self._k_p = K_P
        self._k_d = K_D
        self._k_i = K_I
        self._error_buffer = deque(maxlen=10)

    def run_step(self, target_velocity_ms, debug=False):
        """
        Execute one step of longitudinal control to reach a given target velocity.

        :param target_velocity_ms: target velocity in m/s
        :param debug: boolean for debugging
        :return: throttle control
        """
        current_velocity_ms = get_velocity_ms(self._vehicle)

        if debug:
            print("Current velocity = {}".format(current_velocity_ms))

        return self._pid_control(target_velocity_ms, current_velocity_ms)

    def _pid_control(self, target_velocity_ms, current_velocity_ms):
        """
        Estimate the throttle/brake of the vehicle based on the PID equations

        :param target_velocity_ms:  target velocity in m/s
        :param current_velocity_ms: current velocity of the vehicle in m/s
        :return: throttle/brake control
        """
        acceleration = 0.0
        #######################################################################
        ################## TODO: IMPLEMENT LONGITUDINAL PID CONTROL HERE ######
        #######################################################################
        error = target_velocity_ms - current_velocity_ms
        P = self._k_p * error
        I = self._k_i * error * self._dt
        D = self._k_d * (error /self._dt)
        acceleration = P+I+D
        return acceleration


class PIDLateralController:
    """
    PIDLateralController implements lateral control using a PID.
    """

    def __init__(self, vehicle, dt, K_P, K_D, K_I):
        """
        Constructor method.

        :param vehicle: actor to apply to local planner logic onto
        :param dt: time differential in seconds
        :param K_P: Proportional term
        :param K_D: Differential term
        :param K_I: Integral term
        """
        self._vehicle = vehicle
        self._dt = dt
        self._k_p = K_P
        self._k_d = K_D
        self._k_i = K_I
        self._error_buffer = deque(maxlen=10)

    def run_step(self, waypoints):
        """
        Execute one step of lateral control to steer
        the vehicle towards a certain waypoin.

        :param waypoint: target waypoint
        :return: steering control
        """
        return self._pid_control(waypoints, self._vehicle.get_transform())

    def _get_steering_direction(self, v1, v2):
        """
        Note that Carla uses a left hand coordinate system, this is why a positive
        cross product requires a negative steering direction.
        :param v1: vector between vehicle and waypoint
        :param v2: vector in direction of vehicle
        :return: steering direction
        """
        cross_prod = v1[0] * v2[1] - v1[1] * v2[0]
        if cross_prod >= 0:
            return -1
        return 1

    def _pid_control(self, waypoints, vehicle_transform):
        """
        Estimate the steering angle of the vehicle based on the PID equations

        :param waypoints: local waypoints
        :param vehicle_transform: current transform of the vehicle
        :return: steering control
        """
        steering = 0.0
        ######################################################################
        ################## TODO: IMPLEMENT LATERAL PID CONTROL HERE ###########
        #######################################################################
        x_wp = waypoints[0][0]
        y_wp = waypoints[0][1]
        x_car = vehicle_transform.location.x
        y_car = vehicle_transform.location.y
        cte = np.sqrt((y_wp-y_car)**2+(x_wp-x_car)**2) 
        
        #des_ang = math.atan((y_wp-y_car)/(x_wp-y_car))
        #yaw_car = vehicle_transform.rotation.yaw
        next_waypoint = get_nearest_waypoint(self._vehicle,waypoints)
        v1 = [x_car - next_waypoint[0][0], y_car - next_waypoint[0][1] ]
        v2 = [vehicle_transform.get_forward_vector().x,vehicle_transform.get_forward_vector().y]
        #print(f" waypoints : {waypoints [0]}, Transform : {vehicle_transform}")
        #print(f" Transform : {type(vehicle_transform.location.x)}")
        P = self._k_p * cte 
        I = self._k_i * cte * self._dt 
        D = self._k_d * (cte /self._dt)
        steering = -(P+I+D) * self._get_steering_direction(v1, v2)
        if (steering>0.5):
            steering = 0.5
        elif (steering<-0.5):
            steering = -0.5
        print(f"{cte}, P : {P}, I : {I}, D: {D}")
        return steering
