crops_data = [
    {
        'name': 'Rice',
        'optimal': {'N': (100, 150), 'P': (40, 60), 'K': (80, 120), 'temp': (20, 35), 'humidity': (70, 90), 'ph': (5.5, 7.0), 'rainfall': (1000, 2000), 'area': (1, 100)},
        'suitability': 'High yield in irrigated areas, large farms',
        'economics': {'yield_ton_per_ha': 4.0, 'price_per_ton': 22000, 'base_cost_per_ha': 38000}
    },
    {
        'name': 'Wheat',
        'optimal': {'N': (120, 180), 'P': (50, 80), 'K': (50, 80), 'temp': (15, 25), 'humidity': (50, 70), 'ph': (6.0, 7.5), 'rainfall': (500, 1000), 'area': (0.5, 50)},
        'suitability': 'Rabi crop, cooler climates, medium farms',
        'economics': {'yield_ton_per_ha': 3.2, 'price_per_ton': 23000, 'base_cost_per_ha': 30000}
    },
    {
        'name': 'Maize',
        'optimal': {'N': (120, 200), 'P': (50, 100), 'K': (40, 80), 'temp': (20, 30), 'humidity': (60, 80), 'ph': (5.5, 7.5), 'rainfall': (500, 1200), 'area': (1, 20)},
        'suitability': 'Kharif crop, versatile, small-medium farms',
        'economics': {'yield_ton_per_ha': 3.6, 'price_per_ton': 21000, 'base_cost_per_ha': 29000}
    },
    {
        'name': 'Cotton',
        'optimal': {'N': (80, 120), 'P': (40, 60), 'K': (80, 120), 'temp': (25, 35), 'humidity': (60, 80), 'ph': (6.0, 8.0), 'rainfall': (700, 1300), 'area': (2, 200)},
        'suitability': 'Cash crop, drought tolerant, large areas',
        'economics': {'yield_ton_per_ha': 2.0, 'price_per_ton': 62000, 'base_cost_per_ha': 52000}
    },
    {
        'name': 'Potato',
        'optimal': {'N': (120, 180), 'P': (100, 150), 'K': (150, 250), 'temp': (15, 25), 'humidity': (70, 90), 'ph': (5.0, 6.5), 'rainfall': (500, 750), 'area': (0.1, 5)},
        'suitability': 'High P&K needs, small intensive farms',
        'economics': {'yield_ton_per_ha': 22.0, 'price_per_ton': 12000, 'base_cost_per_ha': 130000}
    },
    {
        'name': 'Groundnut',
        'optimal': {'N': (20, 40), 'P': (40, 60), 'K': (30, 50), 'temp': (25, 35), 'humidity': (50, 70), 'ph': (6.0, 7.0), 'rainfall': (500, 1000), 'area': (0.5, 10)},
        'suitability': 'Low N, legumes, small-medium farms',
        'economics': {'yield_ton_per_ha': 1.8, 'price_per_ton': 60000, 'base_cost_per_ha': 45000}
    }
]
