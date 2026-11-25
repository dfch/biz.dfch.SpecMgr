workspace "Stay Planner" "Plans and manages hotel stays for a regional hotel group." {
    model {
        guest = person "Guest" "Books and manages hotel stays."
        planner = softwareSystem "Stay Planner" "Manages reservations, rooms, rates, and stays." {
            portal = container "Reservation Portal" "Lets guests book and manage stays." "Python"
            mobile = container "Mobile App Backend" "Serves the hotel group's mobile app." "Kotlin"
            stays = container "Stay Service" "Registers and tracks stays." "Java"
            rooms = container "Room Assignment" "Assigns rooms to confirmed stays." "Java"
            rate = container "Rate Service" "Calculates stay rates." "Go"
            housekeeping = container "Housekeeping Service" "Plans cleaning tasks for the rooms." "C#"
            concierge = container "Concierge Service" "Handles guest requests and local recommendations." "Python"
            notifications = container "Notification Hub" "Sends booking and stay messages." "Python"
            deposits = container "Deposit Service" "Manages booking deposits and refunds." "Java"
            feedback = container "Feedback Service" "Collects and scores guest feedback." "Python"
            reporting = container "Reporting Service" "Produces occupancy and revenue reports." "Java"
            availability = container "Availability Search" "Finds rooms by date and type." "Go"
            scheduler = container "Batch Scheduler" "Runs the nightly batch jobs." "Java"
            staydb = container "Stay Database" "Stores stay, room, occupancy, and task records." "PostgreSQL" "Database"
            guestdb = container "Guest Database" "Stores guest and deposit records." "PostgreSQL" "Database"
            mediadb = container "Media Database" "Stores contracts, invoices, and guest media." "PostgreSQL" "Database"
            queue = container "Event Queue" "Carries stay events between the application parts." "Kafka"
            tariff = container "Tariff Rules Library" "Computes rates from room type, season, and stay length." "Python"
        }
        payments = element "Payment Gateway" "Charges guest cards for stays and deposits."
        loyaltyFeed = element "Loyalty Points Feed" "Streams loyalty points balances for guests." "REST/JSON" "External"
        legacy = softwareSystem "Legacy Booking System" "The retired booking system being phased out."
        guest -> portal "Books rooms through" "HTTPS"
        guest -> mobile "Books rooms via" "HTTPS"
        portal -> stays "Registers stays in" "gRPC"
        portal -> rate "uses" "HTTP"
        mobile -> rooms "Requests room assignment via" "gRPC"
        stays -> scheduler "Registers nightly tasks in" "gRPC"
        rate -> tariff "Looks up tariffs in" "in-process"
        deposits -> payments "Charges cards through" "REST/JSON"
        housekeeping -> staydb "Stores task records in" "SQL"
        availability -> staydb "Reads room data from" "SQL"
        deposits -> guestdb "Stores deposit records in" "SQL"
        feedback -> mediadb "Stores guest feedback media in" "SQL"
        reporting -> staydb "Reads occupancy records from" "SQL"
        stays -> queue "Publishes stay events to" "Kafka"
        queue -> notifications "Delivers stay events to" "Kafka"
        concierge -> loyaltyFeed "Reads loyalty balances from" "REST/JSON"
    }
    views {
        systemContext planner "GuestContext" "Shows the guest's journey around the system." {
            include *
            autoLayout
        }
        container planner {
            include *
            autoLayout
        }
    }
}
