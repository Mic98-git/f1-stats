from flask import Flask, jsonify, request
from flasgger import Swagger
import pandas as pd
import os

app = Flask(__name__)
app.config['SWAGGER'] = {
    'title': 'Formula 1 stats',
}
Swagger(app)

data_directory = os.path.join(os.path.dirname(__file__), "data")

# Load and parse JSON files into DataFrames
def load_data():
    try:
        circuits = pd.read_json(os.path.join(data_directory, "circuits.json"))
        drivers = pd.read_json(os.path.join(data_directory, "drivers.json"))
        standings = pd.read_json(os.path.join(data_directory, "driver_standings.json"))
        lap_times = pd.read_json(os.path.join(data_directory, "lap_times.json"))
        races = pd.read_json(os.path.join(data_directory, "races.json"))
        return circuits, drivers, standings, lap_times, races
    except FileNotFoundError as e:
        print({"error": f"File not found: {e}"})
        exit()
    except pd.errors.EmptyDataError as e:
        print({"error": f"Empty data: {e}"})
        exit()
    except Exception as e:
        print({"error": f"An error occurred: {e}"})
        exit()

circuits_df, drivers_df, standings_df, lap_times_df, races_df = load_data()

@app.route("/driver-standings", methods=["GET"])
def get_driver_standings():
    """
    Get all driver standings.
    ---
    tags:
      - Driver standings
    responses:
      200:
        description: List of driver standings
        schema:
          type: array
          items:
            type: object
            properties:
              driverStandingsId:
                type: integer
                example: 1
              raceId:
                type: integer
                example: 18
              points:
                type: integer
                example: 10
              position:
                type: integer
                example: 1
              positionText:
                type: string
                example: "1"
              wins:
                type: integer
                example: 1
    """
    # Check for missing values
    # print(standings_df.isnull().sum()) -> 1 null value for positionText
    standings_df["positionText"] = standings_df["positionText"].fillna(0).astype(int).astype(str)
    return jsonify(standings_df.to_dict(orient="records"))

@app.route("/lap-times", methods=["GET"])
def get_lap_times():
    """
    Get all lap times.
    ---
    tags:
      - Lap times
    responses:
      200:
        description: List of lap times
        schema:
          type: array
          items:
            type: object
            properties:
              raceId:
                type: integer
                example: 1
              driverId:
                type: integer
                example: 5
              lap:
                type: integer
                example: 12
              position:
                type: integer
                example: 1
              time:
                type: string
                example: "1:20.567"
              milliseconds:
                type: integer
                example: 120567
    """
    return jsonify(lap_times_df.to_dict(orient="records"))

@app.route("/races", methods=["GET"])
def get_races():
    """
    Get all races.
    ---
    tags:
      - Races
    responses:
      200:
        description: List of races
        schema:
          type: array
          items:
            type: object
            properties:
              raceId:
                type: integer
                example: 1
              year:
                type: integer
                example: 2024
              round:
                type: integer
                example: 1
              name:
                type: string
                example: Bahrain Grand Prix
              circuitId:
                type: integer
                example: 1
    """
    return jsonify(races_df.to_dict(orient="records"))

@app.route("/circuits", methods=["GET"])
def get_circuits():
    """
    Get all circuits.
    ---
    tags:
      - Circuits
    responses:
      200:
        description: List of circuits
        schema:
          type: array
          items:
            type: object
            properties:
              circuitId:
                type: integer
                example: 1
              name:
                type: string
                example: Albert Park Grand Prix Circuit
              country:
                type: string
                example: Australia
    """
    return jsonify(circuits_df.to_dict(orient="records"))

@app.route("/drivers", methods=["GET"])
def get_drivers():
    """
    Get all drivers.
    ---
    tags:
      - Drivers
    responses:
      200:
        description: List of drivers
        schema:
          type: array
          items:
            type: object
            properties:
              code:
                type: string
                example: HAM
              driverId:
                type: integer
                example: 1
              forename:
                type: string
                example: Lewis
              surname:
                type: string
                example: Hamilton
              nationality:
                type: string
                example: British
    """
    return jsonify(drivers_df.to_dict(orient="records"))

