
set(SIMULATION_SUBDIRS 
        .
        Control
        Manager
        Model
        Wrap
        SimbodyEngine
        OpenSense)

set(SOURCES)
set(INCLUDES)
foreach(dir ${SIMULATION_SUBDIRS})
    file(GLOB SOURCES_ONEDIR ${dir}/*.cpp)
    file(GLOB INCLUDES_ONEDIR ${dir}/*.h)
    list(APPEND SOURCES ${SOURCES_ONEDIR})
    list(APPEND INCLUDES ${INCLUDES_ONEDIR})
endforeach()

# List of source files for the osimSimulation library.
set(CPP_FILES
    About.cpp
    AssemblySolver.cpp
    BufferedOrientationsReference.cpp
    BufferedMarkersReference.cpp
    CoordinateReference.cpp
    InverseDynamicsSolver.cpp
    InverseKinematicsSolver.cpp
    Manager/Manager.cpp
    MarkersReference.cpp
    Model/Model.cpp
    Model/ModelVisualizer.cpp
    Model/PointForceDirection.cpp
    MomentArmSolver.cpp
    OpenSense/IMUInverseKinematicsTool.cpp
    OpenSense/IMUPlacer.cpp
    OpenSense/IMUDataReader.cpp
    OpenSense/OpenSenseUtilities.cpp
    OpenSense/OrientationWeightSet.cpp
    OrientationsReference.cpp
    PositionMotion.cpp
    RegisterTypes_osimSimulation.cpp
    SimbodyEngine/SimbodyEngine.cpp
    SimulationUtilities.cpp
    StatesDocument.cpp
    StatesTrajectory.cpp
    StatesTrajectoryReporter.cpp
    VisualizerUtilities.cpp
)

# List of header files for the osimSimulation library.
set(H_FILES
    About.h
    AssemblySolver.h
    BufferedOrientationsReference.h
    BufferedMarkersReference.h
    Control/Control.h
    Control/ControlConstant.h
    Control/ControlLinear.h
    Control/ControlSet.h
    Control/ControlSetController.h
    Control/Controller.h
    Control/PrescribedController.h
    CoordinateReference.h
    InverseDynamicsSolver.h
    InverseKinematicsSolver.h
    Manager/Manager.h
    MarkersReference.h
    Model/Actuator.h
    Model/ActuatorSet.h
    Model/Analysis.h
    Model/AnalysisSet.h
    Model/BodySet.h
    Model/Component.h
    Model/ComponentSet.h
    Model/Constraint.h
    Model/ConstraintSet.h
    Model/ContactGeometry.h
    Model/ContactGeometrySet.h
    Model/ContactHalfSpace.h
    Model/ContactMesh.h
    Model/ContactSphere.h
    Model/PointForceDirection.h
    Model/PointSet.h
    Model/Probe.h
    Model/ProbeSet.h
    Model/Station.h
    Model/PhysicalOffsetFrame.h
    Model/Model.h
    Model/ModelVisualizer.h
    Model/ModelVisitor.h
    Model/Force.h
    Model/ForceAdapter.h
    Model/ForceSet.h
    Model/Frame.h
    Model/Geometry.h
    Model/HuntCrossleyForce.h
    Model/Joint.h
    Model/JointSet.h
    Model/Marker.h
    Model/MarkerSet.h
    MomentArmSolver.h
    OpenSense/IMUInverseKinematicsTool.h
    OpenSense/IMUPlacer.h
    OpenSense/IMUDataReader.h
    OpenSense/OpenSenseUtilities.h
    OpenSense/OrientationWeightSet.h
    OrientationsReference.h
    PositionMotion.h
    Reference.h
    RegisterTypes_osimSimulation.h
    Solver.h
    StatesDocument.h
    StatesTrajectory.h
    StatesTrajectoryReporter.h
    TableProcessor.h
    VisualizerUtilities.h
    Wrap/PathWrap.h
    Wrap/PathWrapSet.h
    Wrap/WrapObject.h
    Wrap/WrapObjectSet.h
    Wrap/WrapCylinder.h
    Wrap/WrapEllipsoid.h
    Wrap/WrapSphere.h
    Wrap/WrapTorus.h
    osimSimulation.h
    osimSimulationDLL.h
)

OpenSimAddLibrary(
    KIT Simulation
    AUTHORS "Ajay_Seth-Michael_Sherman-Ayman_Habib"
    LINKLIBS ${Simbody_LIBRARIES} osimCommon osimLepton
    INCLUDES ${INCLUDES}
    SOURCES ${SOURCES}
    TESTDIRS SimbodyEngine Test
    INCLUDEDIRS ${SIMULATION_SUBDIRS}
    )
