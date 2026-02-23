1_UseCaseDiagram.puml
@startuml
actor Admin
actor "Station Master" as SM

rectangle "Platform Assignment System" {
  Admin -- (Add Train)
  Admin -- (Update Train)
  Admin -- (Delete Train)

  SM -- (View Platform Status)
  SM -- (Assign Platform)
  SM -- (Modify Assignment)
}
@enduml

  2_ClassDiagram.puml

  @startuml
class Train {
  trainId
  trainName
  arrivalTime
  departureTime
}

class Platform {
  platformNo
  status
}

class Assignment {
  assignmentId
  date
}

class User {
  userId
  role
}

class PlatformAssignmentSystem {
  assignPlatform()
  releasePlatform()
  checkAvailability()
}

Train --> Assignment
Platform --> Assignment
User --> PlatformAssignmentSystem
PlatformAssignmentSystem --> Train
PlatformAssignmentSystem --> Platform
@enduml

3_SequenceDiagram.puml
  @startuml
actor "Station Master"
participant System
participant Platform
participant Train

"Station Master" -> System : requestPlatform()
System -> Platform : checkAvailability()
Platform --> System : available
System -> Train : assignPlatform()
System --> "Station Master" : confirmation
@enduml

  4_CollaborationDiagram.puml
  @startuml
object StationMaster
object System
object Platform
object Train

StationMaster --> System : assignPlatform
System --> Platform : availabilityCheck
System --> Train : allocatePlatform
@enduml

  5_StateChartDiagram.puml
  
@startuml
[*] --> Available
Available --> Reserved : assign
Reserved --> Occupied : trainArrives
Occupied --> Available : trainDeparts
@enduml

6_FlowchartDiagram.puml
  
  @startuml
start
:Enter Train Details;
:Check Platform Availability;
if (Platform Available?) then (Yes)
  :Assign Platform;
else (No)
  :Wait or Reschedule;
endif
stop
@enduml

  7_ComponentDiagram.puml
  @startuml
component "User Interface"
component "Assignment Logic"
component "Database"

"User Interface" --> "Assignment Logic"
"Assignment Logic" --> "Database"
@enduml

  8_DeploymentDiagram.puml
  @startuml
node Client
node "Application Server"
node "Database Server"

Client --> "Application Server"
"Application Server" --> "Database Server"
@enduml

  9_PackageDiagram.puml
  @startuml
package authentication
package trainManagement
package platformManagement
package assignmentLogic
package database

authentication --> assignmentLogic
trainManagement --> assignmentLogic
platformManagement --> assignmentLogic
assignmentLogic --> database
@enduml
  
  
  