@app.route("/circuit-summary", methods=["GET"])
def circuit_summary():
    """
    Get a summary for each circuit.
    ---
    tags:
      - Circuits
    parameters:
      - name: name
        in: query
        type: string
        required: false
        description: Filter circuits by name
    responses:
      200:
        description: A summary per circuit
      500:
        description: Internal server error
    """
    try:
      # Merge data to compute total races and fastest lap for each circuit
      circuit_race_data = pd.merge(circuits_df, races_df, on="circuitId")
      total_races = circuit_race_data.groupby("circuitId")["raceId"].nunique()
      lap_race_data = pd.merge(circuit_race_data, lap_times_df, on="raceId")
      fastest_laps = lap_race_data.groupby("circuitId")["milliseconds"].min().reset_index()

      # Create summary
      circuit_summary_df = pd.merge(
          circuits_df,
          total_races.rename("total_races_completed"),
          left_on="circuitId",
          right_index=True
      )
      circuit_summary_df = pd.merge(
          circuit_summary_df,
          fastest_laps.rename(columns={"milliseconds": "fastest_lap_milliseconds"}),
          on="circuitId",
          how="left" # Use left join to keep all circuits
      )

      # Handle NaN values and ensure JSON-serializable types
      # print(circuit_summary_df.isnull().sum()) -> fastest laps has 36 null values
      circuit_summary_df["fastest_lap_milliseconds"] = circuit_summary_df["fastest_lap_milliseconds"].fillna(0).astype(int)

      # Optional filtering by circuit name
      circuit_name = request.args.get("name")
      if circuit_name:
          filtered_df = circuit_summary_df[circuit_summary_df["name"].str.contains(circuit_name, case=False, na=False)]
          if filtered_df.empty:
              return jsonify({"error": "No circuit found with the given name"}), 404
          return jsonify(filtered_df.to_dict(orient="records"))
      
      return jsonify(circuit_summary_df.to_dict(orient="records"))
    
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/driver-summary", methods=["GET"])
def driver_summary():
    """
    Get a summary for each driver.
    ---
    tags:
      - Drivers
    parameters:
      - name: code
        in: query
        type: string
        required: false
        description: Filter drivers by code
      - name: id
        in: query
        type: int
        required: false
        description: Filter drivers by id
    responses:
      200:
        description: A summary per driver
      500:
        description: Internal server error
    """
    try:
      race_driver_data = pd.merge(drivers_df, standings_df, on="driverId")
      podium_finishes = race_driver_data[race_driver_data["position"].isin([1, 2, 3])]
      podium_count = podium_finishes.groupby("driverId")["position"].count()
      total_races_entered = race_driver_data.groupby("driverId")["raceId"].nunique()

      # Create summary
      driver_summary_df = pd.merge(
          drivers_df,
          podium_count.rename("podium_finishes"),
          left_on="driverId",
          right_index=True,
          how="left"
      )
      driver_summary_df = pd.merge(
          driver_summary_df,
          total_races_entered.rename("total_races_entered"),
          on="driverId",
          how="left"
      )

      # Handle NaN values and ensure JSON-serializable types
      # print(driver_summary_df.isnull().sum()) -> 737 null values for podium_finshes and 7 for total_race_entered
      driver_summary_df["podium_finishes"] = driver_summary_df["podium_finishes"].fillna(0).astype(int)
      driver_summary_df["total_races_entered"] = driver_summary_df["total_races_entered"].fillna(0).astype(int)

      # Optional filtering
      driver_code = request.args.get("code")
      driver_id = request.args.get("id")

      # Filter by driver code if provided
      if driver_code:
          filtered_df = driver_summary_df[driver_summary_df["code"].str.contains(driver_code, case=False, na=False)]
          if filtered_df.empty:
              return jsonify({"error": "No driver found with the given code"}), 404
          return jsonify(filtered_df.to_dict(orient="records"))

      # Filter by driver ID if provided
      if driver_id:
          try:
              driver_id = int(driver_id)  # Convert driver_id to integer
          except ValueError:
              return jsonify({"error": "Driver ID must be an integer"}), 400
          filtered_df = driver_summary_df[driver_summary_df["driverId"] == driver_id]
          if filtered_df.empty:
              return jsonify({"error": "No driver found with the given ID"}), 404
          return jsonify(filtered_df.to_dict(orient="records"))

      # Return full summary if no filters are provided
      return jsonify(driver_summary_df.to_dict(orient="records"))
  
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)