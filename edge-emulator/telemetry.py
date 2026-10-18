"""Telemetry v1: Unix UTC seconds, RPM, volts, amps, Celsius, g and deg/s."""
import math
MOTORS = ("front_left", "front_right", "rear_left", "rear_right")

def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a number")
    if not math.isfinite(value):
        raise ValueError("Expected a finite number")
    return float(value)

def validate(data):
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object")
    if data.get("schema_version", 1) != 1:
        raise ValueError("Unsupported schema_version")
    stamp = number(data["timestamp"])
    if not 0 < stamp < 4102444800:
        raise ValueError("timestamp must be Unix seconds before 2100")
    if not isinstance(data["agv_id"], str) or not data["agv_id"].strip():
        raise ValueError("Missing agv_id")
    if "schema_version" in data:
        if not isinstance(data.get("session_id"), str) or not data["session_id"]:
            raise ValueError("Missing session_id")
        if type(data.get("sequence")) is not int or data["sequence"] < 0:
            raise ValueError("Invalid sequence")
    telemetry = data["telemetry"]
    power = telemetry["power_supply"]
    values = [stamp, data["agv_id"], number(power["bus_voltage_V"]), number(power["current_A"])]
    for name in MOTORS:
        motor = telemetry["motors"][name]
        values.extend((number(motor["speed_rpm"]), number(motor["temp_C"])))
    for sensor in ("accel_g", "gyro_dps"):
        values.extend(number(telemetry["imu"][sensor][axis]) for axis in ("x", "y", "z"))
    return tuple(values)
