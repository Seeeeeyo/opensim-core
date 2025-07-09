import opensim as osim
import numpy as np
import time
import os
from datetime import datetime

def load_ik_task_set_from_setup(setup_file_path):
    """
    Load IKTaskSet from OpenSim IK setup file using native OpenSim functionality.
    Returns a dictionary with marker names as keys and weights as values.
    """
    marker_weights = {}
    
    try:
        # Use OpenSim's InverseKinematicsTool to load the setup file
        ik_tool = osim.InverseKinematicsTool(setup_file_path)
        
        # Get the IKTaskSet from the tool
        ik_task_set = ik_tool.get_IKTaskSet()
        
        print(f"✓ Loaded IKTaskSet with {ik_task_set.getSize()} tasks")
        
        # Iterate through all tasks in the task set
        for i in range(ik_task_set.getSize()):
            task = ik_task_set.get(i)
            
            # Check if this is a marker task (not coordinate task)
            if hasattr(task, 'getApply') and hasattr(task, 'getWeight'):
                marker_name = task.getName()
                is_applied = task.getApply()
                weight = task.getWeight()
                
                if is_applied:
                    marker_weights[marker_name] = weight
                    print(f"  ✓ {marker_name}: weight={weight}")
                else:
                    print(f"  ✗ {marker_name}: disabled (apply=false)")
        
        print(f"✓ Extracted {len(marker_weights)} enabled markers from IKTaskSet")
        
    except Exception as e:
        print(f"⚠ Error loading IK setup file {setup_file_path}: {e}")
        print("  Using default weights of 1.0 for all markers")
    
    return marker_weights

def parse_trc_file(filepath):
    """
    Manually parses a TRC file to extract marker data and times.
    Skips header and returns times and a list of data rows.
    """
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the start of the data
    data_start_line = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('Frame#'):
            data_start_line = i + 2  # Data starts 2 lines after the header
            break
            
    times = []
    marker_data_rows = []
    
    for line in lines[data_start_line:]:
        parts = line.strip().split()
        if not parts:
            continue
        
        times.append(float(parts[1]))
        
        # Each marker is 3 coordinates (X, Y, Z)
        # The first two columns are Frame# and Time
        coord_data = [float(p) for p in parts[2:]]
        
        # Group coordinates into Vec3s
        num_markers = len(coord_data) // 3
        row_data = []
        for i in range(num_markers):
            x = coord_data[i*3]
            y = coord_data[i*3 + 1]
            z = coord_data[i*3 + 2]
            row_data.append(osim.Vec3(x, y, z))
        marker_data_rows.append(row_data)
        
    return times, marker_data_rows

def write_ik_results_to_mot_file(results_data, filename="ik_results.mot"):
    """
    Write IK results to a .mot file following OpenSim motion file format.
    """
    if not results_data:
        print("No results data to write")
        return
    
    # Get all coordinate names from the first successful result
    coordinate_names = []
    for result in results_data:
        if result['success'] and 'coordinates' in result:
            coordinate_names = list(result['coordinates'].keys())
            break
    
    if not coordinate_names:
        print("No successful IK results found")
        return
    
    # Count successful results
    successful_results = [r for r in results_data if r['success']]
    
    with open(filename, 'w') as f:
        # Write header
        f.write("IKResults\n")
        f.write("version=1\n")
        f.write(f"nRows={len(successful_results)}\n")
        f.write(f"nColumns={len(coordinate_names) + 1}\n")  # +1 for time column
        f.write("inDegrees=yes\n")
        f.write("\n")
        f.write("Units are S.I. units (second, meters, Newtons, ...)\n")
        f.write("If the header above contains a line with 'inDegrees', this indicates whether rotational values are in degrees (yes) or radians (no).\n")
        f.write("\n")
        f.write("endheader\n")
        
        # Write column headers
        f.write("time")
        for coord_name in coordinate_names:
            f.write(f"\t{coord_name}")
        f.write("\n")
        
        # Write data rows (only successful results)
        for result in successful_results:
            f.write(f"      {result['time']:.8f}")
            for coord_name in coordinate_names:
                value = result['coordinates'].get(coord_name, 0.0)
                f.write(f"\t      {value:.8f}")
            f.write("\n")
    
    print(f"✓ IK results written to {filename}")
    print(f"  - {len(successful_results)} successful IK solutions")
    print(f"  - {len(coordinate_names)} coordinates")
    print(f"  - Time range: {successful_results[0]['time']:.3f}s to {successful_results[-1]['time']:.3f}s")

