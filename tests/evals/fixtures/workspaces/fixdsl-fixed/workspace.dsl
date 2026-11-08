workspace "ParkFlow" "Manages a multi-level parking garage." {
    model {
        driver = person "Driver" "Arrives at and departs from the garage."
        traffic = element "City Traffic Feed" "Provides live traffic data for the region."
        garage = softwareSystem "Parking Garage" "Manages bays, entry, exit, and billing." {
            entry = container "Entry Gate Controller" "Reads licence plates and drives the entry barrier." "C/C++"
            exit = container "Exit Gate Controller" "Drives the exit barrier." "C/C++"
            billing = container "Billing Service" "Calculates fees and issues invoices." "Java"
        }
        entry -> billing "Registers bay occupancy in" "gRPC"
        exit -> billing "Clears bay occupancy in" "gRPC"
        billing -> traffic "Considers live traffic from" "REST/JSON"
        driver -> entry "Enters through" "HTTPS"
    }
    views {
        systemContext garage "GarageContext" {
            include *
            autoLayout
        }
    }
}
