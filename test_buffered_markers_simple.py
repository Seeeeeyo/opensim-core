#!/usr/bin/env python3

import opensim as osim
import numpy as np

def test_buffered_markers():
    print("Testing BufferedMarkersReference...")
    
    # Create a BufferedMarkersReference
    buffered_ref = osim.BufferedMarkersReference()
    print("✓ BufferedMarkersReference created")
    
    # Test putValues method
    print("Testing putValues method...")
    
    # Create some dummy marker data (3 markers)
    marker_data = osim.RowVectorVec3(3)
    marker_data[0] = osim.Vec3(1.0, 2.0, 3.0)  # First marker
    marker_data[1] = osim.Vec3(4.0, 5.0, 6.0)  # Second marker  
    marker_data[2] = osim.Vec3(7.0, 8.0, 9.0)  # Third marker
    
    # Add the data to the buffer
    time = 0.0
    buffered_ref.putValues(time, marker_data)
    print("✓ putValues method works")
    
    # Test getNextValuesAndTime method
    print("Testing getNextValuesAndTime method...")
    try:
        values = osim.SimTKArrayVec3()
        retrieved_time = buffered_ref.getNextValuesAndTime(values)
        print(f"✓ Retrieved time: {retrieved_time}")
        print(f"✓ Retrieved {values.size()} markers")
        for i in range(values.size()):
            marker = values.getElt(i)
            print(f"  Marker {i}: ({marker[0]}, {marker[1]}, {marker[2]})")
    except Exception as e:
        print(f"✗ getNextValuesAndTime failed: {e}")
    
    print("BufferedMarkersReference test completed!")

if __name__ == "__main__":
    test_buffered_markers() 