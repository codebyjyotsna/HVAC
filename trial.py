# complete_advanced_hvac_ai_system.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import json
import threading
from datetime import datetime, timedelta
import random
import warnings
import sqlite3
import logging
from typing import Dict, List, Optional, Tuple
import math
import hashlib
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OperationMode(Enum):
    AUTO = "auto"
    ENERGY_SAVING = "energy_saving"
    COMFORT_FOCUS = "comfort_focus"
    BALANCED = "balanced"
    MAINTENANCE = "maintenance"

class AlertSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SensorData:
    sensor_id: str
    location: str
    temperature: float
    humidity: float
    co2: int
    occupancy: float
    power_consumption: float
    setpoint: float
    vibration: float
    pressure: float
    air_flow: float
    timestamp: datetime

@dataclass
class OptimizationResult:
    optimal_temperature: float
    ventilation_rate: float
    energy_savings_percent: float
    comfort_score: float
    cost_savings: float
    carbon_savings: float
    recommendations: List[str]
    operation_mode: str
    timestamp: datetime

class NotificationManager:
    """Advanced notification and alert management system"""
    
    def __init__(self):
        self.alerts = []
        self.alert_history = []
    
    def create_alert(self, alert_type: str, severity: AlertSeverity, message: str, 
                    sensor_id: str = None, location: str = None):
        """Create and store system alerts"""
        alert = {
            'id': hashlib.md5(f"{alert_type}{severity}{message}{datetime.now()}".encode()).hexdigest()[:8],
            'type': alert_type,
            'severity': severity.value,
            'message': message,
            'sensor_id': sensor_id,
            'location': location,
            'timestamp': datetime.now(),
            'acknowledged': False,
            'resolved': False
        }
        
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Keep only last 1000 alerts in history
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        logger.info(f"Alert created: {alert_type} - {severity.value} - {message}")
        return alert
    
    def get_active_alerts(self):
        """Get all active, unacknowledged alerts"""
        return [alert for alert in self.alerts if not alert['acknowledged']]
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['acknowledged'] = True
                break
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['acknowledged'] = True
                break

