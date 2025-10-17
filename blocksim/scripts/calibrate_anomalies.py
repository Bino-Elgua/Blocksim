import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, roc_curve
import csv
import json
from typing import List, Tuple
import matplotlib.pyplot as plt
import pickle

class AnomalyCalibrator:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.threshold = 0.5
        self.roc_data = {}

    def load_flight_csv(self, filepath: str, label: str) -> Tuple[np.ndarray, List[str]]:
        features = []
        labels = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            prev_alt, prev_batt, prev_lat, prev_lon, prev_time = None, None, None, None, None
            for row in reader:
                try:
                    alt = float(row['altitude'])
                    batt = float(row['battery'])
                    lat = float(row['gps_lat'])
                    lon = float(row['gps_lon'])
                    time_s = float(row['timestamp'])
                    accel_x = float(row.get('accel_x', 0))
                    accel_y = float(row.get('accel_y', 0))
                    accel_z = float(row.get('accel_z', 0))
                    
                    if prev_alt is not None:
                        dt = time_s - prev_time if prev_time else 0.1
                        alt_rate = (alt - prev_alt) / dt if dt > 0 else 0
                        batt_drain = (prev_batt - batt) / dt if dt > 0 else 0
                        gps_speed = np.sqrt((lat - prev_lat)**2 + (lon - prev_lon)**2) * 111000 / dt if dt > 0 else 0
                        accel_mag = np.sqrt(accel_x**2 + accel_y**2)
                        
                        # PHYSICS CROSS-CHECKS
                        alt_integral_error = abs(alt - (prev_alt + accel_z * dt))
                        energy_ratio = (0.5 * 1.5 * gps_speed**2) / max(batt_drain * 3.7 * dt, 0.01)
                        
                        features.append([
                            alt_rate, batt_drain, gps_speed, accel_mag,
                            alt_integral_error, energy_ratio
                        ])
                        labels.append(label)
                    
                    prev_alt, prev_batt, prev_lat, prev_lon, prev_time = alt, batt, lat, lon, time_s
                except (ValueError, KeyError):
                    continue
        
        return np.array(features), labels

    def calibrate_from_flights(self, good_flights: List[str], bad_flights: List[str]) -> None:
        good_features = []
        for fp in good_flights:
            features, _ = self.load_flight_csv(fp, 'good')
            good_features.append(features)
        
        good_features = np.vstack(good_features) if good_features else np.empty((0, 6))
        
        bad_features = []
        for fp in bad_flights:
            features, _ = self.load_flight_csv(fp, 'bad')
            bad_features.append(features)
        
        bad_features = np.vstack(bad_features) if bad_features else np.empty((0, 6))
        
        if len(good_features) == 0:
            raise ValueError("No good flight data")
        
        self.scaler.fit(good_features)
        good_scaled = self.scaler.transform(good_features)
        bad_scaled = self.scaler.transform(bad_features)
        
        self.model.fit(good_scaled)
        
        good_scores = self.model.decision_function(good_scaled)
        bad_scores = self.model.decision_function(bad_scaled)
        
        y_true = np.concatenate([np.zeros(len(good_scores)), np.ones(len(bad_scores))])
        y_scores = np.concatenate([good_scores, bad_scores])
        
        fpr, tpr, thresholds = roc_curve(y_true, -y_scores)
        self.roc_data = {
            "auc": roc_auc_score(y_true, -y_scores),
            "fpr": fpr.tolist(),
            "tpr": tpr.tolist(),
            "thresholds": thresholds.tolist()
        }
        
        idx = int(np.argmax(tpr >= 0.93)) if len(tpr) else 0
        self.threshold = float(thresholds[idx]) if idx < len(thresholds) else 0.5
        
        print(f"AUC: {self.roc_data['auc']:.3f}")
        print(f"Threshold for 93% TPR: {self.threshold:.3f}")

    def save_model(self, path: str) -> None:
        with open(path, 'wb') as f:
            pickle.dump((self.model, self.scaler, self.threshold), f)
        
        with open(path.replace('.pkl', '.json'), 'w') as f:
            json.dump({
                "threshold": self.threshold,
                "auc": self.roc_data.get("auc", 0),
                "features": 6,
                "model_version": "v1.1_physics"
            }, f, indent=2)

    def load_model(self, path: str) -> None:
        with open(path, 'rb') as f:
            self.model, self.scaler, self.threshold = pickle.load(f)

if __name__ == "__main__":
    calibrator = AnomalyCalibrator()
    
    good_flights = ["flight_001_good.csv", "flight_002_good.csv"]  # Expand to 40
    bad_flights = ["flight_001_bad.csv", "flight_002_bad.csv"]  # Expand to 10
    
    calibrator.calibrate_from_flights(good_flights, bad_flights)
    calibrator.save_model("../models/anomaly_v1.1_physics.pkl")
    
    fpr, tpr, _ = calibrator.roc_data["fpr"], calibrator.roc_data["tpr"], calibrator.roc_data["thresholds"]
    plt.plot(fpr, tpr, label=f"ROC (AUC = {calibrator.roc_data['auc']:.3f})")
    plt.plot([0,1], [0,1], 'k--')
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title("Anomaly Detector ROC Curve (6 Features)")
    plt.legend()
    plt.savefig("roc_curve_physics.png")
    plt.show()
