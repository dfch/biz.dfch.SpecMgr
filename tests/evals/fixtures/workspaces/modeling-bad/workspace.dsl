workspace "Parcel Tracker" "Tracks parcels from dispatch to delivery." {
    model {
        customer = person "Customer" "Looks up the status of their parcels."
        tracker = softwareSystem "Parcel Tracker" "Tracks parcels from dispatch to delivery." {
            portal = container "Web Portal" "Lets customers look up shipments." "Python/FastAPI"
            dispatch = container "Dispatch Service" "Assigns parcels to couriers." "Java"
            pricing = container "Pricing Rules Library" "Computes delivery prices from weight and zone." "Python"
            email = container "Email Delivery Service" "Sends customer notification emails." "SaaS"
            db = container "Shipments Database" "Stores shipments and dispatch records." "PostgreSQL"
        }
        customer -> portal "uses" "HTTPS/JSON"
        portal -> dispatch "requests dispatch status from" "gRPC"
        portal -> db "reads shipment records from" "JDBC"
        dispatch -> db "writes dispatch records to" "JDBC"
        dispatch -> email "connects to" "REST/JSON"
    }
    views {
        systemContext tracker "TrackerContext" {
            include *
            autoLayout
        }
    }
}
