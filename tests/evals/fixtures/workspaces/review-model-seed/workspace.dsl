workspace "Fleet Manager" "Manages a regional car rental fleet." {
    model {
        customer = person "Customer" "Rents vehicles through the fleet manager."
        manager = softwareSystem "Fleet Manager" "Manages bookings, vehicles, contracts, and maintenance." {
            booking = container "Booking Web App" "Lets customers book and return vehicles." "Python"
            mobile = container "Mobile Backend" "Serves the rental mobile app." "Kotlin"
            fleet = container "Fleet Service" "Tracks vehicle availability and locations." "Java"
            dispatch = container "Dispatch Service" "Assigns vehicles to bookings." "Java"
            pricing = container "Pricing Service" "Calculates rental prices." "Go"
            maintenance = container "Maintenance Service" "Plans servicing and repairs." "C#"
            telemetry = container "Telemetry Ingest" "Collects vehicle telemetry events." "Go"
            notifications = container "Notification Service" "Sends booking and reminder messages." "Python"
            contracts = container "Contract Service" "Manages rental contracts and deposits." "Java"
            damage = container "Damage Assessment" "Records and prices vehicle damage." "Python"
            reports = container "Reports Service" "Produces utilisation and revenue reports." "Java"
            search = container "Search Service" "Finds vehicles by location and class." "Go"
            scheduler = container "Batch Scheduler" "Runs the nightly batch jobs." "Java"
            fleetdb = container "Fleet Database" "Stores vehicle, booking, and service records." "PostgreSQL" "Database"
            customerdb = container "Customer Database" "Stores customer and contract records." "PostgreSQL" "Database"
            mediadb = container "Media Database" "Stores contracts, invoices, and photos." "PostgreSQL" "Database"
            queue = container "Event Queue" "Carries booking and telemetry events." "Kafka"
            rates = container "Pricing Rules Library" "Computes rental prices from class, duration, and zone." "Python"
        }
        payments = element "Payment Provider" "Charges customer cards for rentals and deposits."
        telemetryFeed = element "Vehicle Telemetry Feed" "Streams position and status telemetry." "MQTT" "External"
        legacy = softwareSystem "Legacy Billing System" "The retired billing system being phased out."
        customer -> booking "Rents vehicles through" "HTTPS"
        customer -> mobile "Books vehicles via" "HTTPS"
        booking -> fleet "Reserves vehicles in" "gRPC"
        booking -> pricing "uses" "HTTP"
        booking -> queue "Publishes booking events to" "Kafka"
        mobile -> dispatch "Requests dispatch via" "gRPC"
        fleet -> scheduler "Registers nightly tasks in" "gRPC"
        pricing -> rates "Looks up rules in" "in-process"
        contracts -> payments "Charges cards through" "REST/JSON"
        damage -> mediadb "Stores damage photos in" "SQL"
        reports -> fleetdb "Reads booking records from" "SQL"
        maintenance -> fleetdb "Stores service records in" "SQL"
        search -> fleetdb "Reads availability from" "SQL"
        contracts -> customerdb "Stores contract records in" "SQL"
        telemetry -> queue "Publishes telemetry events to" "Kafka"
        queue -> notifications "Delivers booking and telemetry events to" "Kafka"
        telemetry -> telemetryFeed "Receives fleet telemetry from" "MQTT"
    }
    views {
        systemContext manager "CustomerContext" "Shows the customer's journey around the system." {
            include *
            autoLayout
        }
        container manager {
            include *
            autoLayout
        }
    }
}
