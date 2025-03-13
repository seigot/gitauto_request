import tkinter as tk
from tkintermapview import TkinterMapView
import requests
import json
from tkinter import messagebox

class NavigationApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Simple Navigation App')
        
        # OpenRouteService API key - Replace with your own key
        self.ors_api_key = 'YOUR_API_KEY'
        
        # Initialize coordinates
        self.start_coords = None
        self.end_coords = None
        
        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill='both', expand=True)
        
        # Create map widget
        self.map_widget = TkinterMapView(self.main_frame, width=800, height=600)
        self.map_widget.pack(fill='both', expand=True)
        
        # Set initial position (Tokyo)
        self.map_widget.set_position(35.6762, 139.6503)
        self.map_widget.set_zoom(10)
        
        # Create buttons
        self.button_frame = tk.Frame(root)
        self.button_frame.pack(fill='x')
        
        self.start_button = tk.Button(self.button_frame, text='Set Start Point',
                                    command=self.set_start_point)
        self.start_button.pack(side='left', padx=5, pady=5)
        
        self.end_button = tk.Button(self.button_frame, text='Set End Point',
                                  command=self.set_end_point)
        self.end_button.pack(side='left', padx=5, pady=5)
        
        self.route_button = tk.Button(self.button_frame, text='Calculate Route',
                                    command=self.calculate_route)
        self.route_button.pack(side='left', padx=5, pady=5)
        
        self.clear_button = tk.Button(self.button_frame, text='Clear',
                                    command=self.clear_route)
        self.clear_button.pack(side='left', padx=5, pady=5)
        
        # Bind map click event
        self.map_widget.add_left_click_map_command(self.on_map_click)
        
        # Store markers and path
        self.start_marker = None
        self.end_marker = None
        self.route_path = None
        
        self.point_selection_mode = None
    
    def on_map_click(self, coords):
        if self.point_selection_mode == 'start':
            self.start_coords = coords
            if self.start_marker:
                self.map_widget.delete_marker(self.start_marker)
            self.start_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                         text='Start')
            self.point_selection_mode = None
        elif self.point_selection_mode == 'end':
            self.end_coords = coords
            if self.end_marker:
                self.map_widget.delete_marker(self.end_marker)
            self.end_marker = self.map_widget.set_marker(coords[0], coords[1],
                                                       text='End')
            self.point_selection_mode = None
    
    def set_start_point(self):
        self.point_selection_mode = 'start'
        messagebox.showinfo('Info', 'Click on the map to set start point')
    
    def set_end_point(self):
        self.point_selection_mode = 'end'
        messagebox.showinfo('Info', 'Click on the map to set end point')
    
    def calculate_route(self):
        if not self.start_coords or not self.end_coords:
            messagebox.showerror('Error', 'Please set both start and end points')
            return
        
        # OpenRouteService API endpoint
        url = 'https://api.openrouteservice.org/v2/directions/driving-car'
        
        headers = {
            'Authorization': self.ors_api_key,
            'Content-Type': 'application/json'
        }
        
        body = {
            'coordinates': [
                [self.start_coords[1], self.start_coords[0]],
                [self.end_coords[1], self.end_coords[0]]
            ]
        }
        
        try:
            response = requests.post(url, json=body, headers=headers)
            if response.status_code == 200:
                route_data = response.json()
                coordinates = route_data['features'][0]['geometry']['coordinates']
                # Convert coordinates from [lon, lat] to [lat, lon]
                path_coords = [(coord[1], coord[0]) for coord in coordinates]
                
                # Clear existing route if any
                if self.route_path:
                    self.map_widget.delete_path(self.route_path)
                
                # Draw new route
                self.route_path = self.map_widget.set_path(path_coords)
            else:
                messagebox.showerror('Error',
                                   f'Failed to calculate route: {response.text}')
        except Exception as e:
            messagebox.showerror('Error', f'Error calculating route: {str(e)}')
    
    def clear_route(self):
        if self.start_marker:
            self.map_widget.delete_marker(self.start_marker)
            self.start_marker = None
        if self.end_marker:
            self.map_widget.delete_marker(self.end_marker)
            self.end_marker = None
        if self.route_path:
            self.map_widget.delete_path(self.route_path)
            self.route_path = None
        self.start_coords = None
        self.end_coords = None

if __name__ == '__main__':
    root = tk.Tk()
    app = NavigationApp(root)
    root.mainloop()