def ik_streaming_markers():
    # Load the model
    model = osim.Model("Hu_scaled_2.osim")

    visualize = True
    real_time = True
    debug = False
    ik_setup_file = "IK_Setup_1.xml"  # Path to your IK setup file
    
    model.setUseVisualizer(visualize)  # Disable visualizer for cleaner output

    # Get marker names from TRCFileAdapter (this part is reliable)
    marker_tables = osim.TRCFileAdapter().read("test1.trc")
    marker_names = list(marker_tables["markers"].getColumnLabels())
    print("marker_names", marker_names[:10])

    # Manually parse the TRC file to get data
    times, marker_data_rows = parse_trc_file("test1.trc")
    num_frames = len(times)

    # Load IKTaskSet from setup file using OpenSim's native functionality
    print(f"\nLoading IK setup file: {ik_setup_file}")
    setup_marker_weights = load_ik_task_set_from_setup(ik_setup_file)

    # Create marker weights using IK setup file
    marker_weights = osim.SetMarkerWeights()
    for name in marker_names:
        weight = osim.MarkerWeight()
        weight.setName(name)
        
        # Use weight from setup file if available, otherwise default to 1.0
        if name in setup_marker_weights:
            weight_value = setup_marker_weights[name]
            print(f"  Using setup weight for {name}: {weight_value}")
        else:
            weight_value = 1.0
            print(f"  Using default weight for {name}: {weight_value} (not found in setup)")
        
        weight.setWeight(weight_value)
        marker_weights.cloneAndAppend(weight)

    # Summary of marker weights configuration
    enabled_markers = [name for name in marker_names if name in setup_marker_weights]
    disabled_markers = [name for name in marker_names if name not in setup_marker_weights]
    
    print(f"\n📊 Marker Weight Summary:")
    print(f"  - Total markers in TRC: {len(marker_names)}")
    print(f"  - Enabled in IK setup: {len(enabled_markers)}")
    print(f"  - Using default weights: {len(disabled_markers)}")
    if disabled_markers:
        print(f"  - Markers with default weights: {disabled_markers[:5]}{'...' if len(disabled_markers) > 5 else ''}")

    # Create our custom BufferedMarkersReference
    buffered_markers_reference = osim.BufferedMarkersReference()
    
    # Create the IK solver (needs a reference, so we still create this)
    trc_markers_reference = osim.MarkersReference("test1.trc", marker_weights)
    # osim.SimTKArrayCoordinateReference(): An empty array to hold coordinate references
    # Purpose: IK can optionally use coordinate references (like joint angle targets) in addition to marker data. Since we're only using markers, this is empty
    # Why needed: The IK solver constructor requires this parameter even if we don't use coordinate-based targets
    coordinate_references = osim.SimTKArrayCoordinateReference()
    ik_solver = osim.InverseKinematicsSolver(model, trc_markers_reference, coordinate_references)
    
    # Create IK reporter to store results (similar to ik_streaming.py)
    ik_reporter = osim.TableReporter()
    ik_reporter.setName('ik_reporter')
    coordinates = model.getCoordinateSet()
    for coord in coordinates:
        ik_reporter.addToReport(coord.getOutput('value'), coord.getName())
    model.addComponent(ik_reporter)
    model.finalizeConnections()
    
    state = model.initSystem()
    
    # Initialize the IK solver with the correct start time
    print("Initializing IK solver...")
    try:
        # Use the actual start time from the TRC file instead of 0.0
        start_time = times[0]  # This should be 0.125
        state.setTime(start_time)
        ik_solver.assemble(state)
        print(f"✓ IK solver initialized successfully at time {start_time:.3f}s")

        if visualize: # initialize visualization
            model.getVisualizer().show(state)
            model.getVisualizer().getSimbodyVisualizer().setShowSimTime(True)

    except Exception as e:
        print(f"⚠ IK solver initialization failed: {e}")
        # Try with a more conservative approach
        try:
            print("Trying alternative initialization...")
            # Set a reasonable initial pose
            for coord_idx in range(model.getCoordinateSet().getSize()):
                coord = model.getCoordinateSet().get(coord_idx)
                # Set to default values
                coord.setValue(state, coord.getDefaultValue())
            state.setTime(start_time)
            ik_solver.assemble(state)
            print(f"✓ IK solver initialized with default pose at time {start_time:.3f}s")
        except Exception as e2:
            print(f"⚠ Alternative initialization also failed: {e2}")
            return
    
    print(f"Processing {num_frames} frames from TRC file...")
    
    # Store results for writing to file
    results_data = []
    
    # Performance tracking
    processing_times = []
    start_processing = time.time()
    
    # Loop through each frame, push to buffer, and solve IK
    for i in range(num_frames):
        current_time = times[i]
        
        # Get the marker data for the current frame from our parsed data
        row_vector_mm = marker_data_rows[i]
        
        # Data is in mm, convert to meters for OpenSim.
        # It's already Vec3, so just need to scale and put in RowVector.
        row_vector_m = osim.RowVectorVec3(len(row_vector_mm))
        for j, vec_mm in enumerate(row_vector_mm):
            row_vector_m[j] = osim.Vec3(vec_mm[0]/1000, 
                                        vec_mm[1]/1000, 
                                        vec_mm[2]/1000)

        # Add the frame to the buffer
        buffered_markers_reference.putValues(current_time, row_vector_m)
        if debug:
            print(f"Frame {i}: time={current_time:.3f}s, buffered {len(marker_names)} markers")
        
        # For demonstration, also retrieve data from buffer
        if debug:
            if i % 3 == 0:
                try:
                    values = osim.SimTKArrayVec3()
                    retrieved_time = buffered_markers_reference.getNextValuesAndTime(values)
                    print(f"  ✓ Retrieved from buffer: time={retrieved_time:.3f}s, {values.size()} markers")
                    # Show first few marker positions
                    for k in range(min(3, values.size())):
                        marker = values.getElt(k)
                        print(f"    Marker {k}: {marker_names[k]} ({marker[0]:.3f}, {marker[1]:.3f}, {marker[2]:.3f})")
                except Exception as e:
                    print(f"  ✗ Buffer retrieval failed: {e}")

        # Set the state time and solve IK
        state.setTime(current_time)
        
        # Track processing time for this frame
        frame_start_time = time.time()
        
        # Initialize result data for this frame
        frame_result = {
            'frame': i,
            'time': current_time,
            'success': False,
            'error_message': '',
            'coordinates': {}
        }
        
        try:
            ik_solver.track(state)
            if visualize:
                model.getVisualizer().show(state)
            model.realizeReport(state)

            if real_time: # The previous kinematics are pulled here and can be used to implement any custom real-time applications
                try:
                    # Get the most recent row from the IK reporter table
                    table = ik_reporter.getTable()
                    if table.getNumRows() > 0:
                        rowind = table.getRowIndexBeforeTime(current_time)
                        kin_step = table.getRowAtIndex(rowind).to_numpy() # joint angles for current time step as numpy array
                        # see the header of the saved .sto files for the names of the corresponding joints.
                        ### ADD CUSTOM CODE HERE FOR REAL-TIME APPLICATIONS ###
                        # Example: print(f"Real-time kinematics at {current_time:.3f}s: {kin_step[:5]}")
                except Exception as e:
                    print(f"  ⚠ Real-time data access failed: {e}")
                    pass

            
            # Extract all coordinate values
            for coord_idx in range(model.getCoordinateSet().getSize()):
                coord = model.getCoordinateSet().get(coord_idx)
                value = coord.getValue(state)
                frame_result['coordinates'][coord.getName()] = value
            
            frame_result['success'] = True
            
            # Print some coordinate values
            if debug:   
                if i % 5 == 0:
                    print(f"  ✓ IK Results for frame {i}:")
                    for coord_idx in range(min(5, model.getCoordinateSet().getSize())):
                        coord = model.getCoordinateSet().get(coord_idx)
                        value = coord.getValue(state)
                        print(f"    {coord.getName()}: {value:.3f}")
                        
        except Exception as e:
            error_msg = str(e)[:100]  # Truncate long error messages
            frame_result['error_message'] = error_msg
            print(f"  ⚠ IK tracking: {error_msg}...")
            # Try to continue with the next frame
            continue
        
        # Store the result
        results_data.append(frame_result)
        
        # Track processing time
        frame_processing_time = time.time() - frame_start_time
        processing_times.append(frame_processing_time)
        
        # Progress reporting every 50 frames
        if i % 50 == 0 and i > 0:
            avg_time = sum(processing_times[-50:]) / min(50, len(processing_times))
            progress = (i / num_frames) * 100
            print(f"  📊 Progress: {progress:.1f}% | Avg frame time: {avg_time*1000:.1f}ms")

    # Get IK results from reporter and save to .sto file (like ik_streaming.py)
    print("Saving IK results to .sto file...")
    ik_results = ik_reporter.getTable()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sto_filename = f"ik_results_{timestamp}.sto"
    osim.STOFileAdapter.write(ik_results, sto_filename)
    print(f"✓ IK results saved to {sto_filename}")
    print(f"  - {ik_results.getNumRows()} time steps")
    print(f"  - {ik_results.getNumColumns()} coordinates")
    print(f"  - Time range: {ik_results.getIndependentColumn()[0]:.3f}s to {ik_results.getIndependentColumn()[-1]:.3f}s")

    # Write results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ik_results_{timestamp}.mot"
    write_ik_results_to_mot_file(results_data, filename)
    
    # Performance summary
    total_time = time.time() - start_processing
    avg_frame_time = sum(processing_times) / len(processing_times) if processing_times else 0
    print(f"\n📈 Performance Summary:")
    print(f"  - Total processing time: {total_time:.2f}s")
    print(f"  - Average frame time: {avg_frame_time*1000:.1f}ms")
    print(f"  - Effective rate: {len(processing_times)/total_time:.1f} frames/sec")


if __name__ == "__main__":
    ik_streaming_markers() 