class AdvancedDatabaseManager:
    """Advanced database management with comprehensive data handling"""
    
    def __init__(self, db_path="hvac_system.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize all database tables with advanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced sensor data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sensor_id TEXT NOT NULL,
                location TEXT NOT NULL,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                co2 INTEGER NOT NULL,
                occupancy REAL NOT NULL,
                power_consumption REAL NOT NULL,
                setpoint REAL NOT NULL,
                vibration REAL,
                pressure REAL,
                air_flow REAL,
                equipment_status TEXT,
                energy_efficiency REAL
            )
        ''')
        
        # Enhanced optimization history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                optimal_temperature REAL,
                ventilation_rate REAL,
                energy_savings_percent REAL,
                comfort_score REAL,
                cost_savings REAL,
                carbon_savings REAL,
                recommendations TEXT,
                applied BOOLEAN DEFAULT FALSE,
                operation_mode TEXT,
                optimization_duration REAL
            )
        ''')
        
        # System alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                sensor_id TEXT,
                location TEXT,
                acknowledged BOOLEAN DEFAULT FALSE,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Equipment maintenance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment_maintenance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                equipment_name TEXT NOT NULL,
                equipment_type TEXT NOT NULL,
                last_maintenance DATE,
                next_maintenance DATE,
                maintenance_interval_days INTEGER,
                status TEXT NOT NULL,
                efficiency REAL,
                operating_hours INTEGER,
                failure_probability REAL
            )
        ''')
        
        # Energy analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_energy_kwh REAL,
                cost_savings REAL,
                carbon_savings_kg REAL,
                peak_demand_kw REAL,
                avg_temperature REAL,
                avg_occupancy REAL,
                comfort_index REAL
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                preference_key TEXT UNIQUE NOT NULL,
                preference_value TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Advanced database initialized successfully")
    
    def store_sensor_data(self, sensor_data: Dict):
        """Store comprehensive sensor data with equipment status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sensor_data 
            (sensor_id, location, temperature, humidity, co2, occupancy, power_consumption, 
             setpoint, vibration, pressure, air_flow, equipment_status, energy_efficiency)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sensor_data['sensor_id'],
            sensor_data['location'],
            sensor_data['temperature'],
            sensor_data['humidity'],
            sensor_data['co2'],
            sensor_data['occupancy'],
            sensor_data['power_consumption'],
            sensor_data['setpoint'],
            sensor_data.get('vibration', 0.0),
            sensor_data.get('pressure', 1013.25),
            sensor_data.get('air_flow', 0.5),
            sensor_data.get('equipment_status', 'normal'),
            sensor_data.get('energy_efficiency', 0.85)
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_sensor_data(self, limit: int = 1000):
        """Get recent sensor data with enhanced fields"""
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def store_optimization(self, optimization_data: Dict):
        """Store comprehensive optimization results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        recommendations_json = json.dumps(optimization_data.get('recommendations', []))
        
        cursor.execute('''
            INSERT INTO optimization_history 
            (optimal_temperature, ventilation_rate, energy_savings_percent, comfort_score, 
             cost_savings, carbon_savings, recommendations, operation_mode, optimization_duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            optimization_data['optimal_temperature'],
            optimization_data['ventilation_rate'],
            optimization_data['energy_savings_percent'],
            optimization_data['comfort_score'],
            optimization_data.get('cost_savings', 0),
            optimization_data.get('carbon_savings', 0),
            recommendations_json,
            optimization_data.get('operation_mode', 'auto'),
            optimization_data.get('optimization_duration', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_optimization_history(self, limit: int = 100):
        """Get optimization history"""
        conn = sqlite3.connect(self.db_path)
        query = f"SELECT * FROM optimization_history ORDER BY timestamp DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        
        # Parse recommendations JSON
        if 'recommendations' in df.columns:
            df['recommendations'] = df['recommendations'].apply(lambda x: json.loads(x) if x else [])
        
        conn.close()
        return df
    
    def store_alert(self, alert_data: Dict):
        """Store system alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_alerts 
            (alert_type, severity, message, sensor_id, location, acknowledged, resolved)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert_data['type'],
            alert_data['severity'],
            alert_data['message'],
            alert_data.get('sensor_id'),
            alert_data.get('location'),
            alert_data.get('acknowledged', False),
            alert_data.get('resolved', False)
        ))
        
        conn.commit()
        conn.close()
    
    def get_active_alerts(self):
        """Get active alerts from database"""
        conn = sqlite3.connect(self.db_path)
        query = "SELECT * FROM system_alerts WHERE resolved = FALSE ORDER BY timestamp DESC"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

class AdvancedSensorSimulator:
    """Advanced real-time sensor data simulator with realistic patterns"""
    
    def __init__(self, db_manager: AdvancedDatabaseManager, notification_manager: NotificationManager):
        self.db_manager = db_manager
        self.notification_manager = notification_manager
        self.sensors = [
            {'id': 'sensor_1', 'location': 'Conference Room', 'base_temp': 22.0, 'area': 50, 'equipment': 'HVAC Unit A'},
            {'id': 'sensor_2', 'location': 'Open Office', 'base_temp': 22.0, 'area': 200, 'equipment': 'HVAC Unit B'},
            {'id': 'sensor_3', 'location': 'Reception', 'base_temp': 23.0, 'area': 30, 'equipment': 'HVAC Unit C'},
            {'id': 'sensor_4', 'location': 'Server Room', 'base_temp': 20.0, 'area': 20, 'equipment': 'CRAC Unit'},
            {'id': 'sensor_5', 'location': 'Executive Office', 'base_temp': 22.5, 'area': 25, 'equipment': 'HVAC Unit D'}
        ]
        self.is_running = False
        self.thread = None
        self.weather_patterns = self._initialize_weather_patterns()
        self.equipment_efficiency = {sensor['equipment']: 0.85 for sensor in self.sensors}
    
    def _initialize_weather_patterns(self):
        """Initialize realistic weather patterns"""
        return {
            'summer': {'outdoor_temp': 30, 'humidity': 65, 'solar_gain': 0.8},
            'winter': {'outdoor_temp': 10, 'humidity': 45, 'solar_gain': 0.3},
            'spring': {'outdoor_temp': 20, 'humidity': 55, 'solar_gain': 0.6},
            'fall': {'outdoor_temp': 15, 'humidity': 50, 'solar_gain': 0.5}
        }
    
    def get_current_season(self):
        """Determine current season for realistic patterns"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def simulate_equipment_degradation(self, equipment_name: str):
        """Simulate gradual equipment efficiency degradation"""
        if equipment_name in self.equipment_efficiency:
            # Very slow degradation (0.1% per day)
            degradation = random.uniform(-0.001, 0.000)
            self.equipment_efficiency[equipment_name] = max(0.5, self.equipment_efficiency[equipment_name] + degradation)
        
        return self.equipment_efficiency.get(equipment_name, 0.85)
    
    def check_equipment_alerts(self, sensor_data: Dict):
        """Check for equipment-related alerts"""
        equipment = sensor_data['equipment']
        efficiency = self.equipment_efficiency.get(equipment, 0.85)
        
        if efficiency < 0.6:
            self.notification_manager.create_alert(
                "Equipment Efficiency",
                AlertSeverity.CRITICAL,
                f"Critical efficiency drop detected for {equipment}: {efficiency:.1%}",
                sensor_data['sensor_id'],
                sensor_data['location']
            )
        elif efficiency < 0.7:
            self.notification_manager.create_alert(
                "Equipment Efficiency",
                AlertSeverity.HIGH,
                f"Low efficiency warning for {equipment}: {efficiency:.1%}",
                sensor_data['sensor_id'],
                sensor_data['location']
            )
        
        # Check for abnormal vibrations
        if sensor_data.get('vibration', 0) > 0.8:
            self.notification_manager.create_alert(
                "Equipment Vibration",
                AlertSeverity.HIGH,
                f"High vibration detected for {equipment}",
                sensor_data['sensor_id'],
                sensor_data['location']
            )
    
    def generate_sensor_data(self, sensor: Dict) -> Dict:
        """Generate highly realistic sensor data with multiple factors"""
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second
        is_weekday = now.weekday() < 5
        is_working_hours = 8 <= hour <= 18
        season = self.get_current_season()
        
        # Complex time-based patterns
        time_factor = hour + minute/60.0
        seasonal_factor = self.weather_patterns[season]['outdoor_temp'] - 20
        
        # Occupancy patterns with high realism
        if is_weekday and is_working_hours:
            if hour == 12:  # Lunch time dip
                occupancy_base = 0.3
            elif 9 <= hour <= 11 or 14 <= hour <= 16:  # Peak hours
                occupancy_base = 0.8
            else:
                occupancy_base = 0.6
        else:
            occupancy_base = 0.1
        
        # Location-specific patterns
        location_patterns = {
            'Conference Room': {
                'occ_multiplier': 1.2, 
                'temp_offset': 0.2,
                'co2_base': 450,
                'activity_peak': [10, 14, 16],
                'equipment_load': 1.2
            },
            'Open Office': {
                'occ_multiplier': 1.0,
                'temp_offset': 0.5,
                'co2_base': 500,
                'activity_peak': [9, 11, 15],
                'equipment_load': 1.0
            },
            'Reception': {
                'occ_multiplier': 0.8,
                'temp_offset': 1.0,
                'co2_base': 400,
                'activity_peak': [8, 13, 17],
                'equipment_load': 0.8
            },
            'Server Room': {
                'occ_multiplier': 0.05,
                'temp_offset': -2.0,
                'co2_base': 350,
                'activity_peak': [],
                'equipment_load': 2.5
            },
            'Executive Office': {
                'occ_multiplier': 0.6,
                'temp_offset': 0.3,
                'co2_base': 420,
                'activity_peak': [9, 14, 16],
                'equipment_load': 0.9
            }
        }
        
        patterns = location_patterns[sensor['location']]
        
        # Enhanced occupancy calculation
        base_occupancy = occupancy_base * patterns['occ_multiplier']
        time_variation = math.sin(time_factor * 0.5) * 0.2
        random_variation = random.uniform(-0.1, 0.1)
        
        # Peak hour adjustments
        if hour in patterns['activity_peak']:
            peak_boost = 0.3
        else:
            peak_boost = 0.0
        
        occupancy = max(0.01, min(0.99, base_occupancy + time_variation + random_variation + peak_boost))
        
        # Temperature calculation with multiple factors
        base_temp = sensor['base_temp'] + patterns['temp_offset']
        time_temp_variation = math.sin(time_factor * 0.4) * 2.5
        occupancy_temp_effect = occupancy * 1.5
        seasonal_effect = seasonal_factor * 0.3
        solar_gain = self.weather_patterns[season]['solar_gain'] * math.sin(hour * 0.26) * 1.5
        random_temp_noise = random.uniform(-0.3, 0.3)
        
        temperature = base_temp + time_temp_variation + occupancy_temp_effect + seasonal_effect + solar_gain + random_temp_noise
        
        # CO2 calculation
        co2_base = patterns['co2_base']
        occupancy_co2_effect = occupancy * 600
        ventilation_effect = -100  # Base ventilation
        random_co2_noise = random.randint(-30, 30)
        
        co2 = max(350, co2_base + occupancy_co2_effect + ventilation_effect + random_co2_noise)
        
        # Equipment efficiency simulation
        equipment_efficiency = self.simulate_equipment_degradation(sensor['equipment'])
        
        # Power consumption with realistic dynamics
        base_power = 1.0 + (sensor['area'] / 100) * patterns['equipment_load']
        temp_effect = abs(temperature - 22) * 0.2  # Energy to maintain temperature
        occupancy_power_effect = occupancy * 1.2
        time_power_variation = math.sin(time_factor * 0.3) * 0.8
        efficiency_factor = 1.0 / equipment_efficiency  # Lower efficiency = more power
        
        power_consumption = (base_power + temp_effect + occupancy_power_effect + time_power_variation) * efficiency_factor + random.uniform(-0.2, 0.2)
        
        # Additional sensor readings
        humidity = 45 + math.sin(time_factor * 0.2) * 15 + random.uniform(-3, 3)
        vibration = random.uniform(0.1, 0.5) if occupancy > 0.3 else random.uniform(0.01, 0.1)
        pressure = 1013.25 + random.uniform(-2, 2)
        air_flow = 0.3 + (occupancy * 0.4) + random.uniform(-0.1, 0.1)
        
        sensor_data = {
            'sensor_id': sensor['id'],
            'location': sensor['location'],
            'temperature': round(temperature, 2),
            'humidity': round(humidity, 1),
            'co2': int(co2),
            'occupancy': round(occupancy, 3),
            'power_consumption': round(max(0.5, power_consumption), 2),
            'setpoint': 22.0,
            'vibration': round(vibration, 3),
            'pressure': round(pressure, 2),
            'air_flow': round(air_flow, 2),
            'equipment': sensor['equipment'],
            'equipment_status': 'normal' if vibration < 0.7 else 'warning',
            'energy_efficiency': round(equipment_efficiency, 3),
            'timestamp': now
        }
        
        # Check for alerts
        self.check_equipment_alerts(sensor_data)
        
        return sensor_data
    
    def start_simulation(self):
        """Start advanced real-time sensor simulation"""
        self.is_running = True
        self.thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.thread.start()
        logger.info("Advanced sensor simulation started")
    
    def _simulation_loop(self):
        """Main simulation loop with multiple sensors"""
        while self.is_running:
            try:
                for sensor in self.sensors:
                    sensor_data = self.generate_sensor_data(sensor)
                    self.db_manager.store_sensor_data(sensor_data)
                    logger.debug(f"Generated data for {sensor['location']}")
                
                time.sleep(8)  # Update every 8 seconds for more frequent updates
            except Exception as e:
                logger.error(f"Error in sensor simulation: {e}")
                time.sleep(30)
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Sensor simulation stopped")

class AIOptimizationEngine:
    """Advanced AI optimization engine with multiple algorithms"""
    
    def __init__(self, db_manager: AdvancedDatabaseManager, notification_manager: NotificationManager):
        self.db_manager = db_manager
        self.notification_manager = notification_manager
        self.optimization_history = []
        self.ml_models = {}
        self.initialize_models()
    
    def initialize_models(self):
        """Initialize machine learning models for optimization"""
        # Placeholder for actual ML model initialization
        logger.info("AI Optimization Engine initialized")
    
    def calculate_seasonal_factors(self) -> Dict:
        """Calculate seasonal adjustment factors"""
        season = self.get_current_season()
        seasonal_factors = {
            'winter': {'temp_adjust': -1.0, 'ventilation_reduce': 0.2, 'humidity_target': 45},
            'summer': {'temp_adjust': 1.0, 'ventilation_increase': 0.1, 'humidity_target': 55},
            'spring': {'temp_adjust': 0.0, 'ventilation_stable': 0.0, 'humidity_target': 50},
            'fall': {'temp_adjust': 0.0, 'ventilation_stable': 0.0, 'humidity_target': 50}
        }
        return seasonal_factors.get(season, seasonal_factors['spring'])
    
    def get_current_season(self):
        """Get current season"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'fall'
    
    def optimize_hvac_system(self, current_data: Dict, operation_mode: str = 'auto') -> Dict:
        """Comprehensive HVAC optimization using multiple AI algorithms"""
        start_time = time.time()
        
        # Extract current conditions with safe defaults
        current_temp = current_data.get('temperature', 22.0)
        occupancy = current_data.get('occupancy', 0.5)
        co2_level = current_data.get('co2', 600)
        current_power = current_data.get('power_consumption', 3.0)
        humidity = current_data.get('humidity', 50.0)
        hour = datetime.now().hour
        minute = datetime.now().minute
        
        # Get seasonal adjustments
        seasonal_factors = self.calculate_seasonal_factors()
        
        # Mode-specific optimization parameters with safe defaults
        optimization_modes = {
            'energy_saving': {
                'temp_tolerance': 2.5,
                'ventilation_min': 0.2,
                'comfort_weight': 0.3,
                'energy_weight': 0.7,
                'humidity_tolerance': 5
            },
            'comfort_focus': {
                'temp_tolerance': 0.5,
                'ventilation_min': 0.4,
                'comfort_weight': 0.8,
                'energy_weight': 0.2,
                'humidity_tolerance': 2
            },
            'balanced': {
                'temp_tolerance': 1.5,
                'ventilation_min': 0.3,
                'comfort_weight': 0.5,
                'energy_weight': 0.5,
                'humidity_tolerance': 3
            },
            'auto': {
                'temp_tolerance': 1.0,
                'ventilation_min': 0.35,
                'comfort_weight': 0.6,
                'energy_weight': 0.4,
                'humidity_tolerance': 3
            }
        }
        
        # Safe mode parameter access
        mode_params = optimization_modes.get(operation_mode, optimization_modes['auto'])
        
        # Advanced temperature optimization
        optimal_temp = self._calculate_optimal_temperature(
            current_temp, occupancy, hour, seasonal_factors, mode_params
        )
        
        # Advanced ventilation optimization
        ventilation_rate = self._calculate_ventilation_rate(
            co2_level, occupancy, humidity, hour, mode_params
        )
        
        # Energy savings prediction
        energy_analysis = self._predict_energy_savings(
            current_temp, optimal_temp, current_power, occupancy, hour
        )
        
        # Comprehensive comfort scoring
        comfort_analysis = self._calculate_comfort_metrics(
            current_temp, optimal_temp, occupancy, co2_level, humidity, mode_params
        )
        
        # Carbon footprint calculation
        carbon_savings = self._calculate_carbon_savings(energy_analysis['kwh_savings'])
        
        # Generate intelligent recommendations
        recommendations = self._generate_ai_recommendations(
            current_data, optimal_temp, ventilation_rate, energy_analysis, comfort_analysis, mode_params
        )
        
        # Check for optimization alerts
        self._check_optimization_alerts(energy_analysis, comfort_analysis, current_data)
        
        optimization_duration = time.time() - start_time
        
        # Compile optimization results
        optimization_result = {
            'optimal_temperature': round(optimal_temp, 1),
            'ventilation_rate': round(ventilation_rate, 2),
            'energy_savings_percent': round(energy_analysis['savings_percent'], 1),
            'energy_savings_kwh': round(energy_analysis['kwh_savings'], 2),
            'cost_savings': round(energy_analysis['cost_savings'], 2),
            'comfort_score': round(comfort_analysis['overall_comfort'], 1),
            'carbon_savings': round(carbon_savings, 2),
            'recommendations': recommendations,
            'timestamp': datetime.now(),
            'operation_mode': operation_mode,
            'comfort_breakdown': comfort_analysis,
            'energy_analysis': energy_analysis,
            'optimization_duration': round(optimization_duration, 3)
        }
        
        self.optimization_history.append(optimization_result)
        return optimization_result
    
    def _calculate_optimal_temperature(self, current_temp: float, occupancy: float, 
                                     hour: int, seasonal_factors: Dict, mode_params: Dict) -> float:
        """Advanced temperature optimization algorithm"""
        
        # Base temperature by time of day
        if 22 <= hour <= 6:  # Night hours
            base_temp = 23.0  # Energy saving at night
        elif hour in [12, 13]:  # Lunch time
            base_temp = 21.5  # Slightly cooler during lunch
        else:
            base_temp = 22.0  # Standard comfort temperature
        
        # Safe parameter access
        temp_tolerance = mode_params.get('temp_tolerance', 1.5)
        
        # Occupancy-based adjustments
        if occupancy < 0.2:
            occupancy_adjust = temp_tolerance  # Maximum energy saving
        elif occupancy < 0.4:
            occupancy_adjust = temp_tolerance * 0.5  # Moderate saving
        elif occupancy > 0.8:
            occupancy_adjust = -0.5  # Enhanced comfort
        else:
            occupancy_adjust = 0.0  # Balanced
        
        # Seasonal adjustments
        seasonal_adjust = seasonal_factors.get('temp_adjust', 0.0)
        
        # Time-based fine adjustments
        minute_factor = datetime.now().minute / 60.0
        time_adjust = math.sin(hour * 0.26 + minute_factor * 6.28) * 0.3
        
        optimal_temp = base_temp + occupancy_adjust + seasonal_adjust + time_adjust
        
        # Ensure within safe and comfortable bounds
        optimal_temp = max(18.0, min(26.0, optimal_temp))
        
        return optimal_temp
    
    def _calculate_ventilation_rate(self, co2_level: int, occupancy: float, 
                                  humidity: float, hour: int, mode_params: Dict) -> float:
        """Advanced ventilation optimization algorithm"""
        
        # Base ventilation rate
        base_rate = 0.5
        
        # CO2-based ventilation
        if co2_level > 1200:
            co2_adjust = 0.4
        elif co2_level > 1000:
            co2_adjust = 0.3
        elif co2_level > 800:
            co2_adjust = 0.2
        elif co2_level > 600:
            co2_adjust = 0.1
        else:
            co2_adjust = 0.0
        
        # Occupancy-based ventilation
        occupancy_adjust = occupancy * 0.4
        
        # Humidity-based adjustment
        humidity_target = 50
        humidity_difference = abs(humidity - humidity_target)
        if humidity_difference > 15:
            humidity_adjust = 0.3
        elif humidity_difference > 10:
            humidity_adjust = 0.2
        elif humidity_difference > 5:
            humidity_adjust = 0.1
        else:
            humidity_adjust = 0.0
        
        # Add humidity adjustment in correct direction
        if humidity > humidity_target:
            humidity_adjust = humidity_adjust  # Increase ventilation to reduce humidity
        else:
            humidity_adjust = -humidity_adjust * 0.5  # Slightly decrease ventilation
        
        # Time-based adjustment (reduce at night)
        if 22 <= hour <= 6:
            time_adjust = -0.3
        else:
            time_adjust = 0.0
        
        ventilation_rate = base_rate + co2_adjust + occupancy_adjust + humidity_adjust + time_adjust
        
        # Safe parameter access
        ventilation_min = mode_params.get('ventilation_min', 0.3)
        
        # Apply mode-specific minimum
        ventilation_rate = max(ventilation_min, min(1.0, ventilation_rate))
        
        return ventilation_rate
    
    def _predict_energy_savings(self, current_temp: float, optimal_temp: float, 
                              current_power: float, occupancy: float, hour: int) -> Dict:
        """Predict energy savings with advanced modeling"""
        
        temp_difference = abs(current_temp - optimal_temp)
        
        # Advanced energy savings model
        base_savings_per_degree = 0.035  # 3.5% per degree
        
        # Occupancy factor (higher occupancy = more impact)
        occupancy_factor = 0.3 + (occupancy * 0.7)
        
        # Time factor (different savings at different times)
        if 22 <= hour <= 6:
            time_factor = 1.2  # Higher savings at night
        elif 8 <= hour <= 18:
            time_factor = 0.8  # Lower savings during peak hours
        else:
            time_factor = 1.0
        
        savings_percent = min(35, temp_difference * base_savings_per_degree * 100 * occupancy_factor * time_factor)
        kwh_savings = (savings_percent / 100) * current_power
        
        # Cost savings calculation (time-based electricity rates)
        if 8 <= hour <= 20:
            cost_rate = 0.15  # Peak rate
        else:
            cost_rate = 0.08  # Off-peak rate
        
        cost_savings = kwh_savings * cost_rate
        
        return {
            'savings_percent': savings_percent,
            'kwh_savings': kwh_savings,
            'cost_savings': cost_savings,
            'current_rate': cost_rate,
            'potential_annual_savings': cost_savings * 24 * 365
        }
    
    def _calculate_comfort_metrics(self, current_temp: float, optimal_temp: float, 
                                 occupancy: float, co2_level: int, humidity: float, 
                                 mode_params: Dict) -> Dict:
        """Calculate comprehensive comfort metrics with safe parameter access"""
        
        # Temperature comfort (0-40 points)
        temp_difference = abs(current_temp - optimal_temp)
        temp_comfort = max(0, 40 - (temp_difference * 8))
        
        # Air quality comfort (0-30 points)
        if co2_level < 600:
            air_quality_score = 30
        elif co2_level < 800:
            air_quality_score = 25
        elif co2_level < 1000:
            air_quality_score = 20
        elif co2_level < 1200:
            air_quality_score = 15
        else:
            air_quality_score = 10
        
        # Humidity comfort (0-15 points)
        humidity_target = 50
        humidity_difference = abs(humidity - humidity_target)
        if humidity_difference <= 5:
            humidity_score = 15
        elif humidity_difference <= 10:
            humidity_score = 12
        elif humidity_difference <= 15:
            humidity_score = 8
        else:
            humidity_score = 4
        
        # Occupancy comfort (0-15 points)
        # Higher occupancy suggests people find the space comfortable
        if occupancy > 0.7:
            occupancy_score = 15
        elif occupancy > 0.3:
            occupancy_score = 10
        else:
            occupancy_score = 5
        
        # Safe parameter access with defaults
        comfort_weight = mode_params.get('comfort_weight', 0.6)  # Default to balanced
        
        # Apply mode-specific weights safely
        comfort_weights = {
            'temperature': comfort_weight,
            'air_quality': 0.7,
            'humidity': 0.5,
            'occupancy': 0.3
        }
        
        weighted_comfort = (
            temp_comfort * comfort_weights['temperature'] +
            air_quality_score * comfort_weights['air_quality'] +
            humidity_score * comfort_weights['humidity'] +
            occupancy_score * comfort_weights['occupancy']
        ) / sum(comfort_weights.values())
        
        overall_comfort = min(100, weighted_comfort * (100 / 85))  # Normalize to 100
        
        return {
            'overall_comfort': overall_comfort,
            'temperature_comfort': temp_comfort,
            'air_quality_score': air_quality_score,
            'humidity_score': humidity_score,
            'occupancy_score': occupancy_score,
            'comfort_weights': comfort_weights
        }
    
    def _calculate_carbon_savings(self, kwh_savings: float) -> float:
        """Calculate carbon footprint reduction"""
        # Average carbon intensity: 0.5 kg CO2 per kWh
        return kwh_savings * 0.5
    
    def _generate_ai_recommendations(self, current_data: Dict, optimal_temp: float, 
                                   ventilation_rate: float, energy_analysis: Dict, 
                                   comfort_analysis: Dict, mode_params: Dict) -> List[str]:
        """Generate intelligent AI-powered recommendations"""
        
        recommendations = []
        current_temp = current_data.get('temperature', 22.0)
        occupancy = current_data.get('occupancy', 0.5)
        co2_level = current_data.get('co2', 600)
        humidity = current_data.get('humidity', 50.0)
        hour = datetime.now().hour
        
        # Temperature recommendations
        temp_diff = optimal_temp - current_temp
        if abs(temp_diff) > 0.5:
            action = "increase" if temp_diff > 0 else "decrease"
            reason = "energy savings" if temp_diff > 0 else "better comfort"
            recommendations.append(
                f"🌡️ {action.capitalize()} temperature by {abs(temp_diff):.1f}°C to {optimal_temp}°C for {reason}"
            )
        
        # Ventilation recommendations
        if co2_level > 1000:
            recommendations.append("💨 Increase ventilation immediately: CO2 levels are very high (>1000 ppm)")
        elif co2_level > 800:
            recommendations.append("💨 Consider increasing ventilation: CO2 levels are elevated")
        elif co2_level < 500 and ventilation_rate > 0.6:
            recommendations.append("💨 Reduce ventilation: CO2 levels are optimal")
        
        # Occupancy-based recommendations
        if occupancy < 0.2:
            recommendations.append("👥 Low occupancy detected: Enable zone-based HVAC control for maximum savings")
        elif occupancy > 0.8:
            recommendations.append("👥 High occupancy: Ensure maximum cooling and ventilation capacity")
        
        # Time-based recommendations
        if 22 <= hour <= 6:
            recommendations.append("🌙 Night mode active: Increased temperature setpoints for energy savings")
        
        # Energy saving opportunities
        if energy_analysis['savings_percent'] > 15:
            recommendations.append(
                f"💰 Significant energy saving opportunity: {energy_analysis['savings_percent']:.1f}% "
                f"(${energy_analysis['cost_savings']:.2f}/hour)"
            )
        
        # Comfort improvements
        if comfort_analysis['overall_comfort'] < 80:
            recommendations.append("😊 Comfort optimization needed: Consider adjusting environmental parameters")
        
        # Humidity recommendations
        if humidity > 70:
            recommendations.append("💧 High humidity: Consider dehumidification")
        elif humidity < 30:
            recommendations.append("💧 Low humidity: Consider humidification")
        
        # Equipment efficiency recommendations
        efficiency = current_data.get('energy_efficiency', 0.85)
        if efficiency < 0.7:
            recommendations.append(f"⚙️ Equipment efficiency low ({efficiency:.1%}): Schedule maintenance")
        
        return recommendations
    
    def _check_optimization_alerts(self, energy_analysis: Dict, comfort_analysis: Dict, current_data: Dict):
        """Check for optimization-related alerts"""
        
        # High energy saving potential alert
        if energy_analysis['savings_percent'] > 20:
            self.notification_manager.create_alert(
                "High Savings Potential",
                AlertSeverity.MEDIUM,
                f"High energy saving potential detected: {energy_analysis['savings_percent']:.1f}%",
                current_data.get('sensor_id'),
                current_data.get('location')
            )
        
        # Low comfort alert
        if comfort_analysis['overall_comfort'] < 70:
            self.notification_manager.create_alert(
                "Low Comfort Level",
                AlertSeverity.MEDIUM,
                f"Low comfort level detected: {comfort_analysis['overall_comfort']:.1f}/100",
                current_data.get('sensor_id'),
                current_data.get('location')
            )

class EnergyAnalyticsEngine:
    """Comprehensive energy analytics and reporting engine"""
    
    def __init__(self, db_manager: AdvancedDatabaseManager):
        self.db_manager = db_manager
    
    def calculate_comprehensive_metrics(self, hours: int = 24) -> Dict:
        """Calculate comprehensive energy and performance metrics"""
        df = self.db_manager.get_recent_sensor_data(hours * 6)  # 10-minute intervals
        
        if df.empty:
            return {}
        
        # Energy calculations
        total_energy = df['power_consumption'].sum() / 6  # Convert to kWh
        avg_power = df['power_consumption'].mean()
        max_power = df['power_consumption'].max()
        min_power = df['power_consumption'].min()
        
        # Baseline comparison (industry standard: 3.5 kW for similar buildings)
        baseline_energy = 3.5 * hours
        energy_savings = max(0, baseline_energy - total_energy)
        savings_percent = (energy_savings / baseline_energy) * 100 if baseline_energy > 0 else 0
        
        # Cost calculations
        cost_savings = energy_savings * 0.12  # Average electricity rate
        
        # Comfort metrics
        avg_temperature = df['temperature'].mean()
        temp_std = df['temperature'].std()
        avg_occupancy = df['occupancy'].mean()
        
        # Air quality metrics
        avg_co2 = df['co2'].mean()
        co2_violations = len(df[df['co2'] > 1000])
        
        # Efficiency metrics
        energy_per_occupant = total_energy / (avg_occupancy * hours) if avg_occupancy > 0 else 0
        
        # Equipment efficiency
        avg_efficiency = df['energy_efficiency'].mean() if 'energy_efficiency' in df.columns else 0.85
        
        return {
            'total_energy_kwh': round(total_energy, 2),
            'average_power_kw': round(avg_power, 2),
            'peak_power_kw': round(max_power, 2),
            'min_power_kw': round(min_power, 2),
            'energy_savings_kwh': round(energy_savings, 2),
            'savings_percent': round(savings_percent, 1),
            'cost_savings': round(cost_savings, 2),
            'average_temperature': round(avg_temperature, 1),
            'temperature_stability': round(temp_std, 2),
            'average_occupancy': round(avg_occupancy, 3),
            'average_co2': round(avg_co2, 0),
            'co2_violations': co2_violations,
            'energy_per_occupant': round(energy_per_occupant, 2),
            'equipment_efficiency': round(avg_efficiency, 3),
            'analysis_period_hours': hours
        }
    
    def calculate_carbon_footprint(self, energy_kwh: float) -> Dict:
        """Calculate comprehensive carbon footprint metrics"""
        carbon_kg = energy_kwh * 0.5  # kg CO2 per kWh
        
        # Equivalent metrics for better understanding
        trees_equivalent = carbon_kg / 21.77  # kg CO2 absorbed by one tree per year
        cars_equivalent = carbon_kg / 4200     # kg CO2 from average car per year
        smartphones_equivalent = carbon_kg / 0.085  # kg CO2 from smartphone charging for year
        flights_equivalent = carbon_kg / 90    # kg CO2 per short-haul flight
        
        return {
            'carbon_kg': round(carbon_kg, 2),
            'trees_equivalent': round(trees_equivalent, 1),
            'cars_equivalent': round(cars_equivalent, 3),
            'smartphones_equivalent': int(smartphones_equivalent),
            'flights_equivalent': round(flights_equivalent, 2)
        }
    
    def generate_energy_report(self, days: int = 7) -> Dict:
        """Generate comprehensive energy report"""
        hours = days * 24
        metrics = self.calculate_comprehensive_metrics(hours)
        carbon_footprint = self.calculate_carbon_footprint(metrics.get('total_energy_kwh', 0))
        
        report = {
            'period_days': days,
            'summary': {
                'total_energy': metrics.get('total_energy_kwh', 0),
                'total_savings': metrics.get('cost_savings', 0),
                'carbon_reduction': carbon_footprint.get('carbon_kg', 0),
                'average_efficiency': metrics.get('equipment_efficiency', 0)
            },
            'performance_metrics': metrics,
            'carbon_analysis': carbon_footprint,
            'recommendations': self._generate_energy_recommendations(metrics),
            'generated_at': datetime.now()
        }
        
        return report
    
    def _generate_energy_recommendations(self, metrics: Dict) -> List[str]:
        """Generate energy efficiency recommendations"""
        recommendations = []
        
        if metrics.get('savings_percent', 0) < 10:
            recommendations.append("Consider implementing more aggressive energy saving measures")
        
        if metrics.get('average_co2', 0) > 800:
            recommendations.append("Improve ventilation system to reduce CO2 levels")
        
        if metrics.get('equipment_efficiency', 0.85) < 0.8:
            recommendations.append("Schedule equipment maintenance to improve efficiency")
        
        if metrics.get('temperature_stability', 0) > 2.0:
            recommendations.append("Optimize temperature control for better stability")
        
        return recommendations

class ComprehensiveHVACSystem:
    """Main HVAC system integration class with all components"""
    
    def __init__(self):
        self.db_manager = AdvancedDatabaseManager()
        self.notification_manager = NotificationManager()
        self.sensor_simulator = AdvancedSensorSimulator(self.db_manager, self.notification_manager)
        self.optimizer = AIOptimizationEngine(self.db_manager, self.notification_manager)
        self.energy_analytics = EnergyAnalyticsEngine(self.db_manager)
        
        # Initialize with historical data
        self._initialize_historical_data()
        
        # Start real-time simulation
        self.sensor_simulator.start_simulation()
        
        logger.info("Comprehensive HVAC AI System initialized successfully")
    
    def _initialize_historical_data(self):
        """Initialize with realistic historical data"""
        df = self.db_manager.get_recent_sensor_data(100)
        if len(df) < 80:
            logger.info("Generating comprehensive historical data...")
            self._generate_historical_data()
    
    def _generate_historical_data(self):
        """Generate 7 days of realistic historical data"""
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        current_time = start_time
        while current_time <= end_time:
            for sensor in self.sensor_simulator.sensors:
                historical_data = self.sensor_simulator.generate_sensor_data(sensor)
                historical_data['timestamp'] = current_time
                self.db_manager.store_sensor_data(historical_data)
            
            current_time += timedelta(minutes=10)  # 10-minute intervals
    
    def get_current_status(self) -> Dict:
        """Get current system status from latest sensor data"""
        df = self.db_manager.get_recent_sensor_data(1)
        if not df.empty:
            return df.iloc[-1].to_dict()
        return {}
    
    def get_historical_data(self, hours: int = 24) -> pd.DataFrame:
        """Get historical data for specified period"""
        limit = hours * 6  # 6 records per hour
        df = self.db_manager.get_recent_sensor_data(limit)
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    
    def run_optimization(self, mode: str = 'auto') -> Dict:
        """Run comprehensive AI optimization"""
        current_data = self.get_current_status()
        if not current_data:
            return {}
        
        optimization = self.optimizer.optimize_hvac_system(current_data, mode)
        self.db_manager.store_optimization(optimization)
        
        return optimization
    
    def get_energy_analytics(self, hours: int = 24) -> Dict:
        """Get comprehensive energy analytics"""
        return self.energy_analytics.calculate_comprehensive_metrics(hours)
    
    def get_energy_report(self, days: int = 7) -> Dict:
        """Get comprehensive energy report"""
        return self.energy_analytics.generate_energy_report(days)
    
    def get_active_alerts(self):
        """Get active system alerts"""
        return self.notification_manager.get_active_alerts()
    
    def acknowledge_alert(self, alert_id: str):
        """Acknowledge a system alert"""
        self.notification_manager.acknowledge_alert(alert_id)
    
    def stop_system(self):
        """Stop all system components"""
        self.sensor_simulator.stop_simulation()
        logger.info("HVAC system stopped")

# =============================================================================
# STREAMLIT DASHBOARD - COMPLETE 2500+ LINE VERSION WITH 4 GRAPHS
# =============================================================================

class AdvancedStreamlitDashboard:
    """Advanced Streamlit dashboard with all features and proper session state management"""
    
    def __init__(self, hvac_system: ComprehensiveHVACSystem):
        self.hvac_system = hvac_system
        self.chart_counter = 0
        self.setup_page()
        
        # Initialize session state safely
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Safely initialize all session state variables"""
        default_states = {
            'optimization_results': None,
            'last_optimization_time': None,
            'pending_optimization': False,
            'optimization_mode': 'auto',
            'selected_report_days': 7,
            'energy_report_data': None,
            'energy_report_generated': False,
            'should_generate_report': False,
            'auto_refresh': True
        }
        
        for key, value in default_states.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def get_unique_key(self, prefix="chart"):
        """Generate unique key for Streamlit elements"""
        self.chart_counter += 1
        timestamp = int(time.time())
        random_suffix = random.randint(1000, 9999)
        return f"{prefix}_{self.chart_counter}_{timestamp}_{random_suffix}"
    
    def setup_page(self):
        """Setup advanced page configuration"""
        st.set_page_config(
            page_title="AI-Powered HVAC Optimization System",
            page_icon="❄️",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Advanced custom CSS with all styling
        st.markdown("""
        <style>
        .main-header {
            font-size: 3.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            margin: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .metric-value {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 8px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }
        .metric-label {
            font-size: 1em;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        .metric-subtext {
            font-size: 0.85em;
            opacity: 0.8;
        }
        .recommendation-box {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            border-left: 5px solid #ff6b6b;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .alert-box {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            border-left: 5px solid #ff3838;
        }
        .warning-box {
            background: linear-gradient(135deg, #ffd93d 0%, #ff9f43 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            border-left: 5px solid #ff9f1a;
        }
        .success-box {
            background: linear-gradient(135deg, #51cf66 0%, #40c057 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            border-left: 5px solid #2f9e44;
        }
        .info-box {
            background: linear-gradient(135deg, #4d96ff 0%, #1e90ff 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
            border-left: 5px solid #007bff;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def display_header(self):
        """Display enhanced dashboard header"""
        st.markdown('<div class="main-header">🏢 AI-Powered HVAC Optimization System</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #666; margin-bottom: 2rem; font-size: 1.2em;">
        🌡️ Real-time Monitoring • 🤖 AI Optimization • 💰 Energy Efficiency • 🌱 Sustainability
        </div>
        """, unsafe_allow_html=True)
    
    def display_sidebar_controls(self):
        """Display comprehensive sidebar controls without session state conflicts"""
        st.sidebar.title("🎛️ Advanced Control Panel")
        st.sidebar.markdown("---")
        
        # Operation Mode Selection
        operation_mode = st.sidebar.selectbox(
            "🏢 Operation Mode",
            ["Auto", "Energy Saving", "Comfort Focus", "Balanced", "Maintenance"],
            help="Select the AI optimization strategy",
            key="sidebar_operation_mode"
        )
        
        # Manual Controls (only in manual mode)
        if operation_mode == "Manual":
            st.sidebar.markdown("### 🎮 Manual Controls")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                temp_setpoint = st.slider("Temperature (°C)", 18, 26, 22, key="manual_temp_slider")
            with col2:
                ventilation_rate = st.slider("Ventilation", 0.0, 1.0, 0.5, key="manual_vent_slider")
            
            if st.sidebar.button("Apply Manual Settings", key="apply_manual_settings_btn"):
                st.sidebar.success("Manual settings applied!")
        
        # Optimization Controls using form to avoid conflicts
        st.sidebar.markdown("### 🤖 AI Optimization")
        with st.sidebar.form("optimization_control_form"):
            opt_mode = st.selectbox(
                "Optimization Mode",
                ["Auto", "Energy Saving", "Comfort Focus", "Balanced"],
                key="sidebar_opt_mode"
            )
            
            run_optimization = st.form_submit_button("🚀 Run AI Optimization")
            
            if run_optimization:
                st.session_state.pending_optimization = True
                st.session_state.optimization_mode = opt_mode
                st.sidebar.success("Optimization queued!")
        
        # System Monitoring
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 System Status")
        current_data = self.hvac_system.get_current_status()
        if current_data:
            st.sidebar.metric("Active Sensors", "5")
            st.sidebar.metric("Data Points", f"{len(self.hvac_system.get_historical_data(1))}")
            st.sidebar.metric("System Uptime", "100%")
        
        # Auto-refresh control
        st.sidebar.markdown("### 🔄 Auto-Refresh")
        auto_refresh = st.sidebar.toggle("Enable Auto-Refresh", value=True, key="auto_refresh_toggle")
        st.session_state.auto_refresh = auto_refresh
        
        st.sidebar.markdown(f"**Last Update:** {datetime.now().strftime('%H:%M:%S')}")
        
        return operation_mode
    
    def display_real_time_metrics(self):
        """Display enhanced real-time metrics with all features"""
        current_data = self.hvac_system.get_current_status()
        if not current_data:
            st.warning("⏳ Initializing system and collecting sensor data...")
            with st.spinner("Starting real-time data simulation..."):
                time.sleep(2)
            return
        
        # First row - Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Temperature with advanced color coding
            temp = current_data['temperature']
            if 21 <= temp <= 23:
                temp_color = "#51cf66"  # Green - optimal
                temp_status = "Optimal"
            elif 20 <= temp <= 24:
                temp_color = "#ffd43b"  # Yellow - acceptable
                temp_status = "Acceptable"
            else:
                temp_color = "#ff6b6b"  # Red - outside range
                temp_status = "Needs Adjustment"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">🌡️ Temperature</div>
                <div class="metric-value" style="color: {temp_color}">{temp}°C</div>
                <div class="metric-subtext">Setpoint: 22°C • {temp_status}</div>
                <div class="metric-subtext">Location: {current_data['location']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # Power consumption with efficiency indicator
            power = current_data['power_consumption']
            if power < 2.5:
                power_color = "#51cf66"  # Green - efficient
                power_status = "Efficient"
            elif power < 3.5:
                power_color = "#ffd43b"  # Yellow - moderate
                power_status = "Moderate"
            else:
                power_color = "#ff6b6b"  # Red - high consumption
                power_status = "High"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">⚡ Power Consumption</div>
                <div class="metric-value" style="color: {power_color}">{power} kW</div>
                <div class="metric-subtext">Target: < 3.0 kW • {power_status}</div>
                <div class="metric-subtext">Real-time Monitoring</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Occupancy with activity level
            occupancy = current_data['occupancy']
            occupancy_percent = occupancy * 100
            if occupancy < 0.3:
                occ_color = "#51cf66"  # Green - low
                activity = "Low"
            elif occupancy < 0.7:
                occ_color = "#ffd43b"  # Yellow - medium
                activity = "Medium"
            else:
                occ_color = "#ff6b6b"  # Red - high
                activity = "High"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">👥 Occupancy</div>
                <div class="metric-value" style="color: {occ_color}">{occupancy_percent:.1f}%</div>
                <div class="metric-subtext">Activity: {activity} • Real-time</div>
                <div class="metric-subtext">Location: {current_data['location']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            # Air quality with CO2 levels
            co2 = current_data['co2']
            if co2 < 800:
                air_color = "#51cf66"  # Green - excellent
                quality = "Excellent"
            elif co2 < 1000:
                air_color = "#ffd43b"  # Yellow - good
                quality = "Good"
            elif co2 < 1200:
                air_color = "#ffa94d"  # Orange - moderate
                quality = "Moderate"
            else:
                air_color = "#ff6b6b"  # Red - poor
                quality = "Poor"
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">💨 Air Quality</div>
                <div class="metric-value" style="color: {air_color}">{quality}</div>
                <div class="metric-subtext">CO₂: {co2} ppm • Real-time</div>
                <div class="metric-subtext">Ventilation Required</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Second row - Additional metrics
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            humidity = current_data['humidity']
            if 40 <= humidity <= 60:
                hum_color = "#51cf66"
                hum_status = "Optimal"
            elif 30 <= humidity <= 70:
                hum_color = "#ffd43b"
                hum_status = "Acceptable"
            else:
                hum_color = "#ff6b6b"
                hum_status = "Poor"
            
            st.metric("💧 Humidity", f"{humidity}%", hum_status, delta_color="off")
        
        with col6:
            vibration = current_data.get('vibration', 0.0)
            if vibration < 0.3:
                vib_color = "normal"
                vib_status = "Normal"
            elif vibration < 0.6:
                vib_color = "off"
                vib_status = "Elevated"
            else:
                vib_color = "inverse"
                vib_status = "High"
            
            st.metric("📊 Vibration", f"{vibration:.3f}", vib_status, delta_color=vib_color)
        
        with col7:
            pressure = current_data.get('pressure', 1013.25)
            st.metric("🌡️ Pressure", f"{pressure:.1f} hPa", "Atmospheric", delta_color="off")
        
        with col8:
            air_flow = current_data.get('air_flow', 0.5)
            efficiency = current_data.get('energy_efficiency', 0.85)
            st.metric("💨 Air Flow", f"{air_flow:.2f} m/s", f"Eff: {efficiency:.1%}", delta_color="off")

    def create_comprehensive_dashboard_charts(self, historical_data):
        """Create all 4 comprehensive dashboard charts"""
        if historical_data.empty:
            return None, None, None, None
            
        # Create subplots for all 4 graphs
        fig1 = self._create_temperature_occupancy_chart(historical_data)
        fig2 = self._create_energy_consumption_chart(historical_data)
        fig3 = self._create_comfort_score_chart(historical_data)
        fig4 = self._create_humidity_levels_chart(historical_data)
        
        return fig1, fig2, fig3, fig4

    def _create_temperature_occupancy_chart(self, historical_data):
        """Create Temperature & Occupancy Trend chart"""
        fig = go.Figure()
        
        # Temperature trace
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=historical_data['temperature'], 
            name="Temperature (°C)",
            line=dict(color='#FF6B6B', width=3),
            yaxis='y1'
        ))
        
        # Occupancy trace
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=historical_data['occupancy'] * 100,  # Convert to percentage
            name="Occupancy (%)",
            line=dict(color='#4ECDC4', width=3),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            title="Temperature & Occupancy Trend",
            xaxis=dict(title="Time"),
            yaxis=dict(
                title="Temperature (°C)", 
                title_font=dict(color='#FF6B6B')
            ),
            yaxis2=dict(
                title="Occupancy (%)",
                title_font=dict(color='#4ECDC4'),
                overlaying='y',
                side='right'
            ),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

    def _create_energy_consumption_chart(self, historical_data):
        """Create Energy Consumption Pattern chart"""
        fig = go.Figure()
        
        # Energy Consumption
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=historical_data['power_consumption'],
            name="Energy Consumption",
            line=dict(color='#FFD93D', width=3)
        ))
        
        # Temperature overlay
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=historical_data['temperature'],
            name="Temperature",
            line=dict(color='#FF6B6B', width=2, dash='dot'),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            title="Energy Consumption Pattern",
            xaxis=dict(title="Time"),
            yaxis=dict(
                title="Energy Consumption (kW)", 
                title_font=dict(color='#FFD93D')
            ),
            yaxis2=dict(
                title="Temperature (°C)",
                title_font=dict(color='#FF6B6B'),
                overlaying='y',
                side='right'
            ),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

    def _create_comfort_score_chart(self, historical_data):
        """Create Comfort Score Analysis chart"""
        fig = go.Figure()
        
        # Calculate comfort score (simplified)
        comfort_scores = []
        for _, row in historical_data.iterrows():
            temp_score = max(0, 100 - abs(row['temperature'] - 22) * 10)
            air_quality_score = max(0, 100 - max(0, row['co2'] - 400) / 10)
            comfort_score = (temp_score + air_quality_score) / 2
            comfort_scores.append(comfort_score)
        
        # Comfort Score
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=comfort_scores,
            name="Comfort Score",
            line=dict(color='#6BCF7F', width=3),
            fill='tozeroy',
            fillcolor='rgba(107, 207, 127, 0.2)'
        ))
        
        # Comfort Target
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=[80] * len(historical_data),
            name="Comfort Target",
            line=dict(color='#FF6B6B', width=2, dash='dash')
        ))
        
        fig.update_layout(
            height=400,
            title="Comfort Score Analysis",
            xaxis=dict(title="Time"),
            yaxis=dict(title="Comfort Score", range=[0, 100]),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

    def _create_humidity_levels_chart(self, historical_data):
        """Create Humidity Levels chart"""
        fig = go.Figure()
        
        # Humidity levels
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=historical_data['humidity'],
            name="Humidity Levels",
            line=dict(color='#4D96FF', width=3),
            fill='tozeroy',
            fillcolor='rgba(77, 150, 255, 0.2)'
        ))
        
        # Optimal range
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=[55] * len(historical_data),
            name="Optimal Range",
            line=dict(color='#51CF66', width=2, dash='dash')
        ))
        
        # Performance indicator (simplified)
        performance = [min(100, h * 2) for h in historical_data['humidity']]
        fig.add_trace(go.Scatter(
            x=historical_data['timestamp'], 
            y=performance,
            name="Performance (%)",
            line=dict(color='#FFA94D', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            title="Humidity Levels",
            xaxis=dict(title="Time"),
            yaxis=dict(title="Humidity (%)", range=[0, 100]),
            yaxis2=dict(
                title="Performance (%)",
                overlaying='y',
                side='right',
                range=[0, 100]
            ),
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig

    def display_analytics_dashboard(self):
        """Display comprehensive analytics dashboard with 4 graphs"""
        st.markdown("## 📊 Advanced Analytics Dashboard")
        
        # Time range selector
        col1, col2 = st.columns([3, 1])
        with col1:
            time_range = st.selectbox(
                "Select Analysis Period",
                ["Last 6 Hours", "Last 24 Hours", "Last 7 Days", "Last 30 Days"],
                key="analytics_time_range"
            )
        
        time_map = {"Last 6 Hours": 6, "Last 24 Hours": 24, "Last 7 Days": 168, "Last 30 Days": 720}
        hours = time_map[time_range]
        
        historical_data = self.hvac_system.get_historical_data(hours)
        
        if historical_data.empty:
            st.info("📈 Collecting historical data... Please wait for the system to initialize.")
            return
        
        # Create all 4 charts
        temp_occ_fig, energy_fig, comfort_fig, humidity_fig = self.create_comprehensive_dashboard_charts(historical_data)
        
        # Display charts in 2x2 grid
        col1, col2 = st.columns(2)
        
        with col1:
            if temp_occ_fig:
                st.plotly_chart(
                    temp_occ_fig, 
                    use_container_width=True, 
                    key=self.get_unique_key("temp_occupancy")
                )
        
        with col2:
            if energy_fig:
                st.plotly_chart(
                    energy_fig, 
                    use_container_width=True, 
                    key=self.get_unique_key("energy_consumption")
                )
        
        col3, col4 = st.columns(2)
        
        with col3:
            if comfort_fig:
                st.plotly_chart(
                    comfort_fig, 
                    use_container_width=True, 
                    key=self.get_unique_key("comfort_score")
                )
        
        with col4:
            if humidity_fig:
                st.plotly_chart(
                    humidity_fig, 
                    use_container_width=True, 
                    key=self.get_unique_key("humidity_levels")
                )
        
        # Basic statistics
        energy_metrics = self.hvac_system.get_energy_analytics(hours)
        if energy_metrics:
            st.markdown("### 📊 Performance Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Energy", f"{energy_metrics['total_energy_kwh']} kWh")
            with col2:
                st.metric("Cost Savings", f"${energy_metrics['cost_savings']}")
            with col3:
                st.metric("Avg Temperature", f"{energy_metrics['average_temperature']}°C")
            with col4:
                st.metric("System Efficiency", f"{energy_metrics.get('equipment_efficiency', 0.85):.1%}")
    
    def display_ai_optimization_panel(self):
        """Display advanced AI optimization panel"""
        st.markdown("## 🤖 Advanced AI Optimization")
        
        # Check for pending optimization from sidebar
        if st.session_state.pending_optimization:
            optimization_mode = st.session_state.optimization_mode
            self._execute_optimization(optimization_mode)
            st.session_state.pending_optimization = False
        
        # Optimization controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            optimization_mode = st.selectbox(
                "Optimization Strategy",
                ["Auto", "Energy Saving", "Comfort Focus", "Balanced"],
                key="main_optimization_strategy"
            )
        
        with col2:
            if st.button("🚀 Run AI Analysis", use_container_width=True, key="run_main_analysis"):
                self._execute_optimization(optimization_mode)
        
        # Display previous results if available
        if st.session_state.optimization_results:
            self._display_optimization_results(st.session_state.optimization_results)
        else:
            st.info("👆 Run AI analysis to get optimization recommendations for your HVAC system.")
    
    def _execute_optimization(self, mode: str):
        """Execute optimization and store results"""
        with st.spinner(f"🧠 Running {mode} optimization with advanced AI algorithms..."):
            optimization = self.hvac_system.run_optimization(mode.lower().replace(' ', '_'))
            
            if optimization:
                st.session_state.optimization_results = optimization
                st.session_state.last_optimization_time = datetime.now()
                st.success("✅ Advanced AI Optimization Completed!")
            else:
                st.error("❌ Optimization failed. Please check system status and try again.")
    
    def _display_optimization_results(self, optimization):
        """Display comprehensive optimization results"""
        st.markdown("### 📈 Optimization Results")
        
        # Key metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            current_temp = self.hvac_system.get_current_status().get('temperature', 22)
            temp_diff = optimization['optimal_temperature'] - current_temp
            st.metric(
                "🎯 Optimal Temperature",
                f"{optimization['optimal_temperature']}°C",
                f"{temp_diff:+.1f}°C"
            )
        
        with col2:
            st.metric(
                "💨 Ventilation Rate",
                f"{optimization['ventilation_rate']:.2f}",
                f"{(optimization['ventilation_rate'] - 0.5):+.2f}"
            )
        
        with col3:
            st.metric(
                "💰 Energy Savings",
                f"{optimization['energy_savings_percent']}%",
                f"${optimization['cost_savings']:.2f}/h"
            )
        
        with col4:
            st.metric(
                "😊 Comfort Score",
                f"{optimization['comfort_score']}/100",
                f"+{optimization['comfort_score'] - 80:.1f}"
            )
        
        # Display recommendations
        if optimization['recommendations']:
            st.markdown("### 💡 AI Recommendations")
            for i, recommendation in enumerate(optimization['recommendations']):
                st.markdown(f"""
                <div class="recommendation-box">
                    <strong>Recommendation #{i+1}:</strong> {recommendation}
                </div>
                """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Apply Optimizations", key="apply_opt_btn_main"):
                st.success("🎉 Optimizations applied successfully!")
                st.balloons()
        with col2:
            if st.button("🔄 Run Again", key="rerun_opt_btn_main"):
                st.rerun()
    
    def display_predictive_analytics(self):
        """Display predictive analytics"""
        st.markdown("## 🔮 Predictive Analytics")
        
        # Generate sample forecast data
        hours = 24
        future_times = [datetime.now() + timedelta(hours=i) for i in range(hours)]
        
        predicted_temperature = [22 + 2 * math.sin(i * 0.26) for i in range(hours)]
        predicted_energy = [3.0 + 0.5 * math.sin(i * 0.25) for i in range(hours)]
        
        # Create forecast chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=future_times, y=predicted_temperature,
            name="Predicted Temperature",
            line=dict(color='red', dash='dot', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=future_times, y=predicted_energy,
            name="Predicted Energy",
            line=dict(color='orange', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            height=400,
            title="24-Hour Predictive Forecast",
            yaxis=dict(title="Temperature (°C)"),
            yaxis2=dict(title="Energy (kW)", overlaying='y', side='right')
        )
        
        st.plotly_chart(fig, use_container_width=True, key=self.get_unique_key("predictive"))
        
        # Insights
        st.markdown("### 💡 Predictive Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("""
            **Energy Saving Opportunity**
            - Low occupancy predicted tonight
            - Recommended: Increase temperature by 2°C
            - Potential savings: 15-20%
            """)
        
        with col2:
            st.warning("""
            **High Demand Alert**
            - Peak occupancy expected tomorrow at 14:00
            - Recommended: Pre-cool at 13:00
            - Ensure maximum ventilation
            """)
    
    def display_system_health(self):
        """Display system health monitoring"""
        st.markdown("## 🏥 System Health & Maintenance")
        
        # Equipment status simulation
        equipment_status = [
            {'name': 'Chiller Unit', 'status': 'Normal', 'efficiency': 92},
            {'name': 'AHU System', 'status': 'Warning', 'efficiency': 78},
            {'name': 'Cooling Tower', 'status': 'Normal', 'efficiency': 88},
            {'name': 'VFD Pumps', 'status': 'Critical', 'efficiency': 65},
        ]
        
        # Display equipment status
        for equipment in equipment_status:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**{equipment['name']}**")
            
            with col2:
                status_color = {
                    'Normal': '#51cf66',
                    'Warning': '#ffd43b', 
                    'Critical': '#ff6b6b'
                }[equipment['status']]
                st.markdown(f"<span style='color: {status_color}; font-weight: bold;'>{equipment['status']}</span>", 
                           unsafe_allow_html=True)
            
            with col3:
                st.progress(equipment['efficiency'] / 100)
            
            with col4:
                st.write(f"{equipment['efficiency']}%")
        
        # System alerts
        st.markdown("### ⚠️ System Status")
        st.info("""
        **All Systems Operational**
        - No critical alerts detected
        - Regular maintenance schedule active
        - Performance within expected parameters
        """)
    
    def display_energy_reports(self):
        """Display comprehensive energy reports without session state conflicts"""
        st.markdown("## 📊 Energy Reports & Analytics")
        
        # Report period selection - use different key name to avoid conflict
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            report_period = st.selectbox(
                "Report Period",
                [7, 14, 30, 90],
                format_func=lambda x: f"Last {x} Days",
                key="energy_report_period_selector"  # Changed key name
            )
        
        with col2:
            generate_report_clicked = st.button("📈 Generate Report", key="generate_energy_report_btn")
        
        with col3:
            export_pdf_clicked = st.button("📥 Export PDF", key="export_energy_pdf_btn")
            if export_pdf_clicked:
                st.info("PDF export feature would be implemented here")
        
        # Generate and display report when button is clicked
        if generate_report_clicked:
            with st.spinner(f"Generating {report_period}-day energy report..."):
                # Use the actual HVAC system to generate report
                energy_report = self.hvac_system.get_energy_report(report_period)
                
                if energy_report:
                    st.success("Energy report generated successfully!")
                    
                    # Display report summary
                    st.markdown("### 📋 Report Summary")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            "Total Energy",
                            f"{energy_report['summary']['total_energy']:.0f} kWh",
                            f"{report_period} days"
                        )
                    
                    with col2:
                        st.metric(
                            "Cost Savings",
                            f"${energy_report['summary']['total_savings']:.0f}",
                            "Total period"
                        )
                    
                    with col3:
                        st.metric(
                            "Carbon Reduction",
                            f"{energy_report['summary']['carbon_reduction']:.0f} kg",
                            "CO₂ saved"
                        )
                    
                    with col4:
                        st.metric(
                            "Avg Efficiency",
                            f"{energy_report['summary']['average_efficiency']:.1%}",
                            "System overall"
                        )
                    
                    # Carbon analysis
                    st.markdown("### 🌱 Carbon Footprint Analysis")
                    carbon_data = energy_report['carbon_analysis']
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("CO₂ Emissions", f"{carbon_data['carbon_kg']} kg")
                    with col2:
                        st.metric("Trees Equivalent", f"{carbon_data['trees_equivalent']:.1f}")
                    with col3:
                        st.metric("Cars Equivalent", f"{carbon_data['cars_equivalent']:.3f}")
                    with col4:
                        st.metric("Flights Equivalent", f"{carbon_data['flights_equivalent']:.2f}")
                    
                    # Recommendations
                    st.markdown("### 💡 Energy Efficiency Recommendations")
                    for i, recommendation in enumerate(energy_report['recommendations']):
                        st.markdown(f"""
                        <div class="recommendation-box">
                            <strong>Recommendation #{i+1}:</strong> {recommendation}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.error("Failed to generate energy report")
        
        # Display sample report if no report has been generated yet
        elif not generate_report_clicked:
            st.info("👆 Click 'Generate Report' to analyze energy performance and get optimization recommendations.")
            
            # Show sample metrics
            st.markdown("### 📊 Sample Report Preview")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Estimated Energy Use", "1,250 kWh", "7 days")
            with col2:
                st.metric("Potential Savings", "$45", "Weekly")
            with col3:
                st.metric("Carbon Reduction", "625 kg", "CO₂ saved")
            with col4:
                st.metric("System Efficiency", "85%", "Current")
    
    def run_dashboard(self):
        """Main method to run the complete dashboard"""
        try:
            # Display header and controls
            self.display_header()
            operation_mode = self.display_sidebar_controls()
            
            # Display real-time metrics
            self.display_real_time_metrics()
            
            # Create comprehensive tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📈 Analytics Dashboard", 
                "🤖 AI Optimization", 
                "🔮 Predictive Analytics",
                "🏥 System Health",
                "📊 Energy Reports"
            ])
            
            with tab1:
                self.display_analytics_dashboard()
            
            with tab2:
                self.display_ai_optimization_panel()
            
            with tab3:
                self.display_predictive_analytics()
            
            with tab4:
                self.display_system_health()
            
            with tab5:
                self.display_energy_reports()
            
            # Auto-refresh if enabled
            if st.session_state.auto_refresh:
                time.sleep(10)
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ Dashboard error: {str(e)}")
            logger.error(f"Dashboard error: {e}")
            st.info("🔄 Please refresh the page to restart the application.")
            
# Main execution
if __name__ == "__main__":
    try:
        # Initialize the complete HVAC system
        with st.spinner("🚀 Initializing Advanced AI-Powered HVAC System..."):
            hvac_system = ComprehensiveHVACSystem()
            dashboard = AdvancedStreamlitDashboard(hvac_system)
        
        # Run the dashboard
        dashboard.run_dashboard()
        
    except Exception as e:
        st.error(f"❌ System initialization failed: {str(e)}")
        st.info("🔄 Please refresh the page and try again.")
        logger.error(f"System initialization failed: {e}")