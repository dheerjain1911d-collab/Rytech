# Sample Inputs for Crop Recommendation

## Test Case 1: Rice-like conditions (high N, high rainfall)
- N: 
- P: 50
- K: 100
- Temperature: 28
- Humidity: 85
- pH: 6.5
- Rainfall: 1500

**Expected:** Rice top ML/rule rec.

## Test Case 2: Wheat (cooler, moderate rain)
- N: 150
- P: 60
- K: 60
- Temperature: 20
- Humidity: 65
- pH: 6.8
- Rainfall: 800

## Test Case 3: Potato (high P/K, cooler)
- N: 140
- P: 120
- K: 200
- Temperature: 20
- Humidity: 80
- pH: 5.8
- Rainfall: 600

## Test Case 4: Groundnut (low N, warm)
- N: 30
- P: 50
- K: 40
- Temperature: 30
- Humidity: 60
- pH: 6.5
- Rainfall: 800

Open http://127.0.0.1:5000, enter values, submit. See ML (22 crops) + rule (6 crops) recs + profit.
