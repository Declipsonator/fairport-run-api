# Taken from https://web.archive.org/web/20070406100645/http://www.cs.uml.edu/~phoffman/xcinfo3.html

class Purdy(object):
    # Purdy table: [distance, standard_pace, distance, standard_pace, … , -1.0, 0.0]
    pace_table = [
        40.0, 11.000, 50.0, 10.9960, 60.0, 10.9830, 70.0, 10.9620,
        80.0, 10.934, 90.0, 10.9000, 100.0, 10.8600, 110.0, 10.8150,
        120.0, 10.765, 130.0, 10.7110, 140.0, 10.6540, 150.0, 10.5940,
        160.0, 10.531, 170.0, 10.4650, 180.0, 10.3960, 200.0, 10.2500,
        220.0, 10.096, 240.0, 9.9350, 260.0, 9.7710, 280.0, 9.6100,
        300.0, 9.455, 320.0, 9.3070, 340.0, 9.1660, 360.0, 9.0320,
        380.0, 8.905, 400.0, 8.7850, 450.0, 8.5130, 500.0, 8.2790,
        550.0, 8.083, 600.0, 7.9210, 700.0, 7.6690, 800.0, 7.4960,
        900.0, 7.3200, 1000.0, 7.18933, 1200.0, 6.98066, 1500.0, 6.75319,
        2000.0, 6.50015, 2500.0, 6.33424, 3000.0, 6.21913, 3500.0, 6.13510,
        4000.0, 6.07040, 4500.0, 6.01822, 5000.0, 5.97432, 6000.0, 5.90181,
        7000.0, 5.84156, 8000.0, 5.78889, 9000.0, 5.74211, 10000.0, 5.70050,
        12000.0, 5.62944, 15000.0, 5.54300, 20000.0, 5.43785, 25000.0, 5.35842,
        30000.0, 5.29298, 35000.0, 5.23538, 40000.0, 5.18263, 50000.0, 5.08615,
        60000.0, 4.99762, 80000.0, 4.83617, 100000.0, 4.68988, -1.0, 0.0
    ]

    def __init__(self, dist, time):
        """A class to score and convert running performances between distances
        Args:
            dist: the distance of the performance (in meters)
            time: the time of the performance (in seconds)
        """
        self.dist = dist
        self.time = time
        # self.score = self.score()


    def _fractional_lap_factor(self, distance=None):
        """
        Compute the fraction of a 400m lap represented by the given distance,
        mapped onto a 200m scale.  This accounts for partial laps beyond
        400m segments to approximate pacing adjustments.

        Args:
            distance (float, optional): distance in meters; defaults to self.distance_m

        Returns:
            float: (scaled_meters) / distance
        """
        if distance is None:
            distance = self.dist

        # No meaningful fraction for distances under 110m
        if distance < 110:
            return 0.0

        # Count full 400m laps and leftover meters
        full_400m_laps = distance // 400
        leftover_meters = distance - full_400m_laps * 400

        # Map leftover_meters into a 0–200m “partial‐lap” scale
        if leftover_meters <= 50:
            partial_lap_m = 0
        elif leftover_meters <= 150:
            partial_lap_m = leftover_meters - 50
        elif leftover_meters <= 250:
            partial_lap_m = 100
        elif leftover_meters <= 350:
            partial_lap_m = 100 + (leftover_meters - 250)
        else:  # leftover_meters > 350
            partial_lap_m = 200

        # Total “scaled” meters = 200m per full lap + partial_lap_m
        scaled_meters = full_400m_laps * 200 + partial_lap_m

        # Fractional lap factor
        return scaled_meters / distance

    def purdy_score(self, dist=None, time=None):
        """
        Compute the Purdy Points for a performance.

        Purdy tables give a standard pace for each distance; this routine
        interpolates the “standard” time, applies fatigue constants, and
        scales the athlete’s performance against that standard.

        Args:
            dist (float, optional): distance in meters; defaults to self.distance_m
            time (float, optional): performance time in seconds; defaults to self.time_s

        Returns:
            float: Purdy point score
        """
        if dist is None:
            dist = self.dist
        if time is None:
            time = self.time

        # Fatigue constants
        fatigue_const_1 = 0.2
        fatigue_const_2 = 0.08
        fatigue_const_3 = 0.0065

        # Find the segment in the pace table that brackets our distance
        idx = 0
        # d_temp holds the table distance at current index
        d_temp = self.pace_table[idx]

        # Advance through table until d_temp >= distance
        while d_temp > 0 and dist > d_temp:
            idx += 2
            d_temp = self.pace_table[idx]

        # If beyond table range, no score
        if d_temp < 0:
            return 0.0

        # Step back to get lower and upper bracketing entries
        upper_idx = idx
        lower_idx = idx - 2

        d_lower, pace_lower = self.pace_table[lower_idx], self.pace_table[lower_idx + 1]
        d_upper, pace_upper = self.pace_table[upper_idx], self.pace_table[upper_idx + 1]

        # Compute “standard” times at those bracket distances
        time_lower = d_lower / pace_lower
        time_upper = d_upper / pace_upper

        # Linearly interpolate to get standard time at our exact distance
        standard_time = (
            time_lower
            + (time_upper - time_lower) * (dist - d_lower) / (d_upper - d_lower)
        )

        # Athlete’s average velocity
        avg_velocity = dist / standard_time

        # Adjusted “virtual” time with fatigue correction
        adjusted_time = (
            standard_time
            + fatigue_const_1
            + fatigue_const_2 * avg_velocity
            + fatigue_const_3 * self._fractional_lap_factor(dist) * avg_velocity**2
        )

        # Compute scaling parameters
        k_factor = 0.0654 - 0.00258 * avg_velocity
        a_factor = 85.0 / k_factor
        b_parameter = 1.0 - 950.0 / a_factor

        # Final Purdy point score
        purdy_points = a_factor * (adjusted_time / time - b_parameter)

        return purdy_points


    def convert(self, dist, score=None):
        """
        Given a race distance and a desired Purdy point score, compute the
        performance time (seconds) that would produce that score.

        Args:
            dist (float): distance in meters
            score (float): desired Purdy point score

        Returns:
            float: required time in seconds to achieve target_score, or 0 if invalid
        """

        if not score:
            score = self.purdy_score()


        # Fatigue constants (same as in purdy_score)
        fatigue_c1 = 0.20
        fatigue_c2 = 0.08
        fatigue_c3 = 0.0065

        # --- Locate the bracketing segment in pace_table ---
        idx = 0
        table_distance = self.pace_table[idx]

        # Advance until we find the first table_distance >= distance_m
        while table_distance > 0 and dist > table_distance:
            idx += 2
            table_distance = self.pace_table[idx]

        # If we ran off the end (table_distance <= 0), invalid
        if table_distance <= 0:
            return 0.0

        # Step back to get lower and upper bracket entries
        upper_idx = idx
        lower_idx = idx - 2
        d_lower, pace_lower = self.pace_table[lower_idx], self.pace_table[lower_idx + 1]
        d_upper, pace_upper = self.pace_table[upper_idx], self.pace_table[upper_idx + 1]

        # --- Compute the “standard” time via linear interpolation ---
        time_lower = d_lower / pace_lower
        time_upper = d_upper / pace_upper
        standard_time = (
                time_lower
                + (time_upper - time_lower) * (dist - d_lower) / (d_upper - d_lower)
        )

        # Athlete’s average velocity (m/s) over the “standard” time
        avg_velocity = dist / standard_time

        # Compute the fractional lap factor exactly as in Performance._fractional_lap_factor
        def _lap_fraction_factor(dist):
            if dist < 110:
                return 0.0
            full_laps = dist // 400
            leftover = dist - full_laps * 400
            if leftover <= 50:
                part = 0
            elif leftover <= 150:
                part = leftover - 50
            elif leftover <= 250:
                part = 100
            elif leftover <= 350:
                part = 100 + (leftover - 250)
            else:
                part = 200
            scaled = full_laps * 200 + part
            return scaled / dist

        lap_factor = _lap_fraction_factor(dist)

        # Adjust “virtual” time with fatigue corrections
        adjusted_time = (
                standard_time
                + fatigue_c1
                + fatigue_c2 * avg_velocity
                + fatigue_c3 * lap_factor * avg_velocity ** 2
        )

        # Compute scaling parameters for inversion
        k_factor = 0.0654 - 0.00258 * avg_velocity
        a_factor = 85.0 / k_factor
        b_parameter = 1.0 - 950.0 / a_factor

        # Invert: target_score = a_factor * (adjusted_time / t_sec - b_parameter)
        # => t_sec = adjusted_time / ((target_score / a_factor) + b_parameter)
        return adjusted_time / ((score / a_factor) + b_parameter)

