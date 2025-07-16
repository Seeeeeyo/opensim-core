/* -------------------------------------------------------------------------- *
 *                    OpenSim:  BufferedMarkersReference.h                    *
 * -------------------------------------------------------------------------- *
 * The OpenSim API is a toolkit for musculoskeletal modeling and simulation.  *
 * See http://opensim.stanford.edu and the NOTICE file for more information.  *
 * OpenSim is developed at Stanford University and supported by the US        *
 * National Institutes of Health (U54 GM072970, R24 HD065690) and by DARPA    *
 * through the Warrior Web program.                                           *
 *                                                                            *
 * Copyright (c) 2005-2023 Stanford University and the Authors                *
 * Author(s):                                      *
 *                                                                            *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may    *
 * not use this file except in compliance with the License. You may obtain a  *
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0.         *
 *                                                                            *
 * Unless required by applicable law or agreed to in writing, software        *
 * distributed under the License is distributed on an "AS IS" BASIS,          *
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   *
 * See the License for the specific language governing permissions and        *
 * limitations under the License.                                             *
 * -------------------------------------------------------------------------- */
#ifndef OPENSIM_BUFFERED_MARKERS_REFERENCE_H_
#define OPENSIM_BUFFERED_MARKERS_REFERENCE_H_

#include "MarkersReference.h"
#include <OpenSim/Common/DataQueue.h>
#include <OpenSim/Common/TimeSeriesTable.h>
#include <OpenSim/Common/Units.h>

namespace OpenSim {
/**
 * A MarkersReference that provides the marker data from a buffer, intended to be
 * populated in real-time. This class is backed by a DataQueue of marker data
 * (Vec3s). This class is intended to be used in streaming applications.
 * For example, reading marker data from a device and feeding it to a real-time
 * IK solver.
 *
 * @author Selim Gilon
 */
class OSIMSIMULATION_API BufferedMarkersReference : public MarkersReference {
    OpenSim_DECLARE_CONCRETE_OBJECT(BufferedMarkersReference, MarkersReference);

public:
    BufferedMarkersReference();
    
    /** Constructor from TimeSeriesTable and marker weights */
    BufferedMarkersReference(const TimeSeriesTable_<SimTK::Vec3>& markerData,
                            const Set<MarkerWeight>& markerWeightSet,
                            Units units = Units(Units::Meters));

    /** get the time range for which this Reference values are valid,
        based on the loaded marker data. Extended to infinity for streaming.*/
    SimTK::Vec2 getValidTimeRange() const override {
        SimTK::Vec2 tableRange = MarkersReference::getValidTimeRange();
        return SimTK::Vec2(tableRange[0], SimTK::Infinity);
    }

    /**
    * Get the values of the MarkersReference at a specific time.
    * This method will block until the underlying buffer has data up to the
    * specified time.
    */
    void getValuesAtTime(
            double time, SimTK::Array_<SimTK::Vec3>& values) const override;

    /**
    * Get the next available frame of marker data and the corresponding time.
    * This method will block until a frame is available in the buffer.
    */
    double getNextValuesAndTime(SimTK::Array_<SimTK::Vec3>& values);

    /**
    * Add a frame of marker data to the buffer at a specific time.
    */
    void putValues(double time, const SimTK::RowVector_<SimTK::Vec3>& dataRow);

private:
    // The underlying DataQueue that holds the marker data.
    // The data is mutable so that getValuesAtTime can be const.
    mutable DataQueue_<SimTK::Vec3> _markerDataQueue;

    // A more robust internal cache to store streamed-in data, making this
    // class behave more like a TimeSeriesTable to the outside world.
    mutable TimeSeriesTable_<SimTK::Vec3> _streamedMarkerTable;
};

} // end of namespace OpenSim

#endif // OPENSIM_BUFFERED_MARKERS_REFERENCE_H_ 