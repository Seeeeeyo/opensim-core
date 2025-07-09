#include <iostream>
#include <vector>
#include <string>

// Simple demonstration of the BufferedMarkersReference concept
class SimpleBufferedMarkersReference {
private:
    std::vector<std::string> markerNames;
    std::vector<std::vector<double>> markerBuffer;
    std::vector<double> timeBuffer;
    
public:
    void setMarkerNames(const std::vector<std::string>& names) {
        markerNames = names;
        std::cout << "Set " << markerNames.size() << " marker names:" << std::endl;
        for (const auto& name : markerNames) {
            std::cout << "  - " << name << std::endl;
        }
    }
    
    void addMarkerFrame(double time, const std::vector<double>& markerData) {
        timeBuffer.push_back(time);
        markerBuffer.push_back(markerData);
        std::cout << "Added frame at time " << time << " with " << markerData.size() << " marker values" << std::endl;
    }
    
    bool getMarkersAtTime(double time, std::vector<double>& markers) {
        // Simple implementation: find the closest time
        if (timeBuffer.empty()) return false;
        
        size_t bestIdx = 0;
        double bestDiff = std::abs(timeBuffer[0] - time);
        
        for (size_t i = 1; i < timeBuffer.size(); ++i) {
            double diff = std::abs(timeBuffer[i] - time);
            if (diff < bestDiff) {
                bestDiff = diff;
                bestIdx = i;
            }
        }
        
        markers = markerBuffer[bestIdx];
        std::cout << "Retrieved " << markers.size() << " markers for time " << time << " (closest: " << timeBuffer[bestIdx] << ")" << std::endl;
        return true;
    }
    
    size_t getBufferSize() const {
        return timeBuffer.size();
    }
};

int main() {
    std::cout << "=== Testing BufferedMarkersReference Concept ===" << std::endl;
    
    // Create the buffered reference
    SimpleBufferedMarkersReference bufferedRef;
    
    // Set up some marker names (simulating what would come from a .trc file)
    std::vector<std::string> markerNames = {
        "LFHD", "RFHD", "LBHD", "RBHD", "C7", "T10", "CLAV", "STRN", "RBAK"
    };
    
    bufferedRef.setMarkerNames(markerNames);
    
    // Simulate adding real-time marker data (this would come from a motion capture system)
    std::cout << "\n=== Simulating Real-time Data Stream ===" << std::endl;
    
    // Add some sample frames
    for (int frame = 0; frame < 5; ++frame) {
        double time = frame * 0.01; // 100 Hz
        std::vector<double> markerData;
        
        // Generate some sample marker data (normally this would come from the .trc file)
        for (size_t i = 0; i < markerNames.size(); ++i) {
            markerData.push_back(i * 10.0 + frame); // Simple test data
        }
        
        bufferedRef.addMarkerFrame(time, markerData);
    }
    
    std::cout << "\nBuffer now contains " << bufferedRef.getBufferSize() << " frames" << std::endl;
    
    // Test retrieving data
    std::cout << "\n=== Testing Data Retrieval ===" << std::endl;
    
    std::vector<double> retrievedMarkers;
    if (bufferedRef.getMarkersAtTime(0.025, retrievedMarkers)) {
        std::cout << "Successfully retrieved marker data!" << std::endl;
        std::cout << "First few marker values: ";
        for (size_t i = 0; i < std::min(size_t(3), retrievedMarkers.size()); ++i) {
            std::cout << retrievedMarkers[i] << " ";
        }
        std::cout << std::endl;
    }
    
    std::cout << "\n=== Test Complete ===" << std::endl;
    std::cout << "This demonstrates the core concept of BufferedMarkersReference:" << std::endl;
    std::cout << "1. Set marker names from a .trc file" << std::endl;
    std::cout << "2. Add frames of marker data as they arrive in real-time" << std::endl;
    std::cout << "3. Retrieve marker data at specific times for IK solving" << std::endl;
    std::cout << "4. The actual OpenSim implementation uses thread-safe queues and SimTK types" << std::endl;
    
    return 0;
} 